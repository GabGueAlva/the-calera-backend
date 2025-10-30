import json
import os
from typing import List, Optional

from domain.entities.farmer import Farmer
from domain.repositories.farmer_repository import FarmerRepository


class JSONFarmerRepository(FarmerRepository):
    """Repository that stores farmers in a JSON file"""

    def __init__(self, file_path: str = "data/farmers.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the data directory and file if they don't exist"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
            print(f"[FARMER REPOSITORY] Created farmers database at {self.file_path}")

    def _load_farmers(self) -> List[dict]:
        """Load farmers from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_farmers(self, farmers_data: List[dict]) -> None:
        """Save farmers to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(farmers_data, f, indent=2)

    async def save_farmer(self, farmer: Farmer) -> None:
        """Save a farmer registration"""
        farmers_data = self._load_farmers()

        # Check if farmer already exists (by phone number)
        existing_index = None
        for i, existing in enumerate(farmers_data):
            if existing["phone_number"] == farmer.phone_number:
                existing_index = i
                break

        if existing_index is not None:
            # Update existing farmer
            farmers_data[existing_index] = farmer.to_dict()
            print(f"[FARMER REPOSITORY] Updated farmer: {farmer.first_name} {farmer.last_name} ({farmer.phone_number})")
        else:
            # Add new farmer
            farmers_data.append(farmer.to_dict())
            print(f"[FARMER REPOSITORY] Registered new farmer: {farmer.first_name} {farmer.last_name} ({farmer.phone_number})")

        self._save_farmers(farmers_data)
        print(f"[FARMER REPOSITORY] Total registered farmers: {len(farmers_data)}")

    async def get_all_farmers(self) -> List[Farmer]:
        """Get all registered farmers"""
        farmers_data = self._load_farmers()
        return [Farmer.from_dict(data) for data in farmers_data]

    async def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        """Find a farmer by phone number"""
        farmers_data = self._load_farmers()
        for data in farmers_data:
            if data["phone_number"] == phone_number:
                return Farmer.from_dict(data)
        return None

    async def get_all_phone_numbers(self) -> List[str]:
        """Get all registered phone numbers"""
        farmers_data = self._load_farmers()
        phone_numbers = [data["phone_number"] for data in farmers_data]
        print(f"[FARMER REPOSITORY] Retrieved {len(phone_numbers)} phone numbers for alerts")
        return phone_numbers

    async def delete_farmer(self, phone_number: str) -> bool:
        """Delete a farmer by phone number"""
        farmers_data = self._load_farmers()
        original_count = len(farmers_data)

        farmers_data = [f for f in farmers_data if f["phone_number"] != phone_number]

        if len(farmers_data) < original_count:
            self._save_farmers(farmers_data)
            print(f"[FARMER REPOSITORY] Deleted farmer with phone: {phone_number}")
            return True

        return False
