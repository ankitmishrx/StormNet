"""MOSDAC / INSAT Satellite Data Provider Adapter.

Specialized adapter for ISRO SAC / MOSDAC geostationary meteorological products (INSAT-3D, INSAT-3DR, INSAT-3DS).
Supports:
- Infrared/Thermal imagery (TIR1, TIR2, MIR, WV)
- Cloud-related products (Cloud Top Temperature [CTT], Cloud Top Pressure [CTP])
- Quantitative Precipitation Estimation (Hydro-Estimator Method [HEM], IMSRA)
- Cloud-Motion Vectors (CMV)

Does not assume every product is available simultaneously. Consumes authorized downloaded files.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


@dataclass
class INSATFrame:
    """Standardized representation of an ingested INSAT satellite frame."""
    satellite_id: str
    product_type: str
    timestamp: datetime
    sector_id: str
    data_provenance: str  # REAL_AUTHORIZED_DATA, HISTORICAL_DATA, SAMPLE_DATA, SYNTHETIC_DATA
    quality_status: str   # VALIDATED, DEGRADED, SAMPLE, MISSING
    spatial_resolution_km: float = 4.0
    brightness_temp_k: Optional[np.ndarray] = None
    cloud_top_temp_k: Optional[np.ndarray] = None
    cloud_cooling_rate_k_hr: Optional[np.ndarray] = None
    rainfall_rate_mmh: Optional[np.ndarray] = None
    motion_vectors: Optional[Dict[str, np.ndarray]] = None
    observations: List[Dict[str, Any]] = field(default_factory=list)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)


class INSATAdapter:
    """Ingests and standardizes authorized MOSDAC INSAT products."""

    def __init__(self, target_grid_dim: int = 64):
        self.target_grid_dim = target_grid_dim

    def load_insat_file(
        self,
        filepath: Union[str, Path],
        default_provenance: Optional[str] = None,
    ) -> INSATFrame:
        """Loads and standardizes an INSAT product file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"INSAT file does not exist: {path}")

        suffix = path.suffix.lower()

        if suffix in [".json", ".geojson"]:
            return self._load_json(path, default_provenance)
        elif suffix in [".h5", ".hdf5"]:
            return self._load_hdf5(path, default_provenance)
        elif suffix in [".nc", ".netcdf"]:
            return self._load_netcdf(path, default_provenance)
        else:
            raise ValueError(
                f"Unsupported INSAT file format: '{suffix}'. "
                f"Supported formats: .h5 (MOSDAC HDF5), .nc (NetCDF4), .json (Sample schema)"
            )

    def _load_json(self, path: Path, default_provenance: Optional[str]) -> INSATFrame:
        """Parses standardized JSON INSAT frame."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        satellite_id = data.get("satellite_id", "INSAT-3DR")
        raw_source = data.get("source", "DEVELOPMENT_SAMPLE")

        if default_provenance:
            provenance = default_provenance
        elif "SAMPLE" in raw_source.upper() or data.get("is_sample", False):
            provenance = "SAMPLE_DATA"
        elif "SYNTHETIC" in raw_source.upper():
            provenance = "SYNTHETIC_DATA"
        else:
            provenance = "REAL_AUTHORIZED_DATA"

        raw_ts = data.get("timestamp")
        if isinstance(raw_ts, str):
            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            ts = datetime.now(timezone.utc)

        observations = data.get("observations", [])
        grid_bt = np.full((self.target_grid_dim, self.target_grid_dim), 285.0, dtype=np.float32)
        grid_ctt = np.full((self.target_grid_dim, self.target_grid_dim), 280.0, dtype=np.float32)
        grid_cooling = np.zeros((self.target_grid_dim, self.target_grid_dim), dtype=np.float32)

        # Place point observations on grid
        for obs in observations:
            lat = obs.get("latitude", 28.5)
            lon = obs.get("longitude", 77.2)
            bt = obs.get("brightness_temp_kelvin", 240.0)
            ctt = obs.get("cloud_top_temp_kelvin", bt - 3.0)
            cooling = obs.get("cooling_rate_kelvin_per_hour", 0.0)

            # Map lat/lon to grid indices roughly for NCR sector
            gx = int(np.clip((lon - 76.5) / 1.3 * self.target_grid_dim, 0, self.target_grid_dim - 1))
            gy = int(np.clip((lat - 28.0) / 1.2 * self.target_grid_dim, 0, self.target_grid_dim - 1))

            grid_bt[gy, gx] = bt
            grid_ctt[gy, gx] = ctt
            grid_cooling[gy, gx] = cooling

        product_type = data.get("channel", "TIR1_10.8UM")

        return INSATFrame(
            satellite_id=satellite_id,
            product_type=product_type,
            timestamp=ts,
            sector_id=data.get("sector_id", "delhi-ncr"),
            data_provenance=provenance,
            quality_status="SAMPLE" if provenance == "SAMPLE_DATA" else "VALIDATED",
            spatial_resolution_km=4.0,
            brightness_temp_k=grid_bt,
            cloud_top_temp_k=grid_ctt,
            cloud_cooling_rate_k_hr=grid_cooling,
            observations=observations,
            raw_metadata=data,
        )

    def _load_hdf5(self, path: Path, default_provenance: Optional[str]) -> INSATFrame:
        """Parses MOSDAC HDF5 format (e.g. 3RIMG_..._L1B_STD.h5)."""
        try:
            import h5py  # type: ignore
        except ImportError:
            raise ImportError(
                "h5py is required to decode MOSDAC HDF5 satellite products. "
                "Install via 'pip install h5py' in the environment."
            )

        provenance = default_provenance or "REAL_AUTHORIZED_DATA"

        with h5py.File(path, "r") as h5:
            # Extract header attributes
            sat_id = "INSAT-3DR"
            if "Satellite_Name" in h5.attrs:
                sat_attr = h5.attrs["Satellite_Name"]
                sat_id = sat_attr.decode("utf-8") if isinstance(sat_attr, bytes) else str(sat_attr)

            ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if "Acquisition_Time" in h5.attrs:
                try:
                    time_raw = h5.attrs["Acquisition_Time"]
                    time_str = time_raw.decode("utf-8") if isinstance(time_raw, bytes) else str(time_raw)
                    ts = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                except Exception:
                    pass

            product_type = "MOSDAC_HDF5"
            grid_bt = None
            grid_qpe = None

            # Detect channels present
            if "IMG_TIR1" in h5:
                raw_tir1 = np.array(h5["IMG_TIR1"][:self.target_grid_dim, :self.target_grid_dim], dtype=np.float32)
                grid_bt = raw_tir1
                product_type = "TIR1"
            elif "HEM" in h5:
                raw_hem = np.array(h5["HEM"][:self.target_grid_dim, :self.target_grid_dim], dtype=np.float32)
                grid_qpe = raw_hem
                product_type = "HEM_QPE"

            return INSATFrame(
                satellite_id=sat_id,
                product_type=product_type,
                timestamp=ts,
                sector_id="indian-subcontinent",
                data_provenance=provenance,
                quality_status="VALIDATED",
                spatial_resolution_km=4.0,
                brightness_temp_k=grid_bt,
                rainfall_rate_mmh=grid_qpe,
                raw_metadata={"file": str(path)},
            )

    def _load_netcdf(self, path: Path, default_provenance: Optional[str]) -> INSATFrame:
        """Parses NetCDF4 satellite format."""
        try:
            import netCDF4  # type: ignore
        except ImportError:
            raise ImportError(
                "netCDF4 is required to decode NetCDF satellite products. "
                "Install via 'pip install netCDF4' in the environment."
            )

        provenance = default_provenance or "REAL_AUTHORIZED_DATA"

        with netCDF4.Dataset(path, "r") as nc:
            sat_id = getattr(nc, "satellite_name", "INSAT-3DR")
            ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

            return INSATFrame(
                satellite_id=sat_id,
                product_type="NETCDF_SATELLITE",
                timestamp=ts,
                sector_id="regional",
                data_provenance=provenance,
                quality_status="VALIDATED",
                spatial_resolution_km=4.0,
                raw_metadata={"file": str(path)},
            )
