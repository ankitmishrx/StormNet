"""Lightning Data Adapter for Lightning Location Network (LLN / IITM / IMD) telemetry."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ml.preprocessing.fusion.interfaces import (
    BaseMeteorologicalAdapter,
    LightningObservation,
    QualityFlag,
)


class LightningAdapter(BaseMeteorologicalAdapter):
    """Parses, validates, and normalizes ground-based lightning network observations."""

    def __init__(self, provider_name: str = "IITM_LLN_NETWORK"):
        self.provider_name = provider_name

    def load_from_file(self, file_path: str) -> List[LightningObservation]:
        """Loads lightning flashes from JSON or telemetric stream record."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_strikes = data.get("strikes", [])
        network_id = data.get("network_id", "IITM_NCR_LLN")

        observations: List[LightningObservation] = []
        for strike in raw_strikes:
            ts_str = strike.get("timestamp")
            ts = (
                datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts_str
                else datetime.now(timezone.utc)
            )

            obs = LightningObservation(
                event_id=strike.get("id", str(strike.get("event_id", "LTG-000"))),
                network_id=network_id,
                timestamp=ts,
                latitude=float(strike["latitude"]),
                longitude=float(strike["longitude"]),
                strike_type=strike.get("type", "CG"),
                peak_current_ka=float(strike["peak_current_ka"]) if "peak_current_ka" in strike else None,
                polarity=strike.get("polarity", "NEGATIVE"),
                quality_flag=QualityFlag.VALID,
                metadata={
                    "sensor_count": strike.get("sensors_participating", 4),
                    "chi_sq": strike.get("chi_sq", 1.0),
                    "is_sample": data.get("is_sample", True),
                },
            )
            observations.append(obs)

        return self.validate_observations(observations)

    def validate_observations(
        self, observations: List[LightningObservation]
    ) -> List[LightningObservation]:
        """Validates lightning strikes against physical limits (-500 kA to +500 kA)."""
        valid_list: List[LightningObservation] = []
        for obs in observations:
            # Physical bounds check for peak current
            if obs.peak_current_ka is not None:
                if not (-500.0 <= obs.peak_current_ka <= 500.0):
                    obs.quality_flag = QualityFlag.INVALID
                    continue

            # Coordinate bounds
            if not (-90.0 <= obs.latitude <= 90.0) or not (-180.0 <= obs.longitude <= 180.0):
                obs.quality_flag = QualityFlag.INVALID
                continue

            valid_list.append(obs)

        return valid_list
