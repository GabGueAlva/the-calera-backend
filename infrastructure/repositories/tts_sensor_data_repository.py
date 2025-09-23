from typing import List

from ...domain.entities.sensor_data import SensorData
from ...domain.repositories.sensor_data_repository import SensorDataRepository
from ...domain.value_objects.time_range import TimeRange
from ..external.tts_client import TTSClient


class TTSSensorDataRepository(SensorDataRepository):
    def __init__(self, tts_client: TTSClient):
        self.tts_client = tts_client

    async def get_sensor_data_in_range(self, time_range: TimeRange) -> List[SensorData]:
        return await self.tts_client.get_sensor_data_in_range(time_range)