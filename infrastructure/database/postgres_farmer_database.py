import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

from domain.entities.farmer import Farmer


class PostgresFarmerDatabase:
    """PostgreSQL database for storing farmer registrations"""

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
        """Create the farmers table if it doesn't exist"""
        if self._initialized:
            return

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS farmers (
                            phone_number TEXT PRIMARY KEY,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            lot_address TEXT NOT NULL,
                            registered_at TIMESTAMP WITH TIME ZONE NOT NULL
                        )
                    """)

                    # Create index on registered_at for sorting
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_farmers_registered_at
                        ON farmers(registered_at)
                    """)

                    self._initialized = True
                    print("[FARMER DATABASE] PostgreSQL farmers table initialized successfully")
        except Exception as e:
            print(f"[FARMER DATABASE] Warning: Could not initialize database: {e}")
            print("[FARMER DATABASE] Will retry on first database operation")

    def save_farmer(self, farmer: Farmer) -> None:
        """Save a farmer to the database"""
        self._initialize_database()  # Ensure DB is initialized
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO farmers
                    (phone_number, first_name, last_name, lot_address, registered_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (phone_number) DO UPDATE SET
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        lot_address = EXCLUDED.lot_address,
                        registered_at = EXCLUDED.registered_at
                """, (
                    farmer.phone_number,
                    farmer.first_name,
                    farmer.last_name,
                    farmer.lot_address,
                    farmer.registered_at
                ))
                print(f"[FARMER DATABASE] Saved farmer: {farmer.first_name} {farmer.last_name} ({farmer.phone_number})")

    def get_all_farmers(self) -> List[Farmer]:
        """Retrieve all farmers from the database"""
        self._initialize_database()
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM farmers
                    ORDER BY registered_at DESC
                """)

                rows = cursor.fetchall()
                return [self._row_to_farmer(dict(row)) for row in rows]

    def get_farmer_by_phone(self, phone_number: str) -> Optional[Farmer]:
        """Get a farmer by phone number"""
        self._initialize_database()
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM farmers
                    WHERE phone_number = %s
                """, (phone_number,))

                row = cursor.fetchone()
                return self._row_to_farmer(dict(row)) if row else None

    def get_all_phone_numbers(self) -> List[str]:
        """Get all registered phone numbers"""
        self._initialize_database()
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT phone_number FROM farmers
                    ORDER BY registered_at DESC
                """)

                rows = cursor.fetchall()
                return [row[0] for row in rows]

    def delete_farmer(self, phone_number: str) -> bool:
        """Delete a farmer by phone number"""
        self._initialize_database()
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM farmers
                    WHERE phone_number = %s
                """, (phone_number,))

                deleted = cursor.rowcount > 0
                if deleted:
                    print(f"[FARMER DATABASE] Deleted farmer with phone: {phone_number}")
                return deleted

    def get_farmer_count(self) -> int:
        """Get the total count of registered farmers"""
        self._initialize_database()
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM farmers")
                return cursor.fetchone()[0]

    def _row_to_farmer(self, row) -> Farmer:
        """Convert a database row to a Farmer entity"""
        return Farmer(
            phone_number=row['phone_number'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            lot_address=row['lot_address'],
            registered_at=row['registered_at'] if isinstance(row['registered_at'], datetime) else datetime.fromisoformat(str(row['registered_at']))
        )
