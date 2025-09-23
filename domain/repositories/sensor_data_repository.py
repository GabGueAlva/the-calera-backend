from abc import ABC, abstractmethod
from typing import List

from ..entities.sensor_data import SensorData
from ..value_objects.time_range import TimeRange


class SensorDataRepository(ABC):
    @abstractmethod
    async def get_sensor_data_in_range(self, time_range: TimeRange) -> List[SensorData]:
        pass