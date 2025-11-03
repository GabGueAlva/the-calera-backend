from typing import List

from application.use_cases.register_farmer import RegisterFarmerUseCase
from application.use_cases.get_all_farmers import GetAllFarmersUseCase
from application.dtos.farmer_dto import FarmerDTO


class FarmerService:
    """Application service for farmer operations"""

    def __init__(
        self,
        register_farmer_use_case: RegisterFarmerUseCase,
        get_all_farmers_use_case: GetAllFarmersUseCase
    ):
        self.register_farmer_use_case = register_farmer_use_case
        self.get_all_farmers_use_case = get_all_farmers_use_case

    async def register_farmer(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        lot_address: str
    ) -> FarmerDTO:
        """Register a new farmer"""
        farmer = await self.register_farmer_use_case.execute(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            lot_address=lot_address
        )

        return FarmerDTO(
            first_name=farmer.first_name,
            last_name=farmer.last_name,
            phone_number=farmer.phone_number,
            lot_address=farmer.lot_address,
            registered_at=farmer.registered_at
        )

    async def get_all_farmers(self) -> List[FarmerDTO]:
        """Get all registered farmers"""
        farmers = await self.get_all_farmers_use_case.execute()

        return [
            FarmerDTO(
                first_name=farmer.first_name,
                last_name=farmer.last_name,
                phone_number=farmer.phone_number,
                lot_address=farmer.lot_address,
                registered_at=farmer.registered_at
            )
            for farmer in farmers
        ]
