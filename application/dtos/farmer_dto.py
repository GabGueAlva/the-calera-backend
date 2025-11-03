from datetime import datetime
from pydantic import BaseModel


class FarmerDTO(BaseModel):
    """Data Transfer Object for Farmer"""
    first_name: str
    last_name: str
    phone_number: str
    lot_address: str
    registered_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone_number": "+573012592676",
                "lot_address": "Finca La Esperanza, Vereda El Bosque",
                "registered_at": "2025-10-29T17:30:00.123456"
            }
        }
