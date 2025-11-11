import asyncio
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx

from domain.entities.sensor_data import SensorData
from domain.value_objects.time_range import TimeRange
from ..config.settings import settings


class TTSClient:
    def __init__(self):
        self.base_url = settings.tts_server_url
        self.application_id = settings.tts_application_id
        self.api_key = settings.tts_api_key
        self.storage_integration_id = settings.tts_storage_integration_id

    async def get_sensor_data_in_range(self, time_range: TimeRange) -> List[SensorData]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream",
        }

        # Calculate hours between start and end time
        time_diff = time_range.end - time_range.start
        hours = int(time_diff.total_seconds() / 3600)

        # TTS Storage API uses "last" parameter with format like "240h" for 240 hours
        # Maximum is typically limited by the storage retention policy
        params = {
            "last": f"{hours}h",
        }

        print(f"[TTS] Requesting last {hours} hours of data ({hours/24:.1f} days)")

        url = f"{self.base_url}/api/v3/as/applications/{self.application_id}/packages/storage/uplink_message"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                # Parse event-stream response (each line is a JSON object)
                sensor_data_list = []
                response_text = response.text

                # Split by lines and parse each JSON event
                for line in response_text.strip().split('\n'):
                    if not line.strip():
                        continue

                    try:
                        # Parse JSON line
                        message = json.loads(line)

                        # Extract data from the message structure
                        result = message.get("result", {})
                        uplink_message = result.get("uplink_message", {})

                        payload = uplink_message.get("decoded_payload", {})
                        received_at = uplink_message.get("received_at")
                        end_device_ids = result.get("end_device_ids", {})
                        device_id = end_device_ids.get("device_id")

                        if not all([payload, received_at, device_id]):
                            continue

                        # Filter for Nodes 1, 6, and 7 only
                        allowed_nodes = ["nodo-lora-ud-1", "nodo-lora-ud-6", "nodo-lora-ud-7"]
                        if device_id not in allowed_nodes:
                            continue

                        timestamp = datetime.fromisoformat(received_at.replace("Z", "+00:00"))

                        # Handle both Spanish and English field names
                        temperature = payload.get("temperatura_c", payload.get("temperature", 0.0))
                        humidity = payload.get("humedad_pct", payload.get("humidity", 0.0))
                        wind_speed = payload.get("viento_ms", payload.get("wind_speed", 0.0))

                        sensor_data = SensorData(
                            temperature=temperature,
                            humidity=humidity,
                            wind_speed=wind_speed,
                            timestamp=timestamp,
                            device_id=device_id,
                        )
                        sensor_data_list.append(sensor_data)

                    except Exception as e:
                        print(f"Error parsing sensor data: {e}")
                        continue

                # Log all fetched data
                print(f"\n{'='*80}")
                print(f"[TTS] Fetched {len(sensor_data_list)} data points from Nodes 1, 6, and 7")
                print(f"{'='*80}")
                if sensor_data_list:
                    print(f"First data point: {sensor_data_list[0].timestamp} - Temp: {sensor_data_list[0].temperature}°C - Device: {sensor_data_list[0].device_id}")
                    print(f"Last data point:  {sensor_data_list[-1].timestamp} - Temp: {sensor_data_list[-1].temperature}°C - Device: {sensor_data_list[-1].device_id}")
                    print(f"\nAll temperature readings:")
                    for i, data in enumerate(sensor_data_list, 1):
                        print(f"  {i:3d}. {data.timestamp} | Device: {data.device_id:16s} | Temp: {data.temperature:5.1f}°C | Humidity: {data.humidity:5.1f}% | Wind: {data.wind_speed:5.1f} m/s")
                print(f"{'='*80}\n")

                return sensor_data_list
                
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                return []
            except Exception as e:
                print(f"Error fetching data from TTS: {e}")
                return []