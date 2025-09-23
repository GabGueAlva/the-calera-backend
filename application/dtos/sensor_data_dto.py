from datetime import datetime
from pydantic import BaseModel


class SensorDataDTO(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    timestamp: datetime
    device_id: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }