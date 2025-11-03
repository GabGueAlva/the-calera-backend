import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import Callback
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')


class EpochProgressCallback(Callback):
    """Custom callback to log epoch progress"""
    def __init__(self, total_epochs):
        super().__init__()
        self.total_epochs = total_epochs

    def on_epoch_begin(self, epoch, logs=None):
        if epoch % 5 == 0:  # Show every 5 epochs to reduce clutter
            print(f"  [LSTM] Epoch {epoch + 1}/{self.total_epochs}...")

    def on_epoch_end(self, epoch, logs=None):
        loss = logs.get('loss', 0)
        val_loss = logs.get('val_loss', 0)
        mae = logs.get('mae', 0)
        val_mae = logs.get('val_mae', 0)

        # Show every 5 epochs or if validation is getting worse
        if epoch % 5 == 0 or epoch == self.total_epochs - 1:
            print(f"  [LSTM] Epoch {epoch + 1}/{self.total_epochs}: "
                  f"Loss={loss:.4f}, Val Loss={val_loss:.4f}, "
                  f"MAE={mae:.4f}, Val MAE={val_mae:.4f}")

from domain.entities.sensor_data import SensorData
from domain.services.ml_model_service import MLModelService


class LSTMModelService(MLModelService):
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.sequence_length = 144  # 12 hours of 5-minute intervals
        self.n_features = 3  # temperature, humidity, wind_speed
        self.is_trained = False  # Track if model is already trained

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

            # Look at next 12 intervals (1 hour ahead)
            future_temps = data[i:min(i+12, len(data)), 0]  # Temperature is column 0

            if len(future_temps) > 0:
                min_temp = np.min(future_temps)

                # Create continuous probability target based on minimum temperature
                # Below 0°C: high probability (0.7-0.9)
                # 0-4°C: medium probability (0.3-0.7)
                # Above 4°C: low probability (0.05-0.3)
                if min_temp <= 0:
                    frost_prob = min(0.9, max(0.7, (2 - min_temp) / 4))
                elif min_temp <= 4:
                    frost_prob = 0.3 + (4 - min_temp) * 0.1  # 0.3 to 0.7
                else:
                    frost_prob = max(0.05, 0.3 - (min_temp - 4) * 0.05)

                targets.append(np.clip(frost_prob, 0.0, 1.0))
            else:
                targets.append(0.5)  # Neutral if no future data

        return np.array(sequences), np.array(targets)

    def _build_model(self) -> keras.Model:
        model = keras.Sequential([
            layers.LSTM(50, return_sequences=True, input_shape=(self.sequence_length, self.n_features),
                       kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.Dropout(0.3),
            layers.LSTM(50, return_sequences=False,
                       kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.Dropout(0.3),
            layers.Dense(25, activation='relu',
                        kernel_regularizer=keras.regularizers.l2(0.001)),
            layers.Dropout(0.2),
            layers.Dense(1, activation='sigmoid')
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',  # Mean Squared Error works better for continuous targets
            metrics=['mae']  # Mean Absolute Error
        )

        return model

    def _train_model_sync(self, sensor_data: List[SensorData]) -> None:
        """Synchronous training method to run in thread pool"""
        print("\n" + "="*60)
        print("[LSTM] Preparing data for training...")
        print("="*60)

        if len(sensor_data) < self.sequence_length + 50:
            raise ValueError("Insufficient data for LSTM training")

        df = self._prepare_data(sensor_data)
        print(f"[LSTM] Data prepared: {len(df)} data points")

        scaled_data = self.scaler.fit_transform(df.values)
        print(f"[LSTM] Data scaled successfully")

        X, y = self._create_sequences(scaled_data)
        print(f"[LSTM] Created {len(X)} sequences for training")

        if len(X) < 10:
            raise ValueError("Insufficient sequences for training")

        self.model = self._build_model()
        print(f"[LSTM] Model architecture built")
        print(f"[LSTM] Starting training with 50 epochs")
        print("-"*60)

        try:
            # Add early stopping to prevent overfitting
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,  # Stop if no improvement for 10 epochs
                restore_best_weights=True,
                verbose=0
            )

            epoch_callback = EpochProgressCallback(total_epochs=50)

            print(f"[LSTM] Target statistics:")
            print(f"[LSTM]   Min target: {y.min():.2f}, Max target: {y.max():.2f}, Mean: {y.mean():.2f}")
            print(f"[LSTM]   High frost targets (>0.6): {(y > 0.6).sum()}/{len(y)}")

            self.model.fit(
                X, y,
                epochs=50, 
                batch_size=32,
                validation_split=0.2,
                callbacks=[epoch_callback, early_stopping],
                verbose=0
            )
            self.is_trained = True
            print("-"*60)
            print("[LSTM] ✓ Training completed successfully!")
            print(f"[LSTM] Training stopped at epoch {len(self.model.history.history['loss'])}")
            print("="*60 + "\n")
        except Exception as e:
            print(f"[LSTM] ✗ Error training model: {e}")
            raise

    async def train_model(self, sensor_data: List[SensorData]) -> None:
        """Async wrapper that runs training in a thread pool"""
        if self.is_trained:
            print("[LSTM] ⚡ Using cached model (already trained, prediction will be instant)")
            return

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, self._train_model_sync, sensor_data)

    async def predict_frost_probability(self, sensor_data: List[SensorData]) -> float:
        if not self.is_trained:
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