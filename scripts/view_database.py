"""
Script to view the contents of the sensor data database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.database import SensorDatabase
from datetime import datetime, timedelta


def view_database():
    """Display database statistics and recent data"""
    db = SensorDatabase(db_path="data/sensor_data.db")

    print("\n" + "="*80)
    print("SENSOR DATA DATABASE VIEWER")
    print("="*80)

    # Get total count
    total_count = db.get_data_count(device_id="nodo-lora-ud-7")
    print(f"\nTotal records for Node 7: {total_count}")

    if total_count == 0:
        print("\n⚠️  Database is empty. Run 'python scripts/import_tts_data.py' to import data.")
        return

    # Get latest data point
    latest = db.get_latest_sensor_data(device_id="nodo-lora-ud-7")
    if latest:
        print(f"\nLatest data point:")
        print(f"  Timestamp:   {latest.timestamp}")
        print(f"  Temperature: {latest.temperature}°C")
        print(f"  Humidity:    {latest.humidity}%")
        print(f"  Wind Speed:  {latest.wind_speed} m/s")

    # Get data from last 24 hours
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    recent_data = db.get_sensor_data_in_range(start_time, end_time, device_id="nodo-lora-ud-7")

    print(f"\n" + "-"*80)
    print(f"Last 24 hours: {len(recent_data)} data points")
    print("-"*80)

    if recent_data:
        print(f"\nShowing last 20 entries:")
        for i, data in enumerate(recent_data[-20:], 1):
            print(f"  {i:2d}. {data.timestamp} | Temp: {data.temperature:5.1f}°C | "
                  f"Humidity: {data.humidity:5.1f}% | Wind: {data.wind_speed:5.1f} m/s")

    # Get data from last 7 days
    start_time_week = end_time - timedelta(days=7)
    week_data = db.get_sensor_data_in_range(start_time_week, end_time, device_id="nodo-lora-ud-7")

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
