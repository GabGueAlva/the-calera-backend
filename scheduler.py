from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

from application.services.prediction_service import PredictionService
from application.services.sensor_data_service import SensorDataService


class FrostPredictionScheduler:
    def __init__(self, prediction_service: PredictionService, sensor_data_service: SensorDataService = None):
        self.prediction_service = prediction_service
        self.sensor_data_service = sensor_data_service
        self.scheduler = AsyncIOScheduler()

    async def run_prediction_job(self):
        try:
            print(f"\n{'='*60}")
            print(f"⏰ Running prediction job at {datetime.now()}")
            print(f"{'='*60}\n")

            # Prediction can take up to 10 minutes, so we wait patiently
            prediction = await self.prediction_service.generate_prediction()

            print(f"\n{'='*60}")
            print(f"✅ Prediction completed successfully!")
            print(f"   Frost probability: {prediction.probability:.2%}")
            print(f"   Frost level: {prediction.frost_level.value}")
            print(f"   Completed at: {datetime.now()}")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ Error in prediction job: {e}")
            print(f"{'='*60}\n")
            import traceback
            traceback.print_exc()

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
        # TEST: Run prediction in 2 minutes from now (one-time job)
        run_time = datetime.now() + timedelta(minutes=2)
        self.scheduler.add_job(
            self.run_prediction_job,
            DateTrigger(run_date=run_time),
            id="prediction_test_immediate",
            misfire_grace_time=600
        )
        print(f"🧪 TEST: One-time prediction scheduled for {run_time.strftime('%H:%M:%S')}")

        # Schedule prediction jobs at 3:00 AM, 10:00 AM, 12:00 PM, and 4:00 PM
        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=3, minute=0),
            id="prediction_3am",
            misfire_grace_time=30,  # Allow 30 seconds delay
            coalesce=True  # Combine missed executions
        )

        # TEST: Prediction at 10:25 AM
        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=10, minute=25),
            id="prediction_10am",
            misfire_grace_time=600,  # Allow up to 10 minutes delay (for long-running predictions)
            coalesce=True
        )

        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=12, minute=0),
            id="prediction_12pm",
            misfire_grace_time=600,  # Allow up to 10 minutes delay
            coalesce=True
        )

        self.scheduler.add_job(
            self.run_prediction_job,
            CronTrigger(hour=16, minute=0),
            id="prediction_4pm",
            misfire_grace_time=600,  # Allow up to 10 minutes delay
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

        self.scheduler.start()

        print("\n" + "="*70)
        print("⏰ SCHEDULER STARTED SUCCESSFULLY")
        print("="*70)
        print("📅 Prediction Jobs:")
        print("   • 03:00 AM - Morning prediction")
        print("   • 10:25 AM - TEST prediction (can take up to 10 minutes)")
        print("   • 12:00 PM - Midday prediction")
        print("   • 04:00 PM - Afternoon prediction")
        print("\n📱 Alert Job:")
        print("   • 05:00 PM - Daily WhatsApp alert")
        if self.sensor_data_service:
            print("\n🌡️  Sensor Data Updates:")
            print("   • Every 5 minutes - Fetch latest sensor data from TTS")
        print("="*70 + "\n")

    def stop(self):
        self.scheduler.shutdown()
        print("Scheduler stopped")