from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List
from pydantic import BaseModel

from application.services.prediction_service import PredictionService
from application.services.sensor_data_service import SensorDataService
from application.dtos.prediction_dto import PredictionDTO
from application.dtos.sensor_data_dto import LatestSensorDataResponse


# Removed SendAlertRequest - endpoint no longer accepts phone numbers from frontend


class PredictionController:
    def __init__(self, prediction_service: PredictionService, sensor_data_service: SensorDataService = None, farmer_repository=None):
        self.prediction_service = prediction_service
        self.sensor_data_service = sensor_data_service
        self.farmer_repository = farmer_repository  # Injected for getting registered farmers
        self.router = APIRouter()
        self.router.add_api_route(
            "/predict",
            self.generate_prediction,
            methods=["POST"],
            response_model=PredictionDTO
        )
        self.router.add_api_route(
            "/send-alert",
            self.send_alert,
            methods=["POST"],
            status_code=200
        )
        self.router.add_api_route(
            "/sensor-data",
            self.get_sensor_data,
            methods=["GET"],
            response_model=LatestSensorDataResponse
        )

    async def generate_prediction(self) -> PredictionDTO:
        try:
            prediction = await self.prediction_service.generate_prediction()
            return prediction
        except Exception as e:
            print(f"Error generating prediction: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate prediction")

    async def send_alert(self) -> dict:
        """
        Send frost alert to all registered farmers.

        This endpoint automatically sends alerts to all farmers registered in the system.
        No input required - phone numbers are retrieved from the farmer database.
        """
        try:
            # Check if farmer repository is configured
            if self.farmer_repository is None:
                raise HTTPException(
                    status_code=500,
                    detail="Farmer repository not configured"
                )

            # Get all registered phone numbers
            phone_numbers = await self.farmer_repository.get_all_phone_numbers()

            if not phone_numbers or len(phone_numbers) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No farmers registered. Please register farmers first using /api/v1/farmers/register"
                )

            print(f"[ALERT] Sending to all {len(phone_numbers)} registered farmers")

            # Send alerts with personalized names
            await self.prediction_service.send_daily_alert(phone_numbers)

            return {
                "status": "success",
                "message": f"Alert sent successfully to {len(phone_numbers)} registered farmer(s)",
                "recipients_count": len(phone_numbers)
            }
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error sending alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_sensor_data(self) -> LatestSensorDataResponse:
        """
        Get the latest sensor data (temperature, humidity, wind speed).

        This endpoint returns cached sensor data that is updated periodically
        by a background job. No parameters required.
        """
        try:
            if self.sensor_data_service is None:
                raise HTTPException(
                    status_code=500,
                    detail="Sensor data service not configured"
                )

            return await self.sensor_data_service.get_latest_sensor_data()

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            print(f"Error retrieving sensor data: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve sensor data")