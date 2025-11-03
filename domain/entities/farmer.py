from dataclasses import dataclass
from datetime import datetime


@dataclass
class Farmer:
    """Entity representing a registered farmer"""
    first_name: str
    last_name: str
    phone_number: str  # Format: +573012592676
    lot_address: str
    registered_at: datetime

    def to_dict(self) -> dict:
        """Convert farmer to dictionary for JSON serialization"""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "lot_address": self.lot_address,
            "registered_at": self.registered_at.isoformat()
        }

    @staticmethod
    def from_dict(data: dict) -> 'Farmer':
        """Create farmer from dictionary"""
        return Farmer(
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data["phone_number"],
            lot_address=data["lot_address"],
            registered_at=datetime.fromisoformat(data["registered_at"])
        )
