"""Atmospheric Data Adapter for Automatic Weather Stations (AWS / Surface observations)."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ml.preprocessing.fusion.interfaces import (
    BaseMeteorologicalAdapter,
    AtmosphericObservation,
    QualityFlag,
)


class AtmosphericAdapter(BaseMeteorologicalAdapter):
    """Parses, validates, and normalizes surface Automatic Weather Station (AWS) records."""

    def __init__(self, provider_name: str = "IMD_AWS_SURFACE"):
        self.provider_name = provider_name

    def load_from_file(self, file_path: str) -> List[AtmosphericObservation]:
        """Loads surface AWS station readings from JSON or tabular format."""
        if file_path.endswith(".csv"):
            import csv
            import math
            observations: List[AtmosphericObservation] = []
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date_str = row.get("DATE")
                    if not date_str:
                        continue
                    try:
                        ts = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                    except Exception:
                        continue

                    lat = float(row.get("LATITUDE", 28.5665))
                    lon = float(row.get("LONGITUDE", 77.103088))
                    stn_id = row.get("STATION", "VIDP_DELHI")

                    # Temperature & Dew Point
                    t_c = None
                    if "TMP" in row:
                        val = row["TMP"].split(",")[0]
                        if val not in ["+9999", "9999"]:
                            try:
                                t_c = float(val) / 10.0
                            except ValueError:
                                pass

                    dew_c = None
                    if "DEW" in row:
                        val = row["DEW"].split(",")[0]
                        if val not in ["+9999", "9999"]:
                            try:
                                dew_c = float(val) / 10.0
                            except ValueError:
                                pass

                    # Relative humidity approximation from T and Td
                    rh_pct = None
                    if t_c is not None and dew_c is not None:
                        try:
                            es = 6.112 * math.exp((17.67 * t_c) / (t_c + 243.5))
                            e = 6.112 * math.exp((17.67 * dew_c) / (dew_c + 243.5))
                            rh_pct = min(100.0, max(0.0, round((e / es) * 100.0, 1)))
                        except Exception:
                            pass

                    # Pressure
                    p_hpa = None
                    if "SLP" in row:
                        val = row["SLP"].split(",")[0]
                        if val not in ["99999", "+9999"]:
                            try:
                                p_hpa = float(val) / 10.0
                            except ValueError:
                                pass

                    # Wind
                    w_kmh = None
                    w_deg = None
                    if "WND" in row:
                        parts = row["WND"].split(",")
                        if len(parts) >= 4:
                            if parts[0] not in ["999", "9999"]:
                                try:
                                    w_deg = float(parts[0])
                                except ValueError:
                                    pass
                            if parts[3] not in ["9999", "999"]:
                                try:
                                    w_kmh = round((float(parts[3]) / 10.0) * 3.6, 2)
                                except ValueError:
                                    pass

                    # Precip
                    precip_mmh = None
                    if "AA1" in row:
                        parts = row["AA1"].split(",")
                        if len(parts) >= 2 and parts[1] not in ["9999", "999"]:
                            try:
                                precip_mmh = float(parts[1]) / 10.0
                            except ValueError:
                                pass

                    obs = AtmosphericObservation(
                        station_id=stn_id,
                        timestamp=ts,
                        latitude=lat,
                        longitude=lon,
                        temperature_celsius=t_c,
                        relative_humidity_pct=rh_pct,
                        pressure_hpa=p_hpa,
                        wind_speed_kmh=w_kmh,
                        wind_direction_deg=w_deg,
                        precipitation_rate_mmh=precip_mmh,
                        quality_flag=QualityFlag.VALID,
                        metadata={
                            "station_name": row.get("NAME", "INDIRA GANDHI INTERNATIONAL"),
                            "elevation_m": float(row.get("ELEVATION", 236.8)),
                            "provenance": "PUBLIC_REAL_DATA",
                            "source": "NOAA_ISD_METAR",
                        },
                    )
                    observations.append(obs)

            return self.validate_observations(observations)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_stations = data.get("stations", [])

        observations: List[AtmosphericObservation] = []
        for stn in raw_stations:
            ts_str = stn.get("timestamp")
            ts = (
                datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts_str
                else datetime.now(timezone.utc)
            )

            obs = AtmosphericObservation(
                station_id=stn.get("id", str(stn.get("station_id", "AWS-001"))),
                timestamp=ts,
                latitude=float(stn["latitude"]),
                longitude=float(stn["longitude"]),
                temperature_celsius=float(stn["temperature_c"]) if "temperature_c" in stn else None,
                relative_humidity_pct=float(stn["humidity_pct"]) if "humidity_pct" in stn else None,
                pressure_hpa=float(stn["pressure_hpa"]) if "pressure_hpa" in stn else None,
                wind_speed_kmh=float(stn["wind_speed_kmh"]) if "wind_speed_kmh" in stn else None,
                wind_direction_deg=float(stn["wind_direction_deg"]) if "wind_direction_deg" in stn else None,
                precipitation_rate_mmh=float(stn["precipitation_rate_mmh"]) if "precipitation_rate_mmh" in stn else None,
                quality_flag=QualityFlag.VALID,
                metadata={
                    "station_name": stn.get("name", "Unknown Station"),
                    "elevation_m": stn.get("elevation_m", 215.0),
                    "is_sample": data.get("is_sample", True),
                },
            )
            observations.append(obs)

        return self.validate_observations(observations)

    def validate_observations(
        self, observations: List[AtmosphericObservation]
    ) -> List[AtmosphericObservation]:
        """Validates surface AWS variables against meteorological limits."""
        valid_list: List[AtmosphericObservation] = []
        for obs in observations:
            # Temperature: -40 to +60 C
            if obs.temperature_celsius is not None:
                if not (-40.0 <= obs.temperature_celsius <= 60.0):
                    obs.temperature_celsius = None
                    obs.quality_flag = QualityFlag.LOW_QUALITY

            # Humidity: 0 to 100%
            if obs.relative_humidity_pct is not None:
                if not (0.0 <= obs.relative_humidity_pct <= 100.0):
                    obs.relative_humidity_pct = None
                    obs.quality_flag = QualityFlag.LOW_QUALITY

            # Pressure: 700 to 1100 hPa
            if obs.pressure_hpa is not None:
                if not (700.0 <= obs.pressure_hpa <= 1100.0):
                    obs.pressure_hpa = None
                    obs.quality_flag = QualityFlag.LOW_QUALITY

            # Wind speed: 0 to 250 km/h
            if obs.wind_speed_kmh is not None:
                if not (0.0 <= obs.wind_speed_kmh <= 250.0):
                    obs.wind_speed_kmh = None
                    obs.quality_flag = QualityFlag.LOW_QUALITY

            # Coordinate bounds
            if not (-90.0 <= obs.latitude <= 90.0) or not (-180.0 <= obs.longitude <= 180.0):
                obs.quality_flag = QualityFlag.INVALID
                continue

            valid_list.append(obs)

        return valid_list
