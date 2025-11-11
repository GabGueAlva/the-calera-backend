"""
Script to import existing data from The Things Stack into the local database
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from the project
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from infrastructure.external.tts_client import TTSClient
from infrastructure.database.database import SensorDatabase
from domain.value_objects.time_range import TimeRange


async def import_tts_data():
    """Import all available data from TTS into the database"""
    print("="*80)
    print("IMPORTING DATA FROM THE THINGS STACK")
    print("="*80)

    # Initialize clients
    tts_client = TTSClient()
    db = SensorDatabase(db_path="data/sensor_data.db")

    # Fetch all available data from TTS
    # We'll try different time ranges to get all data
    print(f"\nFetching ALL available data from TTS...")
    print(f"Note: TTS Storage API may have limitations on how much data it returns")

    # Try fetching with the "last" parameter directly
    # The TTS client uses last=240h (10 days), but let's see what we actually get
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)  # Try 30 days to get everything
    time_range = TimeRange(start=start_time, end=end_time)

    print(f"Requesting time range: {start_time} to {end_time}")

    # Fetch data from TTS
    sensor_data_list = await tts_client.get_sensor_data_in_range(time_range)

    if not sensor_data_list:
        print("\n⚠️  No data found in TTS storage")
        return

    print(f"\n✓ Found {len(sensor_data_list)} data points from Node 7")
    print(f"Date range: {sensor_data_list[0].timestamp} to {sensor_data_list[-1].timestamp}")

    # Check how many already exist in database
    existing_count = db.get_data_count(device_id="nodo-lora-ud-7")
    print(f"\nCurrent database records: {existing_count}")

    # Save to database
    print(f"\nImporting data to database...")
    saved_count = 0
    for sensor_data in sensor_data_list:
        try:
            db.save_sensor_data(sensor_data)
            saved_count += 1
        except Exception as e:
            print(f"Error saving data point: {e}")

    print(f"\n{'='*80}")
    print(f"✓ IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"Imported: {saved_count} data points")
    print(f"Total in database: {db.get_data_count(device_id='nodo-lora-ud-7')} records")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(import_tts_data())
