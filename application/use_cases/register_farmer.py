from datetime import datetime

from domain.entities.farmer import Farmer
from domain.repositories.farmer_repository import FarmerRepository


class RegisterFarmerUseCase:
    """Use case for registering a new farmer"""

    def __init__(self, farmer_repository: FarmerRepository):
        self.farmer_repository = farmer_repository

    async def execute(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        lot_address: str
    ) -> Farmer:
        """
        Register a new farmer or update existing one.

        Args:
            first_name: Farmer's first name
            last_name: Farmer's last name
            phone_number: Farmer's phone number (format: +573012592676)
            lot_address: Farmer's lot/farm address

        Returns:
            The registered Farmer entity
        """
        # Validate phone number format (basic check)
        if not phone_number.startswith('+'):
            raise ValueError("Phone number must start with '+' and include country code")

        # Create farmer entity
        farmer = Farmer(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone_number=phone_number.strip(),
            lot_address=lot_address.strip(),
            registered_at=datetime.utcnow()
        )

        # Save to repository
        await self.farmer_repository.save_farmer(farmer)

        return farmer
