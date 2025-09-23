import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import warnings
warnings.filterwarnings('ignore')

from ...domain.entities.sensor_data import SensorData
from ...domain.services.ml_model_service import MLModelService


class LSTMModelService(MLModelService):
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.sequence_length = 144  # 12 hours of 5-minute intervals
        self.n_features = 3  # temperature, humidity, wind_speed

    def _prepare_data(self, sensor_data: List[SensorData]) -> pd.DataFrame:
        df = pd.DataFrame([
            {
                'timestamp': data.timestamp,
                'temperature': data.temperature,
                'humidity': data.humidity,
                'wind_speed': data.wind_speed
            }
            for data in sensor_data
        ])
        
        df = df.sort_values('timestamp')
        df.set_index('timestamp', inplace=True)
        
        df = df.resample('5T').mean().interpolate()
        
        return df[['temperature', 'humidity', 'wind_speed']]

    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        sequences = []
        targets = []
        
        for i in range(self.sequence_length, len(data)):
            sequences.append(data[i-self.sequence_length:i])
            
            future_temps = data[i:min(i+12, len(data)), 0]  # Next hour temperatures
            frost_prob = 1.0 if np.any(future_temps <= 0) else 0.0
            targets.append(frost_prob)
        
        return np.array(sequences), np.array(targets)

    def _build_model(self) -> keras.Model:
        model = keras.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=(self.sequence_length, self.n_features)),
            layers.Dropout(0.2),
            layers.LSTM(50, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(25),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model

    async def train_model(self, sensor_data: List[SensorData]) -> None:
        if len(sensor_data) < self.sequence_length + 50:
            raise ValueError("Insufficient data for LSTM training")
        
        df = self._prepare_data(sensor_data)
        
        scaled_data = self.scaler.fit_transform(df.values)
        
        X, y = self._create_sequences(scaled_data)
        
        if len(X) < 10:
            raise ValueError("Insufficient sequences for training")
        
        self.model = self._build_model()
        
        try:
            self.model.fit(
                X, y,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0
            )
        except Exception as e:
            print(f"Error training LSTM model: {e}")
            raise

    async def predict_frost_probability(self, sensor_data: List[SensorData]) -> float:
        if not self.model:
            await self.train_model(sensor_data)
        
        try:
            df = self._prepare_data(sensor_data)
            scaled_data = self.scaler.transform(df.values)
            
            if len(scaled_data) < self.sequence_length:
                return 0.5  # Default neutral probability
            
            last_sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, self.n_features)
            
            prediction = self.model.predict(last_sequence, verbose=0)
            probability = float(prediction[0][0])
            
            return np.clip(probability, 0.0, 1.0)
            
        except Exception as e:
            print(f"Error making LSTM prediction: {e}")
            return 0.5  # Default neutral probability