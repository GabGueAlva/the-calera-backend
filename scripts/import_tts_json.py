#!/usr/bin/env python3
"""
Import TTS webhook messages from JSON file to PostgreSQL database
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.database.postgres_database import PostgresSensorDatabase
from domain.entities.sensor_data import SensorData


def parse_tts_message(message: dict) -> SensorData:
    """Parse a TTS webhook message into SensorData entity"""
    # Extract fields
    device_id = message.get("end_device_ids", {}).get("device_id", "unknown")
    received_at = message.get("received_at")
    decoded_payload = message.get("uplink_message", {}).get("decoded_payload", {})

    # Parse timestamp
    timestamp = datetime.fromisoformat(received_at.replace('Z', '+00:00'))

    # Extract sensor values (handle both Spanish and English field names)
    temperature = decoded_payload.get("temperatura_c", decoded_payload.get("temperature_c", 0.0))
    humidity = decoded_payload.get("humedad_pct", decoded_payload.get("humidity_percent", 0.0))
    wind_speed = decoded_payload.get("viento_ms", decoded_payload.get("wind_speed", 0.0))

    return SensorData(
        temperature=float(temperature),
        humidity=float(humidity),
        wind_speed=float(wind_speed),
        timestamp=timestamp,
        device_id=device_id
    )


def import_json_file(json_file_path: str, database_url: str):
    """Import TTS messages from JSON file to database"""
    print("="*80)
    print("TTS JSON IMPORT TO POSTGRESQL")
    print("="*80)

    # Load JSON file
    print(f"\n[1/4] Loading JSON file: {json_file_path}")
    with open(json_file_path, 'r') as f:
        messages = json.load(f)

    print(f"✓ Loaded {len(messages)} messages")

    # Filter for nodes 1, 6, and 7
    allowed_nodes = ["nodo-lora-ud-1", "nodo-lora-ud-6", "nodo-lora-ud-7"]
    filtered_messages = []

    for msg in messages:
        device_id = msg.get("end_device_ids", {}).get("device_id", "")
        if device_id in allowed_nodes:
            filtered_messages.append(msg)

    print(f"✓ Filtered to {len(filtered_messages)} messages from nodes 1, 6, and 7")

    if len(filtered_messages) == 0:
        print("\n⚠️  No messages from configured nodes found!")
        return

    # Show node breakdown
    node_counts = {}
    for msg in filtered_messages:
        device_id = msg.get("end_device_ids", {}).get("device_id", "")
        node_counts[device_id] = node_counts.get(device_id, 0) + 1

    print("\nMessages by node:")
    for node, count in sorted(node_counts.items()):
        print(f"  {node}: {count} messages")

    # Connect to database
    print(f"\n[2/4] Connecting to PostgreSQL...")
    db = PostgresSensorDatabase(database_url=database_url)
    print("✓ Connected")

    # Parse and import messages
    print(f"\n[3/4] Importing {len(filtered_messages)} messages...")
    imported_count = 0
    error_count = 0
    skipped_count = 0

    for i, message in enumerate(filtered_messages, 1):
        try:
            sensor_data = parse_tts_message(message)
            db.save_sensor_data(sensor_data)
            imported_count += 1

            # Show progress every 50 messages
            if i % 50 == 0 or i == len(filtered_messages):
                print(f"  Progress: {i}/{len(filtered_messages)} ({(i/len(filtered_messages))*100:.1f}%)")
        except Exception as e:
            # Check if it's a duplicate (already exists)
            if "duplicate key" in str(e).lower():
                skipped_count += 1
            else:
                error_count += 1
                print(f"  ✗ Error on message {i}: {e}")

    # Summary
    print("\n[4/4] Import complete!")
    print("="*80)
    print(f"✓ Successfully imported: {imported_count} messages")
    if skipped_count > 0:
        print(f"⊘ Skipped (duplicates):  {skipped_count} messages")
    if error_count > 0:
        print(f"✗ Failed to import:     {error_count} messages")
    print("="*80)

    # Show time range
    if imported_count > 0:
        timestamps = []
        for msg in filtered_messages:
            try:
                received_at = msg.get("received_at")
                timestamps.append(datetime.fromisoformat(received_at.replace('Z', '+00:00')))
            except:
                pass

        if timestamps:
            timestamps.sort()
            print(f"\nData time range:")
            print(f"  First: {timestamps[0]}")
            print(f"  Last:  {timestamps[-1]}")
            print(f"  Span:  {(timestamps[-1] - timestamps[0]).days} days")

    print("\n✓ Import completed successfully!")


if __name__ == "__main__":
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set it to your PostgreSQL connection string.")
        print("\nExample:")
        print('  export DATABASE_URL="postgresql://user:pass@host:5432/db"')
        print('  python scripts/import_tts_json.py <json_file>')
        sys.exit(1)

    # Get JSON file path from command line
    if len(sys.argv) < 2:
        print("\n❌ ERROR: JSON file path not provided!")
        print("\nUsage:")
        print("  python scripts/import_tts_json.py <json_file_path>")
        print("\nExample:")
        print("  python scripts/import_tts_json.py ~/Downloads/stored_messages_1762998079010.json")
        sys.exit(1)

    json_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(json_file):
        print(f"\n❌ ERROR: File not found: {json_file}")
        sys.exit(1)

    # Run import
    try:
        import_json_file(json_file, database_url)
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
