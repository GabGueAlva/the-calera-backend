from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class SensorData:
    def __init__(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        timestamp: datetime,
        device_id: str,
        id: Optional[UUID] = None,
    ):
        self.id = id or uuid4()
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.timestamp = timestamp
        self.device_id = device_id

    def __eq__(self, other) -> bool:
        if not isinstance(other, SensorData):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)