import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

from domain.entities.sensor_data import SensorData


class PostgresSensorDatabase:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._initialized = False

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(self.database_url)
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
        if self._initialized:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS sensor_data (
                            id TEXT PRIMARY KEY,
                            device_id TEXT NOT NULL,
                            temperature REAL NOT NULL,
                            humidity REAL NOT NULL,
                            wind_speed REAL NOT NULL,
                            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL
                        )
                    """)

                    # Create index on timestamp for faster queries
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_timestamp
                        ON sensor_data(timestamp)
                    """)

                    # Create index on device_id for filtering
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_device_id
                        ON sensor_data(device_id)
                    """)

                    self._initialized = True
                    print("[DATABASE] PostgreSQL tables initialized successfully")
        except Exception as e:
            print(f"[DATABASE] Warning: Could not initialize database: {e}")
            print("[DATABASE] Will retry on first database operation")

    def save_sensor_data(self, sensor_data: SensorData) -> None:
        """Save a single sensor data point to the database"""
        self._initialize_database()  # Ensure DB is initialized
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sensor_data
                    (id, device_id, temperature, humidity, wind_speed, timestamp, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        humidity = EXCLUDED.humidity,
                        wind_speed = EXCLUDED.wind_speed,
                        timestamp = EXCLUDED.timestamp
                """, (
                    str(sensor_data.id),
                    sensor_data.device_id,
                    sensor_data.temperature,
                    sensor_data.humidity,
                    sensor_data.wind_speed,
                    sensor_data.timestamp,
                    datetime.utcnow()
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
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if device_id:
                    cursor.execute("""
                        SELECT * FROM sensor_data
                        WHERE timestamp >= %s AND timestamp <= %s AND device_id = %s
                        ORDER BY timestamp ASC
                    """, (start_time, end_time, device_id))
                else:
                    cursor.execute("""
                        SELECT * FROM sensor_data
                        WHERE timestamp >= %s AND timestamp <= %s
                        ORDER BY timestamp ASC
                    """, (start_time, end_time))

                rows = cursor.fetchall()
                return [self._row_to_sensor_data(dict(row)) for row in rows]

    def get_latest_sensor_data(self, device_id: Optional[str] = None) -> Optional[SensorData]:
        """Get the most recent sensor data point"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if device_id:
                    cursor.execute("""
                        SELECT * FROM sensor_data
                        WHERE device_id = %s
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """, (device_id,))
                else:
                    cursor.execute("""
                        SELECT * FROM sensor_data
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """)

                row = cursor.fetchone()
                return self._row_to_sensor_data(dict(row)) if row else None

    def get_data_count(self, device_id: Optional[str] = None) -> int:
        """Get the total count of sensor data points"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                if device_id:
                    cursor.execute(
                        "SELECT COUNT(*) FROM sensor_data WHERE device_id = %s",
                        (device_id,)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) FROM sensor_data")

                return cursor.fetchone()[0]

    def _row_to_sensor_data(self, row) -> SensorData:
        """Convert a database row to a SensorData entity"""
        return SensorData(
            temperature=row['temperature'],
            humidity=row['humidity'],
            wind_speed=row['wind_speed'],
            timestamp=row['timestamp'] if isinstance(row['timestamp'], datetime) else datetime.fromisoformat(str(row['timestamp'])),
            device_id=row['device_id']
        )
