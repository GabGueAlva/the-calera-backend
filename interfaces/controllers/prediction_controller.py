from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from ...application.services.prediction_service import PredictionService
from ...application.dtos.prediction_dto import PredictionDTO


class PredictionController:
    def __init__(self, prediction_service: PredictionService):
        self.prediction_service = prediction_service
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
            methods=["POST"]
        )

    async def generate_prediction(self) -> PredictionDTO:
        try:
            prediction = await self.prediction_service.generate_prediction()
            return prediction
        except Exception as e:
            print(f"Error generating prediction: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate prediction")

    async def send_alert(self) -> dict:
        try:
            await self.prediction_service.send_daily_alert()
            return {"status": "success", "message": "Alert sent successfully"}
        except Exception as e:
            print(f"Error sending alert: {e}")
            raise HTTPException(status_code=500, detail="Failed to send alert")