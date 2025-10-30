import numpy as np
import pandas as pd
from typing import List
from statsmodels.tsa.statespace.sarimax import SARIMAX
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

from domain.entities.sensor_data import SensorData
from domain.services.ml_model_service import MLModelService


class SARIMAModelService(MLModelService):
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.is_trained = False  # Track if model is already trained

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

    def _train_model_sync(self, sensor_data: List[SensorData]) -> None:
        """Synchronous training method to run in thread pool"""
        print("\n" + "="*60)
        print("[SARIMA] Preparing temperature data for training...")
        print("="*60)

        if len(sensor_data) < 144:  # At least 1 day of 5-minute intervals
            raise ValueError("Insufficient data for SARIMA training")

        temperature_series = self._prepare_data(sensor_data)
        print(f"[SARIMA] Temperature series prepared: {len(temperature_series)} data points")

        try:
            print(f"[SARIMA] Building SARIMAX model with order=(0,0,1) seasonal=(0,1,2,144)...")
            self.model = SARIMAX(
                temperature_series,
                order=(0, 0, 1),
                seasonal_order=(0, 1, 2, 144),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            print(f"[SARIMA] Model structure created")
            print(f"[SARIMA] Starting model fitting (this will take 20-40 seconds)...")
            print("-"*60)

            self.fitted_model = self.model.fit(disp=False)
            self.is_trained = True

            print("-"*60)
            print("[SARIMA] ✓ Model fitting completed successfully!")
            print("="*60 + "\n")

        except Exception as e:
            print(f"[SARIMA] ✗ Error training model: {e}")
            raise

    async def train_model(self, sensor_data: List[SensorData]) -> None:
        """Async wrapper that runs training in a thread pool"""
        if self.is_trained:
            print("[SARIMA] ⚡ Using cached model (already trained, prediction will be instant)")
            return

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, self._train_model_sync, sensor_data)

    async def predict_frost_probability(self, sensor_data: List[SensorData]) -> float:
        if not self.is_trained:
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