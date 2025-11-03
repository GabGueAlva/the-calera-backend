from typing import List

from domain.entities.farmer import Farmer
from domain.repositories.farmer_repository import FarmerRepository


class GetAllFarmersUseCase:
    """Use case for retrieving all registered farmers"""

    def __init__(self, farmer_repository: FarmerRepository):
        self.farmer_repository = farmer_repository

    async def execute(self) -> List[Farmer]:
        """
        Get all registered farmers.

        Returns:
            List of all registered farmers
        """
        return await self.farmer_repository.get_all_farmers()
