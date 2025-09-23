import numpy as np
import pandas as pd
from typing import List
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings('ignore')

from ...domain.entities.sensor_data import SensorData
from ...domain.services.ml_model_service import MLModelService


class SARIMAModelService(MLModelService):
    def __init__(self):
        self.model = None
        self.fitted_model = None

    def _prepare_data(self, sensor_data: List[SensorData]) -> pd.Series:
        df = pd.DataFrame([
            {
                'timestamp': data.timestamp,
                'temperature': data.temperature
            }
            for data in sensor_data
        ])
        
        df = df.sort_values('timestamp')
        df.set_index('timestamp', inplace=True)
        
        df = df.resample('5T').mean().interpolate()
        
        return df['temperature']

    async def train_model(self, sensor_data: List[SensorData]) -> None:
        if len(sensor_data) < 288:  # At least 1 day of 5-minute intervals
            raise ValueError("Insufficient data for SARIMA training")
        
        temperature_series = self._prepare_data(sensor_data)
        
        try:
            self.model = SARIMAX(
                temperature_series,
                order=(0, 0, 1),
                seasonal_order=(0, 1, 2, 288),  # 288 = 24 hours * 12 (5-minute intervals)
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            self.fitted_model = self.model.fit(disp=False)
            
        except Exception as e:
            print(f"Error training SARIMA model: {e}")
            raise

    async def predict_frost_probability(self, sensor_data: List[SensorData]) -> float:
        if not self.fitted_model:
            await self.train_model(sensor_data)
        
        try:
            forecast = self.fitted_model.forecast(steps=12)  # Next 12 intervals (1 hour)
            
            min_forecast_temp = forecast.min()
            
            if min_forecast_temp <= 0:  # Freezing point
                probability = min(0.9, max(0.1, (2 - min_forecast_temp) / 4))
            else:
                probability = max(0.05, (4 - min_forecast_temp) / 8)
            
            return float(np.clip(probability, 0.0, 1.0))
            
        except Exception as e:
            print(f"Error making SARIMA prediction: {e}")
            return 0.5  # Default neutral probability