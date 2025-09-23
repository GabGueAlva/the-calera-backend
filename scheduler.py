from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio

from application.services.prediction_service import PredictionService
from infrastructure.config.settings import settings


class FrostPredictionScheduler:
    def __init__(self, prediction_service: PredictionService):
        self.prediction_service = prediction_service
        self.scheduler = AsyncIOScheduler()

    async def run_prediction_job(self):
        try:
            print(f"Running prediction job at {datetime.now()}")
            prediction = await self.prediction_service.generate_prediction()
            print(f"Prediction generated: {prediction.probability:.2%} frost probability")
        except Exception as e:
            print(f"Error in prediction job: {e}")

    async def send_daily_alert_job(self):
        try:
            print(f"Sending daily alert at {datetime.now()}")
            await self.prediction_service.send_daily_alert()
            print("Daily alert sent successfully")
        except Exception as e:
            print(f"Error sending daily alert: {e}")

    def start(self):
        # Schedule prediction jobs at 3:00 AM, 12:00 PM, and 4:00 PM
        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=3, minute=0),
            id="prediction_3am"
        )
        
        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=12, minute=0),
            id="prediction_12pm"
        )
        
        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=16, minute=0),
            id="prediction_4pm"
        )
        
        # Schedule daily alert at 5:00 PM
        self.scheduler.add_job(
            self.send_daily_alert_job,
            CronTrigger(hour=17, minute=0),
            id="daily_alert_5pm"
        )
        
        self.scheduler.start()
        print("Scheduler started successfully")

    def stop(self):
        self.scheduler.shutdown()
        print("Scheduler stopped")