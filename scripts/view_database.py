"""
Script to view the contents of the sensor data database (PostgreSQL)
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.postgres_database import PostgresSensorDatabase
from datetime import datetime, timedelta


def view_database():
    """Display database statistics and recent data"""
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL to your PostgreSQL connection string.")
        print("\nExample:")
        print('  export DATABASE_URL="postgresql://user:pass@host:5432/db"')
        print('  python scripts/view_database.py')
        return

    db = PostgresSensorDatabase(database_url=database_url)

    print("\n" + "="*80)
    print("SENSOR DATA DATABASE VIEWER (PostgreSQL)")
    print("="*80)

    # Get total counts by device
    print("\nTotal records by device:")
    for device_id in ["nodo-lora-ud-1", "nodo-lora-ud-6", "nodo-lora-ud-7"]:
        count = db.get_data_count(device_id=device_id)
        print(f"  {device_id}: {count} records")

    total_count = db.get_data_count()
    print(f"\nTotal records (all devices): {total_count}")

    if total_count == 0:
        print("\n⚠️  Database is empty. No data has been received yet.")
        return

    # Get latest data point
    latest = db.get_latest_sensor_data()
    if latest:
        print(f"\nLatest data point:")
        print(f"  Device:      {latest.device_id}")
        print(f"  Timestamp:   {latest.timestamp}")
        print(f"  Temperature: {latest.temperature}°C")
        print(f"  Humidity:    {latest.humidity}%")
        print(f"  Wind Speed:  {latest.wind_speed} m/s")

    # Get data from last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    recent_data = db.get_sensor_data_in_range(start_time, end_time)

    print(f"\n" + "-"*80)
    print(f"Last 24 hours: {len(recent_data)} data points")
    print("-"*80)

    if recent_data:
        print(f"\nShowing last 20 entries:")
        for i, data in enumerate(recent_data[-20:], 1):
            print(f"  {i:2d}. {data.timestamp} | {data.device_id:16s} | "
                  f"Temp: {data.temperature:5.1f}°C | "
                  f"Humidity: {data.humidity:5.1f}% | Wind: {data.wind_speed:5.1f} m/s")

    # Get data from last 7 days
    start_time_week = end_time - timedelta(days=7)
    week_data = db.get_sensor_data_in_range(start_time_week, end_time)

    print(f"\n" + "-"*80)
    print(f"Last 7 days: {len(week_data)} data points")
    print("-"*80)

    if week_data:
        print(f"  First: {week_data[0].timestamp}")
        print(f"  Last:  {week_data[-1].timestamp}")

        # Calculate some stats
        temps = [d.temperature for d in week_data]
        if temps:
            print(f"\nTemperature Statistics (Last 7 days):")
            print(f"  Min:     {min(temps):.1f}°C")
            print(f"  Max:     {max(temps):.1f}°C")
            print(f"  Average: {sum(temps)/len(temps):.1f}°C")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    view_database()
