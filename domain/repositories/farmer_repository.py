from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.farmer import Farmer


class FarmerRepository(ABC):
    """Abstract repository for farmer persistence"""

    @abstractmethod
    async def save_farmer(self, farmer: Farmer) -> None:
        """Save a farmer registration"""
        pass

    @abstractmethod
    async def get_all_farmers(self) -> List[Farmer]:
        """Get all registered farmers"""
        pass

    @abstractmethod
    async def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        """Find a farmer by phone number"""
        pass

    @abstractmethod
    async def get_all_phone_numbers(self) -> List[str]:
        """Get all registered phone numbers"""
        pass

    @abstractmethod
    async def delete_farmer(self, phone_number: str) -> bool:
        """Delete a farmer by phone number"""
        pass
