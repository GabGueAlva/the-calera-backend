from fastapi import APIRouter, HTTPException, Body
from typing import List
from pydantic import BaseModel

from application.services.farmer_service import FarmerService
from application.dtos.farmer_dto import FarmerDTO


class RegisterFarmerRequest(BaseModel):
    """Request model for registering a farmer"""
    first_name: str
    last_name: str
    phone_number: str
    lot_address: str

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone_number": "+573012592676",
                "lot_address": "Finca La Esperanza, Vereda El Bosque"
            }
        }


class FarmerController:
    """Controller for farmer-related endpoints"""

    def __init__(self, farmer_service: FarmerService):
        self.farmer_service = farmer_service
        self.router = APIRouter()

        # Register routes
        self.router.add_api_route(
            "/farmers/register",
            self.register_farmer,
            methods=["POST"],
            response_model=FarmerDTO
        )
        self.router.add_api_route(
            "/farmers",
            self.get_all_farmers,
            methods=["GET"],
            response_model=List[FarmerDTO]
        )

    async def register_farmer(self, request: RegisterFarmerRequest = Body(...)) -> FarmerDTO:
        """
        Register a new farmer for frost alerts.

        This endpoint allows farmers to register their information to receive
        automatic frost alerts at 5pm daily.
        """
        try:
            farmer = await self.farmer_service.register_farmer(
                first_name=request.first_name,
                last_name=request.last_name,
                phone_number=request.phone_number,
                lot_address=request.lot_address
            )
            return farmer
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"Error registering farmer: {e}")
            raise HTTPException(status_code=500, detail="Failed to register farmer")

    async def get_all_farmers(self) -> List[FarmerDTO]:
        """
        Get all registered farmers.

        Returns a list of all farmers registered in the system.
        """
        try:
            farmers = await self.farmer_service.get_all_farmers()
            return farmers
        except Exception as e:
            print(f"Error retrieving farmers: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve farmers")
