"""Satellite Data Adapter for Geostationary INSAT-3D/3DR observations."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ml.preprocessing.fusion.interfaces import (
    BaseMeteorologicalAdapter,
    SatelliteObservation,
    QualityFlag,
)


class SatelliteAdapter(BaseMeteorologicalAdapter):
    """Parses, validates, and normalizes INSAT-type geostationary satellite telemetry."""

    def __init__(self, provider_name: str = "IMD_INSAT_3DR"):
        self.provider_name = provider_name

    def load_from_file(self, file_path: str) -> List[SatelliteObservation]:
        """Loads satellite observation payload from JSON or structured format."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_observations = data.get("observations", [])
        satellite_id = data.get("satellite_id", "INSAT-3DR")
        default_ts_str = data.get("timestamp")
        default_ts = (
            datetime.fromisoformat(default_ts_str.replace("Z", "+00:00"))
            if default_ts_str
            else datetime.now(timezone.utc)
        )

        observations: List[SatelliteObservation] = []
        for obs in raw_observations:
            ts_str = obs.get("timestamp")
            ts = (
                datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts_str
                else default_ts
            )

            sat_obs = SatelliteObservation(
                satellite_id=satellite_id,
                timestamp=ts,
                channel=obs.get("channel", "TIR1_10.8UM"),
                latitude=float(obs["latitude"]),
                longitude=float(obs["longitude"]),
                brightness_temp_kelvin=obs.get("brightness_temp_kelvin"),
                cloud_top_temp_kelvin=obs.get("cloud_top_temp_kelvin"),
                cooling_rate_kelvin_per_hour=obs.get("cooling_rate_kelvin_per_hour"),
                source_resolution_km=float(obs.get("source_resolution_km", 4.0)),
                quality_flag=QualityFlag.VALID,
                metadata={
                    "satellite_name": data.get("satellite_name", "INSAT-3DR"),
                    "scan_type": data.get("scan_type", "RAPID_SECTOR"),
                    "is_sample": data.get("is_sample", True),
                },
            )
            observations.append(sat_obs)

        return self.validate_observations(observations)

    def validate_observations(
        self, observations: List[SatelliteObservation]
    ) -> List[SatelliteObservation]:
        """Validates brightness temperatures against physical limits (150K to 350K)."""
        valid_list: List[SatelliteObservation] = []
        for obs in observations:
            # Physical bounds check for Kelvin temperature
            if obs.brightness_temp_kelvin is not None:
                if not (150.0 <= obs.brightness_temp_kelvin <= 350.0):
                    obs.quality_flag = QualityFlag.INVALID
                    obs.brightness_temp_kelvin = None

            # Bounding box bounds check for India / Delhi-NCR
            if not (-90.0 <= obs.latitude <= 90.0) or not (-180.0 <= obs.longitude <= 180.0):
                obs.quality_flag = QualityFlag.INVALID
                continue

            valid_list.append(obs)

        return valid_list
