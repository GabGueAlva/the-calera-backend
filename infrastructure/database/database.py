import sqlite3
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager
import os

from domain.entities.sensor_data import SensorData


class SensorDatabase:
    def __init__(self, db_path: str = "data/sensor_data.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()

    def _ensure_db_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Create the sensor_data table if it doesn't exist"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    wind_speed REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Create index on timestamp for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON sensor_data(timestamp)
            """)

            # Create index on device_id for filtering
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_device_id
                ON sensor_data(device_id)
            """)

    def save_sensor_data(self, sensor_data: SensorData) -> None:
        """Save a single sensor data point to the database"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sensor_data
                (id, device_id, temperature, humidity, wind_speed, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(sensor_data.id),
                sensor_data.device_id,
                sensor_data.temperature,
                sensor_data.humidity,
                sensor_data.wind_speed,
                sensor_data.timestamp.isoformat(),
                datetime.utcnow().isoformat()
            ))

    def get_sensor_data_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
        device_id: Optional[str] = None
    ) -> List[SensorData]:
        """
        Retrieve sensor data within a time range

        Args:
            start_time: Start of the time range
            end_time: End of the time range
            device_id: Optional device ID to filter by

        Returns:
            List of SensorData objects
        """
        with self._get_connection() as conn:
            if device_id:
                cursor = conn.execute("""
                    SELECT * FROM sensor_data
                    WHERE timestamp >= ? AND timestamp <= ? AND device_id = ?
                    ORDER BY timestamp ASC
                """, (start_time.isoformat(), end_time.isoformat(), device_id))
            else:
                cursor = conn.execute("""
                    SELECT * FROM sensor_data
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                """, (start_time.isoformat(), end_time.isoformat()))

            rows = cursor.fetchall()

            return [self._row_to_sensor_data(row) for row in rows]

    def get_latest_sensor_data(self, device_id: Optional[str] = None) -> Optional[SensorData]:
        """Get the most recent sensor data point"""
        with self._get_connection() as conn:
            if device_id:
                cursor = conn.execute("""
                    SELECT * FROM sensor_data
                    WHERE device_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (device_id,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM sensor_data
                    ORDER BY timestamp DESC
                    LIMIT 1
                """)

            row = cursor.fetchone()
            return self._row_to_sensor_data(row) if row else None

    def get_data_count(self, device_id: Optional[str] = None) -> int:
        """Get the total count of sensor data points"""
        with self._get_connection() as conn:
            if device_id:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM sensor_data WHERE device_id = ?",
                    (device_id,)
                )
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM sensor_data")

            return cursor.fetchone()[0]

    def _row_to_sensor_data(self, row) -> SensorData:
        """Convert a database row to a SensorData entity"""
        return SensorData(
            temperature=row['temperature'],
            humidity=row['humidity'],
            wind_speed=row['wind_speed'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            device_id=row['device_id']
        )
