import random
from datetime import datetime, timedelta, timezone
from typing import List

from domain.entities.sensor_data import SensorData
from domain.value_objects.time_range import TimeRange


class MockTTSClient:
    """
    Mock TTS Client that generates realistic sensor data for testing purposes.
    This simulates temperature, humidity, and wind speed data that follows
    realistic patterns for frost prediction scenarios.
    """

    def __init__(self):
        print("\n" + "="*60)
        print("[MOCK TTS] Using Mock TTS Client for testing")
        print("[MOCK TTS] Simulated sensor data will be generated")
        print("="*60 + "\n")

    def _generate_realistic_temperature(self, hour: int, base_temp: float = 15.0) -> float:
        """
        Generate realistic temperature based on time of day.
        Temperatures are lower at night (potential frost) and higher during day.
        """
        # Temperature follows a sine wave pattern throughout the day
        # Coldest around 6 AM, warmest around 3 PM
        time_factor = -8 * ((hour - 15) / 12) ** 2 + 8

        # Add some random variation
        noise = random.uniform(-1.5, 1.5)

        temperature = base_temp + time_factor + noise

        # For frost scenarios, make nighttime temperatures potentially drop below 0
        if 0 <= hour <= 6 or 22 <= hour <= 23:
            # 30% chance of frost conditions at night
            if random.random() < 0.3:
                temperature = random.uniform(-2.0, 2.0)

        return round(temperature, 2)

    def _generate_realistic_humidity(self, temperature: float) -> float:
        """
        Generate realistic humidity inversely related to temperature.
        Higher humidity at lower temperatures.
        """
        # Base humidity inversely proportional to temperature
        base_humidity = 85 - (temperature * 2)

        # Add random variation
        noise = random.uniform(-10, 10)

        humidity = base_humidity + noise

        # Clamp between 20% and 95%
        return round(max(20.0, min(95.0, humidity)), 2)

    def _generate_realistic_wind_speed(self) -> float:
        """
        Generate realistic wind speed.
        Wind speed affects frost formation (higher wind reduces frost risk).
        """
        # Most common wind speeds are between 0-15 km/h
        # Use exponential distribution for realistic wind patterns
        wind_speed = random.expovariate(1/5)

        # Clamp between 0 and 30 km/h
        return round(min(30.0, wind_speed), 2)

    async def get_sensor_data_in_range(self, time_range: TimeRange) -> List[SensorData]:
        """
        Generate mock sensor data for the given time range.
        Data points are generated every 5 minutes (standard TTS interval).
        """
        print("\n" + "="*60)
        print("[MOCK TTS] Generating sensor data...")
        print(f"[MOCK TTS] Time range: {time_range.start} to {time_range.end}")
        print("="*60)

        sensor_data_list = []

        # Generate data points every 5 minutes
        current_time = time_range.start
        device_id = "mock-sensor-001"

        # Determine base temperature (can vary between runs)
        base_temp = random.uniform(10.0, 18.0)
        print(f"[MOCK TTS] Base temperature for this generation: {base_temp:.1f}°C")
        print(f"[MOCK TTS] Generating data points (one every 5 minutes)...")

        while current_time <= time_range.end:
            hour = current_time.hour

            temperature = self._generate_realistic_temperature(hour, base_temp)
            humidity = self._generate_realistic_humidity(temperature)
            wind_speed = self._generate_realistic_wind_speed()

            sensor_data = SensorData(
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                timestamp=current_time.replace(tzinfo=timezone.utc),
                device_id=device_id,
            )

            sensor_data_list.append(sensor_data)

            # Move to next 5-minute interval
            current_time += timedelta(minutes=5)

        min_temp = min(d.temperature for d in sensor_data_list)
        max_temp = max(d.temperature for d in sensor_data_list)
        frost_points = sum(1 for d in sensor_data_list if d.temperature <= 0)

        print("-"*60)
        print(f"[MOCK TTS] ✓ Generated {len(sensor_data_list)} data points")
        print(f"[MOCK TTS] Temperature range: {min_temp:.1f}°C to {max_temp:.1f}°C")
        print(f"[MOCK TTS] Frost conditions detected: {frost_points} points at or below 0°C")
        print("="*60 + "\n")

        return sensor_data_list
