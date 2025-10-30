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
            "Content-Type": "application/json",
        }

        params = {
            "field_mask": "up.uplink_message.decoded_payload,up.uplink_message.received_at,end_device_ids.device_id",
            "after": time_range.start.replace(tzinfo=timezone.utc).isoformat(),
            "before": time_range.end.replace(tzinfo=timezone.utc).isoformat(),
            "limit": 10000,
        }

        url = f"{self.base_url}/api/v3/as/applications/{self.application_id}/packages/storage/{self.storage_integration_id}/uplink_message"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                sensor_data_list = []
                
                for message in data.get("result", {}).get("uplink_messages", []):
                    try:
                        payload = message.get("up", {}).get("uplink_message", {}).get("decoded_payload", {})
                        received_at = message.get("up", {}).get("uplink_message", {}).get("received_at")
                        device_id = message.get("up", {}).get("uplink_message", {}).get("end_device_ids", {}).get("device_id")
                        
                        if not all([payload, received_at, device_id]):
                            continue
                            
                        timestamp = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
                        
                        sensor_data = SensorData(
                            temperature=payload.get("temperature", 0.0),
                            humidity=payload.get("humidity", 0.0),
                            wind_speed=payload.get("wind_speed", 0.0),
                            timestamp=timestamp,
                            device_id=device_id,
                        )
                        sensor_data_list.append(sensor_data)
                        
                    except Exception as e:
                        print(f"Error parsing sensor data: {e}")
                        continue
                
                return sensor_data_list
                
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                return []
            except Exception as e:
                print(f"Error fetching data from TTS: {e}")
                return []