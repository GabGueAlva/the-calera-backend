from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from ..schemas.webhook_schemas import TTSWebhookPayload, WebhookResponse
from domain.entities.sensor_data import SensorData
from infrastructure.repositories.database_sensor_data_repository import DatabaseSensorDataRepository


class WebhookController:
    def __init__(self, sensor_repository: Optional[DatabaseSensorDataRepository] = None):
        self.sensor_repository = sensor_repository
        self.router = APIRouter()
        self.router.add_api_route(
            "/webhook",
            self.handle_tts_webhook,
            methods=["POST"],
            response_model=WebhookResponse
        )

    async def handle_tts_webhook(self, payload: Dict[Any, Any]) -> WebhookResponse:
        try:
            # Extract device ID
            device_id = payload.get("end_device_ids", {}).get("device_id", "unknown")

            # Filter for Nodes 1, 6, and 7 only (additional safety check)
            allowed_nodes = ["nodo-lora-ud-1", "nodo-lora-ud-6", "nodo-lora-ud-7"]
            if device_id not in allowed_nodes:
                print(f"Ignoring webhook from device: {device_id}")
                return WebhookResponse(
                    status="ignored",
                    message=f"Device {device_id} not configured for processing",
                    timestamp=datetime.utcnow().isoformat()
                )

            # Extract decoded payload data
            uplink_message = payload.get("uplink_message", {})
            decoded_payload = uplink_message.get("decoded_payload", {})
            received_at = payload.get("received_at", datetime.utcnow().isoformat())

            # Extract sensor values (handle both Spanish and English field names)
            temperature = decoded_payload.get('temperatura_c', decoded_payload.get('temperature', 0.0))
            humidity = decoded_payload.get('humedad_pct', decoded_payload.get('humidity', 0.0))
            wind_speed = decoded_payload.get('viento_ms', decoded_payload.get('wind_speed', 0.0))

            # Parse timestamp
            timestamp = datetime.fromisoformat(received_at.replace("Z", "+00:00"))

            # Create SensorData entity
            sensor_data = SensorData(
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                timestamp=timestamp,
                device_id=device_id
            )

            # Save to database
            if self.sensor_repository:
                self.sensor_repository.save_sensor_data(sensor_data)
                print(f"\n{'='*60}")
                print(f"✓ {device_id.upper()} DATA SAVED TO DATABASE at {received_at}")
                print(f"{'='*60}")
                print(f"Temperature: {temperature}°C")
                print(f"Humidity: {humidity}%")
                print(f"Wind Speed: {wind_speed} m/s")
                print(f"Battery: {decoded_payload.get('bateria_pct', decoded_payload.get('battery_percent'))}%")
                print(f"Packet Number: {decoded_payload.get('paquete_total', decoded_payload.get('packet_number'))}")
                print(f"Counter: {decoded_payload.get('contador', decoded_payload.get('counter'))}")
                print(f"{'='*60}\n")
            else:
                print(f"⚠️  Warning: Database repository not configured, data not saved!")

            return WebhookResponse(
                status="success",
                message=f"{device_id} data received and processed successfully",
                timestamp=datetime.utcnow().isoformat()
            )

        except Exception as e:
            print(f"Error processing webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")