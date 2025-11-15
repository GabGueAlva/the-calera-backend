#!/usr/bin/env python3
"""
Script to import historical sensor data from TTS JSON files into Supabase database.
This script reads multiple JSON files containing The Things Stack messages and inserts
the sensor readings (temperature, humidity, wind speed) into the PostgreSQL database.

Usage:
    python scripts/import_historical_data.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.postgres_database import PostgresSensorDatabase
from domain.entities.sensor_data import SensorData
from infrastructure.config.settings import settings


def parse_tts_message(message: dict) -> SensorData:
    """
    Parse a TTS (The Things Stack) message and extract sensor data.

    Args:
        message: Dictionary containing the TTS uplink message

    Returns:
        SensorData entity with parsed information
    """
    device_id = message["end_device_ids"]["device_id"]
    received_at = message["received_at"]
    decoded_payload = message["uplink_message"]["decoded_payload"]

    # Extract sensor readings from decoded payload
    temperature = decoded_payload["temperatura_c"]
    humidity = decoded_payload["humedad_pct"]
    wind_speed = decoded_payload["viento_ms"]

    # Parse timestamp
    timestamp = datetime.fromisoformat(received_at.replace('Z', '+00:00'))

    return SensorData(
        temperature=float(temperature),
        humidity=float(humidity),
        wind_speed=float(wind_speed),
        timestamp=timestamp,
        device_id=device_id
    )


def load_json_file(file_path: str) -> list:
    """Load and parse a JSON file containing TTS messages."""
    print(f"📖 Reading file: {file_path}")
    with open(file_path, 'r') as f:
        data = json.load(f)
    print(f"   ✓ Found {len(data)} messages")
    return data


def import_data_batch(database: PostgresSensorDatabase, sensor_data_list: list):
    """
    Import a batch of sensor data using a single connection.

    Args:
        database: PostgreSQL database instance
        sensor_data_list: List of SensorData objects to insert
    """
    import psycopg2

    conn = psycopg2.connect(database.database_url, connect_timeout=30)
    try:
        with conn.cursor() as cursor:
            # Insert all records in a single transaction
            for sensor_data in sensor_data_list:
                cursor.execute("""
                    INSERT INTO sensor_data
                    (id, device_id, temperature, humidity, wind_speed, timestamp, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    str(sensor_data.id),
                    sensor_data.device_id,
                    sensor_data.temperature,
                    sensor_data.humidity,
                    sensor_data.wind_speed,
                    sensor_data.timestamp,
                    datetime.utcnow()
                ))
        conn.commit()
        return len(sensor_data_list)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def import_data_from_files(database: PostgresSensorDatabase, file_paths: list):
    """
    Import sensor data from multiple JSON files into the database.

    Args:
        database: PostgreSQL database instance
        file_paths: List of file paths to import
    """
    print("\n" + "="*70)
    print("🌡️  HISTORICAL SENSOR DATA IMPORT")
    print("="*70 + "\n")

    total_messages = 0
    total_inserted = 0
    total_skipped = 0

    all_sensor_data = []

    # First, collect all data from all files
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue

        messages = load_json_file(file_path)
        total_messages += len(messages)

        # Parse each message
        for message in messages:
            try:
                sensor_data = parse_tts_message(message)
                all_sensor_data.append(sensor_data)
            except Exception as e:
                print(f"   ⚠️  Skipped message: {e}")
                total_skipped += 1
                continue

    # Now insert all data in one batch
    print(f"\n💾 Inserting {len(all_sensor_data)} records in batch...")
    try:
        total_inserted = import_data_batch(database, all_sensor_data)
        print(f"   ✓ Successfully inserted {total_inserted} records")
    except Exception as e:
        print(f"   ❌ Error during batch insert: {e}")
        print("   Falling back to individual inserts...")

        # Fallback: insert one by one
        for sensor_data in all_sensor_data:
            try:
                database.save_sensor_data(sensor_data)
                total_inserted += 1
                if total_inserted % 10 == 0:
                    print(f"   💾 Inserted {total_inserted} records...")
            except Exception as e:
                print(f"   ⚠️  Skipped record: {e}")
                total_skipped += 1

    print("\n" + "="*70)
    print("📊 IMPORT SUMMARY")
    print("="*70)
    print(f"Total messages processed: {total_messages}")
    print(f"Successfully inserted:    {total_inserted}")
    print(f"Skipped (errors/dupes):   {total_skipped}")

    try:
        final_count = database.get_data_count()
        print(f"Final database count:     {final_count}")
    except:
        print(f"Final database count:     (unable to query)")

    print("="*70 + "\n")
    print("✅ Import completed successfully!\n")


def main():
    """Main function to run the import."""

    # Check database URL
    if not settings.database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set your Supabase connection string:")
        print('export DATABASE_URL="postgresql://user:pass@host:port/database"')
        sys.exit(1)

    print(f"🔗 Connecting to database...")
    print(f"   Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'local'}\n")

    # Initialize database (skip if tables already exist)
    database = PostgresSensorDatabase(database_url=settings.database_url)

    # Try to get current count (this will initialize if needed)
    try:
        print("📊 Checking current database state...")
        current_count = database.get_data_count()
        print(f"   ✓ Current records in database: {current_count}\n")
    except Exception as e:
        print(f"   ⚠️  Could not get current count: {e}")
        print("   Attempting to initialize database...\n")
        try:
            database._initialize_database()
            print("   ✓ Database initialized\n")
        except Exception as init_error:
            print(f"   ⚠️  Database initialization warning: {init_error}")
            print("   Continuing anyway...\n")

    # Define file paths - UPDATE THESE to match your file locations
    file_paths = [
        "/Users/anaguevara/Downloads/stored_messages_1763217253651.json",
        "/Users/anaguevara/Downloads/stored_messages_1763217257557.json",
        "/Users/anaguevara/Downloads/stored_messages_1763217261439.json",
        "/Users/anaguevara/Downloads/stored_messages_1763217268513.json",
    ]

    # Import data from all files
    import_data_from_files(database, file_paths)


if __name__ == "__main__":
    main()
