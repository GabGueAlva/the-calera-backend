from datetime import datetime
from typing import Optional

from domain.repositories.sensor_data_repository import SensorDataRepository
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

            # Fetch sensor data from the past 5 minutes (for latest reading)
            sensor_readings = await self.sensor_data_repository.get_sensor_data(
                hours=1  # Get last hour of data
            )

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

