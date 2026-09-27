"""Radar Station Registry providing verified physical metadata for Indian DWR networks."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


@dataclass(frozen=True)
class RadarStation:
    """Immutable metadata container for an operational Doppler Weather Radar station."""
    id: str
    station_name: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
    altitude_m: float
    frequency_band: str
    frequency_ghz: float
    wavelength_cm: float
    beamwidth_deg: float
    max_range_km: float
    operational_agency: str
    hardware_manufacturer: str
    native_format: str
    grid_extent_wgs84: Dict[str, float]
    elevation_angles_deg: List[float] = field(default_factory=list)

    @property
    def coordinates(self) -> tuple[float, float]:
        """Returns (latitude, longitude)."""
        return self.latitude, self.longitude


class RadarStationRegistry:
    """Registry loading and serving verified radar station configurations."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join("config", "radar_stations.yaml")
        self.config_path = Path(config_path)
        self._stations: Dict[str, RadarStation] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        if not self.config_path.exists():
            # Fallback to hardcoded verified specifications if yaml is missing
            self._load_fallback_defaults()
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for s_data in data.get("stations", []):
            station = RadarStation(
                id=s_data["id"],
                station_name=s_data["station_name"],
                city=s_data["city"],
                state=s_data["state"],
                country=s_data["country"],
                latitude=float(s_data["latitude"]),
                longitude=float(s_data["longitude"]),
                altitude_m=float(s_data["altitude_m"]),
                frequency_band=s_data["frequency_band"],
                frequency_ghz=float(s_data["frequency_ghz"]),
                wavelength_cm=float(s_data["wavelength_cm"]),
                beamwidth_deg=float(s_data["beamwidth_deg"]),
                max_range_km=float(s_data["max_range_km"]),
                operational_agency=s_data["operational_agency"],
                hardware_manufacturer=s_data["hardware_manufacturer"],
                native_format=s_data["native_format"],
                grid_extent_wgs84=s_data["grid_extent_wgs84"],
                elevation_angles_deg=s_data.get("elevation_angles_deg", []),
            )
            self._stations[station.id] = station

    def _load_fallback_defaults(self) -> None:
        defaults = [
            RadarStation(
                id="DWR-DEL-SAF",
                station_name="New Delhi Safdarjung Doppler Weather Radar",
                city="New Delhi",
                state="Delhi",
                country="India",
                latitude=28.5894,
                longitude=77.2173,
                altitude_m=216.0,
                frequency_band="S-Band",
                frequency_ghz=2.8,
                wavelength_cm=10.7,
                beamwidth_deg=1.0,
                max_range_km=250.0,
                operational_agency="India Meteorological Department (IMD)",
                hardware_manufacturer="Bharat Electronics Limited (BEL)",
                native_format="ODIM_H5",
                grid_extent_wgs84={"min_lat": 27.7, "max_lat": 29.5, "min_lon": 76.2, "max_lon": 78.2},
                elevation_angles_deg=[0.5, 1.0, 1.5, 2.2, 3.0, 4.5, 6.0, 9.0, 12.0, 16.0, 21.0],
            ),
            RadarStation(
                id="DWR-MUM-VER",
                station_name="Mumbai Veravali Doppler Weather Radar",
                city="Mumbai",
                state="Maharashtra",
                country="India",
                latitude=19.1242,
                longitude=72.8661,
                altitude_m=85.0,
                frequency_band="S-Band",
                frequency_ghz=2.8,
                wavelength_cm=10.7,
                beamwidth_deg=1.0,
                max_range_km=250.0,
                operational_agency="India Meteorological Department (IMD)",
                hardware_manufacturer="Bharat Electronics Limited (BEL)",
                native_format="ODIM_H5",
                grid_extent_wgs84={"min_lat": 18.0, "max_lat": 20.2, "min_lon": 71.8, "max_lon": 73.9},
                elevation_angles_deg=[0.5, 1.0, 1.5, 2.2, 3.0, 4.5, 6.0, 9.0, 12.0, 16.0, 21.0],
            ),
            RadarStation(
                id="DWR-CHE-PRT",
                station_name="Chennai Port Trust Cyclone Detection Radar",
                city="Chennai",
                state="Tamil Nadu",
                country="India",
                latitude=13.0844,
                longitude=80.2982,
                altitude_m=16.0,
                frequency_band="S-Band",
                frequency_ghz=2.8,
                wavelength_cm=10.7,
                beamwidth_deg=1.0,
                max_range_km=250.0,
                operational_agency="India Meteorological Department (IMD)",
                hardware_manufacturer="ISRO / BEL Indigenous Radar",
                native_format="ODIM_H5",
                grid_extent_wgs84={"min_lat": 11.9, "max_lat": 14.2, "min_lon": 79.2, "max_lon": 81.4},
                elevation_angles_deg=[0.5, 1.0, 1.5, 2.2, 3.0, 4.5, 6.0, 9.0, 12.0, 16.0, 21.0],
            ),
            RadarStation(
                id="DWR-KOL-SUB",
                station_name="Kolkata NSCB International Airport Radar",
                city="Kolkata",
                state="West Bengal",
                country="India",
                latitude=22.6542,
                longitude=88.4467,
                altitude_m=10.0,
                frequency_band="S-Band",
                frequency_ghz=2.8,
                wavelength_cm=10.7,
                beamwidth_deg=1.0,
                max_range_km=250.0,
                operational_agency="India Meteorological Department (IMD)",
                hardware_manufacturer="Bharat Electronics Limited (BEL)",
                native_format="ODIM_H5",
                grid_extent_wgs84={"min_lat": 21.5, "max_lat": 23.8, "min_lon": 87.3, "max_lon": 89.6},
                elevation_angles_deg=[0.5, 1.0, 1.5, 2.2, 3.0, 4.5, 6.0, 9.0, 12.0, 16.0, 21.0],
            ),
        ]
        for s in defaults:
            self._stations[s.id] = s

    def get_station(self, station_id: str) -> Optional[RadarStation]:
        """Retrieves station metadata by ID (e.g. 'DWR-DEL-SAF')."""
        return self._stations.get(station_id)

    def list_stations(self) -> List[RadarStation]:
        """Returns all configured stations."""
        return list(self._stations.values())

    def list_station_ids(self) -> List[str]:
        return list(self._stations.keys())


# Singleton registry instance
_default_registry: Optional[RadarStationRegistry] = None


def get_station_registry() -> RadarStationRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = RadarStationRegistry()
    return _default_registry
