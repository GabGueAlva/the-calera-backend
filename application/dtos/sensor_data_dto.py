from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SensorDataDTO(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    timestamp: datetime
    device_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LatestSensorDataResponse(BaseModel):
    """Response model for latest sensor data endpoint"""
    status: str
    data: SensorDataDTO
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "temperature": 12.5,
                    "humidity": 78.3,
                    "wind_speed": 3.2,
                    "timestamp": "2025-10-29T17:30:00",
                    "device_id": "tts-sensor-01"
                },
                "last_updated": "2025-10-29T17:30:00"
            }
        }


class AllSensorDataResponse(BaseModel):
    """Response model for all sensor data endpoint"""
    status: str
    data: List[SensorDataDTO]
    total_records: int

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": [
                    {
                        "temperature": 12.5,
                        "humidity": 78.3,
                        "wind_speed": 3.2,
                        "timestamp": "2025-10-29T17:30:00",
                        "device_id": "tts-sensor-01"
                    }
                ],
                "total_records": 1
            }
        }