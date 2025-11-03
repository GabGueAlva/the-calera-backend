from typing import List, Optional

from domain.repositories.prediction_repository import PredictionRepository
from domain.repositories.farmer_repository import FarmerRepository
from domain.services.notification_service import NotificationService
from domain.entities.prediction import Prediction


class SendFrostAlertUseCase:
    def __init__(
        self,
        prediction_repository: PredictionRepository,
        notification_service: NotificationService,
        farmer_repository: Optional[FarmerRepository] = None,
    ):
        self.prediction_repository = prediction_repository
        self.notification_service = notification_service
        self.farmer_repository = farmer_repository

    async def execute(self, phone_numbers: List[str]) -> None:
        """
        Send frost alert based on the daily average of all predictions made today.
        This should be called after all scheduled predictions are complete (e.g., after 4pm).

        Args:
            phone_numbers: List of phone numbers to send the alert to (e.g., ["+573012592676"])
        """
        print("\n" + "📱 " + "="*56 + " 📱")
        print("     SENDING FROST ALERT (DAILY AVERAGE)")
        print("📱 " + "="*56 + " 📱\n")

        # Get all predictions made today
        print("[ALERT] Step 1: Retrieving today's predictions...")
        todays_predictions = await self.prediction_repository.get_todays_predictions()

        if not todays_predictions:
            raise ValueError("No predictions available for today to send alert")

        print(f"[ALERT] ✓ Found {len(todays_predictions)} predictions today\n")

        # Calculate average probability from all daily predictions
        print("[ALERT] Step 2: Calculating daily average...")
        avg_probability = await self.prediction_repository.calculate_daily_average_probability()

        if avg_probability is None:
            raise ValueError("Could not calculate daily average probability")

        print(f"[ALERT] ✓ Daily average probability: {avg_probability:.2%}\n")

        # Use the latest prediction as template and update with average probability
        latest_prediction = todays_predictions[-1]

        # Create a new prediction object with averaged probability
        averaged_prediction = Prediction(
            probability=avg_probability,
            frost_level=Prediction.determine_frost_level(avg_probability),
            model_type=latest_prediction.model_type,
            created_at=latest_prediction.created_at,
            sarima_probability=latest_prediction.sarima_probability,
            lstm_probability=latest_prediction.lstm_probability,
        )

        print(f"[ALERT] Step 3: Sending WhatsApp notifications to {len(phone_numbers)} recipient(s)...")
        print(f"[ALERT] Frost Level: {averaged_prediction.frost_level.value}")

        # Send to all phone numbers with personalized names if available
        for phone_number in phone_numbers:
            # Try to get farmer name from repository
            farmer_name = None
            if self.farmer_repository:
                farmer = await self.farmer_repository.get_farmer_by_phone(phone_number)
                if farmer:
                    farmer_name = f"{farmer.first_name} {farmer.last_name}"
                    print(f"[ALERT] Sending to {phone_number} ({farmer_name})...")
                else:
                    print(f"[ALERT] Sending to {phone_number} (no registration found)...")
            else:
                print(f"[ALERT] Sending to {phone_number}...")

            await self.notification_service.send_frost_alert(averaged_prediction, phone_number, farmer_name)

        print(f"[ALERT] ✓ Alerts sent successfully to {len(phone_numbers)} recipient(s)!")
        print("="*60 + "\n")