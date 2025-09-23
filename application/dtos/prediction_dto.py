from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from ...domain.entities.prediction import FrostLevel, PredictionModel


class PredictionDTO(BaseModel):
    probability: float
    frost_level: FrostLevel
    model_type: PredictionModel
    created_at: datetime
    sarima_probability: Optional[float] = None
    lstm_probability: Optional[float] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }