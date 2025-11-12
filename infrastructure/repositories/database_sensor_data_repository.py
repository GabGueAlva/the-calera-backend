from typing import List

from domain.entities.sensor_data import SensorData
from domain.repositories.sensor_data_repository import SensorDataRepository
from domain.value_objects.time_range import TimeRange
from infrastructure.database.postgres_database import PostgresSensorDatabase


class DatabaseSensorDataRepository(SensorDataRepository):
    """Repository that stores and retrieves sensor data from PostgreSQL database"""

    def __init__(self, database: PostgresSensorDatabase):
        self.database = database

    async def get_sensor_data_in_range(self, time_range: TimeRange) -> List[SensorData]:
        """
        Retrieve sensor data from database within the specified time range

        Args:
            time_range: Time range to query

        Returns:
            List of SensorData objects from all configured nodes (1, 6, and 7)
        """
        # Get data from all nodes instead of filtering for just node 7
        return self.database.get_sensor_data_in_range(
            start_time=time_range.start,
            end_time=time_range.end,
            device_id=None  # Get data from all nodes
        )

    def save_sensor_data(self, sensor_data: SensorData) -> None:
        """
        Save sensor data to the database

        Args:
            sensor_data: SensorData object to save
        """
        self.database.save_sensor_data(sensor_data)
