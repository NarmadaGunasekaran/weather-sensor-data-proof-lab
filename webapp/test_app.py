"""Focused tests for the local upload dashboard."""

from __future__ import annotations

import io
import unittest

from app import create_app


class WeatherCompressionWebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_app().test_client()

    def test_included_sample_displays_lossless_results(self) -> None:
        response = self.client.post("/", data={"action": "sample"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lossless verification", response.data)
        self.assertIn(b"trained-weather-agent", response.data)

    def test_rejects_non_weather_file_extensions(self) -> None:
        response = self.client.post(
            "/",
            data={"action": "upload", "weather_file": (io.BytesIO(b"data"), "weather.exe")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Only JSON, CSV, and TXT files are accepted", response.data)


if __name__ == "__main__":
    unittest.main()
