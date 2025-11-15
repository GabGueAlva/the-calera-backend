from typing import List, Optional

from domain.entities.farmer import Farmer
from domain.repositories.farmer_repository import FarmerRepository
from infrastructure.database.postgres_farmer_database import PostgresFarmerDatabase


class DatabaseFarmerRepository(FarmerRepository):
    """Repository that stores farmers in PostgreSQL (Supabase) database"""

    def __init__(self, database: PostgresFarmerDatabase):
        self.database = database

    async def save_farmer(self, farmer: Farmer) -> None:
        """Save a farmer registration to the database"""
        self.database.save_farmer(farmer)

        # Get total count for logging
        total = self.database.get_farmer_count()
        print(f"[FARMER REPOSITORY] Total registered farmers in database: {total}")

    async def get_all_farmers(self) -> List[Farmer]:
        """Get all registered farmers from the database"""
        farmers = self.database.get_all_farmers()
        print(f"[FARMER REPOSITORY] Retrieved {len(farmers)} farmers from database")
        return farmers

    async def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        """Find a farmer by phone number in the database"""
        farmer = self.database.get_farmer_by_phone(phone_number)
        if farmer:
            print(f"[FARMER REPOSITORY] Found farmer: {farmer.first_name} {farmer.last_name}")
        return farmer

    async def get_all_phone_numbers(self) -> List[str]:
        """Get all registered phone numbers from the database"""
        phone_numbers = self.database.get_all_phone_numbers()
        print(f"[FARMER REPOSITORY] Retrieved {len(phone_numbers)} phone numbers for alerts")
        return phone_numbers

    async def delete_farmer(self, phone_number: str) -> bool:
        """Delete a farmer by phone number from the database"""
        deleted = self.database.delete_farmer(phone_number)
        if deleted:
            print(f"[FARMER REPOSITORY] Successfully deleted farmer with phone: {phone_number}")
        else:
            print(f"[FARMER REPOSITORY] Farmer not found with phone: {phone_number}")
        return deleted
