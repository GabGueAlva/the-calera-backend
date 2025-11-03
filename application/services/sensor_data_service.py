from datetime import datetime, timedelta
from typing import Optional

from domain.repositories.sensor_data_repository import SensorDataRepository
from domain.value_objects.time_range import TimeRange
from application.dtos.sensor_data_dto import SensorDataDTO, LatestSensorDataResponse


class SensorDataService:
    """Service for managing and caching latest sensor data"""

    def __init__(self, sensor_data_repository: SensorDataRepository):
        self.sensor_data_repository = sensor_data_repository
        self._cached_sensor_data: Optional[SensorDataDTO] = None
        self._last_updated: Optional[datetime] = None

    async def update_cached_sensor_data(self) -> None:
        """
        Fetch latest sensor data from TTS and cache it.
        This is called periodically by the background job.
        """
        try:
            print("[SENSOR SERVICE] Fetching latest sensor data from TTS...")

            # Fetch sensor data from the past hour (for latest reading)
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)
            time_range = TimeRange(start=one_hour_ago, end=now)

            sensor_readings = await self.sensor_data_repository.get_sensor_data_in_range(time_range)

            if not sensor_readings or len(sensor_readings) == 0:
                print("[SENSOR SERVICE] No sensor data available")
                return

            # Get the most recent reading
            latest_reading = sensor_readings[-1]

            # Cache the latest sensor data
            self._cached_sensor_data = SensorDataDTO(
                temperature=latest_reading.temperature,
                humidity=latest_reading.humidity,
                wind_speed=latest_reading.wind_speed,
                timestamp=latest_reading.timestamp,
                device_id="tts-sensor-calera"
            )
            self._last_updated = datetime.utcnow()

            print(f"[SENSOR SERVICE] Cached latest reading: {latest_reading.temperature}C, {latest_reading.humidity}% humidity, {latest_reading.wind_speed} m/s wind")

        except Exception as e:
            print(f"[SENSOR SERVICE] Error updating sensor data: {e}")

    async def get_latest_sensor_data(self) -> LatestSensorDataResponse:
        """
        Get the cached latest sensor data.
        Returns the most recent cached reading.
        """
        if self._cached_sensor_data is None:
            # If no cached data, fetch it now
            print("[SENSOR SERVICE] No cached data, fetching now...")
            await self.update_cached_sensor_data()

        if self._cached_sensor_data is None:
            # If still no data after fetching, TTS/Mock might have an issue
            # Return last known state or error
            raise ValueError("No sensor data available. TTS may not be responding.")

        return LatestSensorDataResponse(
            status="success",
            data=self._cached_sensor_data,
            last_updated=self._last_updated or datetime.utcnow()
        )
