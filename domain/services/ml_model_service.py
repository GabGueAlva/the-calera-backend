from abc import ABC, abstractmethod
from typing import List

from ..entities.sensor_data import SensorData


class MLModelService(ABC):
    @abstractmethod
    async def predict_frost_probability(self, sensor_data: List[SensorData]) -> float:
        pass

    @abstractmethod
    async def train_model(self, sensor_data: List[SensorData]) -> None:
        pass