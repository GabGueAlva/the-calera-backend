"""
Script to remove duplicate sensor data from the database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3


def clean_duplicates():
    """Remove duplicate sensor data entries, keeping only the most recent version"""
    db_path = "data/sensor_data.db"

    print("="*80)
    print("CLEANING DUPLICATE RECORDS")
    print("="*80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count total records before
    cursor.execute("SELECT COUNT(*) FROM sensor_data WHERE device_id = 'nodo-lora-ud-7'")
    before_count = cursor.fetchone()[0]
    print(f"\nRecords before cleaning: {before_count}")

    # Find duplicates (same timestamp and device_id)
    cursor.execute("""
        SELECT timestamp, COUNT(*) as count
        FROM sensor_data
        WHERE device_id = 'nodo-lora-ud-7'
        GROUP BY timestamp
        HAVING count > 1
    """)

    duplicates = cursor.fetchall()

    if duplicates:
        print(f"\nFound {len(duplicates)} timestamps with duplicate entries:")
        for timestamp, count in duplicates[:5]:  # Show first 5
            print(f"  {timestamp}: {count} copies")
        if len(duplicates) > 5:
            print(f"  ... and {len(duplicates) - 5} more")

        # Remove duplicates, keeping the one with latest created_at
        print("\nRemoving duplicates (keeping most recent version)...")
        cursor.execute("""
            DELETE FROM sensor_data
            WHERE rowid NOT IN (
                SELECT MAX(rowid)
                FROM sensor_data
                WHERE device_id = 'nodo-lora-ud-7'
                GROUP BY timestamp, device_id
            )
            AND device_id = 'nodo-lora-ud-7'
        """)

        removed = cursor.rowcount
        conn.commit()
        print(f"✓ Removed {removed} duplicate records")
    else:
        print("\n✓ No duplicates found!")

    # Count total records after
    cursor.execute("SELECT COUNT(*) FROM sensor_data WHERE device_id = 'nodo-lora-ud-7'")
    after_count = cursor.fetchone()[0]

    print(f"\nRecords after cleaning: {after_count}")
    print("="*80 + "\n")

    conn.close()


if __name__ == "__main__":
    clean_duplicates()
