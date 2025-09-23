from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class FrostLevel(Enum):
    NO_FROST = "no_frost"
    POSSIBLE_FROST = "possible_frost"
    FROST_EXPECTED = "frost_expected"


class PredictionModel(Enum):
    SARIMA = "sarima"
    LSTM = "lstm"
    HYBRID = "hybrid"


class Prediction:
    def __init__(
        self,
        probability: float,
        frost_level: FrostLevel,
        model_type: PredictionModel,
        created_at: datetime,
        sarima_probability: Optional[float] = None,
        lstm_probability: Optional[float] = None,
        id: Optional[UUID] = None,
    ):
        self.id = id or uuid4()
        self.probability = probability
        self.frost_level = frost_level
        self.model_type = model_type
        self.created_at = created_at
        self.sarima_probability = sarima_probability
        self.lstm_probability = lstm_probability

    @classmethod
    def determine_frost_level(cls, probability: float) -> FrostLevel:
        if probability > 0.70:
            return FrostLevel.FROST_EXPECTED
        elif probability < 0.30:
            return FrostLevel.NO_FROST
        else:
            return FrostLevel.POSSIBLE_FROST

    def __eq__(self, other) -> bool:
        if not isinstance(other, Prediction):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)