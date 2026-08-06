"""Deterministic sample representing an hourly weather API response for one day."""

from __future__ import annotations

import json
import math


def one_day_weather_payload(day: int = 31, temperature_shift: float = 0.0) -> bytes:
    hours = range(24)
    temperatures = [round(13.8 + temperature_shift + 5.7 * math.sin((hour - 7) * math.pi / 12), 1) for hour in hours]
    precipitation = [round(max(0, 0.8 * math.sin((hour - 14) * math.pi / 7)), 1) for hour in hours]
    weather = {
        "latitude": 52.52,
        "longitude": 13.405,
        "timezone": "Europe/Berlin",
        "timezone_abbreviation": "GMT+2",
        "elevation": 34.0,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "relative_humidity_2m": "%",
            "precipitation": "mm",
            "wind_speed_10m": "km/h",
        },
        "hourly": {
            "time": [f"2026-07-{day:02d}T{hour:02d}:00" for hour in hours],
            "temperature_2m": temperatures,
            "relative_humidity_2m": [round(72 - (temperature - 10) * 3.1) for temperature in temperatures],
            "precipitation": precipitation,
            "wind_speed_10m": [round(9 + 5 * abs(math.sin(hour * math.pi / 9)), 1) for hour in hours],
        },
    }
    return json.dumps(weather, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def historical_weather_samples() -> list[bytes]:
    """Representative prior days used only for the demo training phase."""
    return [one_day_weather_payload(day, shift) for day, shift in zip(range(24, 31), (-1.7, -1.1, -0.5, 0.2, 0.8, 1.3, 0.4))]
