from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio

from application.services.prediction_service import PredictionService
from application.services.sensor_data_service import SensorDataService
from infrastructure.config.settings import settings


class FrostPredictionScheduler:
    def __init__(self, prediction_service: PredictionService, sensor_data_service: SensorDataService = None):
        self.prediction_service = prediction_service
        self.sensor_data_service = sensor_data_service
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

    async def update_sensor_data_job(self):
        """Update cached sensor data from TTS"""
        try:
            if self.sensor_data_service:
                await self.sensor_data_service.update_cached_sensor_data()
        except Exception as e:
            print(f"Error updating sensor data: {e}")

    def start(self):
        # Schedule prediction jobs at 3:00 AM, 12:00 PM, and 4:00 PM
        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=3, minute=0),
            id="prediction_3am",
            misfire_grace_time=30,  # Allow 30 seconds delay
            coalesce=True  # Combine missed executions
        )

        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=12, minute=0),
            id="prediction_12pm",
            misfire_grace_time=30,
            coalesce=True
        )

        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=16, minute=0),
            id="prediction_4pm",
            misfire_grace_time=30,
            coalesce=True
        )

        # Schedule daily alert at 5:00 PM
        self.scheduler.add_job(
            self.send_daily_alert_job,
            CronTrigger(hour=17, minute=0),
            id="daily_alert_5pm",
            misfire_grace_time=30,
            coalesce=True
        )

        # Schedule sensor data updates every 5 minutes
        if self.sensor_data_service:
            self.scheduler.add_job(
                self.update_sensor_data_job,
                CronTrigger(minute="*/5"),  # Every 5 minutes
                id="sensor_data_update",
                misfire_grace_time=60,  # Allow up to 60 seconds delay for sensor updates
                coalesce=True  # If multiple executions are missed, only run once
            )
            print("Sensor data updates scheduled every 5 minutes")

        self.scheduler.start()
        print("Scheduler started successfully")

    def stop(self):
        self.scheduler.shutdown()
        print("Scheduler stopped")