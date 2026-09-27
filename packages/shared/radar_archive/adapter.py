"""Historical Radar Archive Adapter for multi-year multi-station indexing and ingestion."""

import os
import re
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator

from packages.shared.radar_archive.stations import RadarStation, get_station_registry

logger = logging.getLogger(__name__)


@dataclass
class ArchiveFrameRecord:
    """Standardized catalog entry for an archived radar scan."""
    station_id: str
    timestamp: datetime
    file_path: str
    file_format: str
    product_type: str
    resolution_km: float
    file_size_bytes: int
    is_valid: bool
    qc_status: str  # "VALID", "CORRUPT", "DUPLICATE", "MISSING_METADATA", "OUT_OF_BOUNDS"
    error_details: Optional[str] = None
    max_dbz: Optional[float] = None


class HistoricalRadarArchiveAdapter:
    """Discovers, validates, indexes, and catalogs multi-year historical radar volumes."""

    # Regex patterns for timestamp extraction from standard WMO / IRIS filenames
    # Example: DWR_DEL_20240715_143000.h5 or dwr_delhi_20260926_1545.json
    TS_PATTERNS = [
        re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})"),  # YYYYMMDD_HHMMSS
        re.compile(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})"),          # YYYYMMDD_HHMM
        re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2})_(\d{2})_(\d{2})"), # YYYY-MM-DDTHH_MM_SS
    ]

    def __init__(self, archive_root_dir: Optional[str] = None):
        self.archive_root = Path(archive_root_dir or os.path.join("data", "raw", "radar_archive"))
        self.station_registry = get_station_registry()
        self._catalog: List[ArchiveFrameRecord] = []

    def parse_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """Extracts UTC observation timestamp from standardized filename conventions."""
        for pattern in self.TS_PATTERNS:
            match = pattern.search(filename)
            if match:
                parts = [int(p) for p in match.groups()]
                if len(parts) == 6:
                    return datetime(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], tzinfo=timezone.utc)
                elif len(parts) == 5:
                    return datetime(parts[0], parts[1], parts[2], parts[3], parts[4], 0, tzinfo=timezone.utc)
        return None

    def scan_station_archive(
        self,
        station_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        station_subpath: Optional[str] = None,
    ) -> List[ArchiveFrameRecord]:
        """Scans archive directory tree for a specific radar station."""
        station = self.station_registry.get_station(station_id)
        if station is None:
            raise ValueError(f"Unknown radar station ID: {station_id}")

        target_dir = Path(station_subpath) if station_subpath else self.archive_root / station_id
        records: List[ArchiveFrameRecord] = []
        seen_timestamps: set[datetime] = set()

        if not target_dir.exists():
            logger.warning(f"Archive directory does not exist for station {station_id}: {target_dir}")
            return records

        for file_path in target_dir.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() not in [".h5", ".nc", ".json", ".raw", ".bufr"]:
                continue

            # File format detection
            suffix = file_path.suffix.lower()
            file_format = "ODIM_H5" if suffix == ".h5" else "NETCDF4" if suffix == ".nc" else "JSON" if suffix == ".json" else "UNKNOWN"
            file_size = file_path.stat().st_size

            # Empty file check
            if file_size == 0:
                records.append(
                    ArchiveFrameRecord(
                        station_id=station_id,
                        timestamp=datetime(1970, 1, 1, tzinfo=timezone.utc),
                        file_path=str(file_path),
                        file_format=file_format,
                        product_type="MAX_Z",
                        resolution_km=3.0,
                        file_size_bytes=0,
                        is_valid=False,
                        qc_status="CORRUPT",
                        error_details="Zero-byte corrupted file",
                    )
                )
                continue

            # Timestamp parsing
            ts = self.parse_timestamp_from_filename(file_path.name)
            if ts is None:
                # Attempt to read timestamp from internal JSON header
                if file_format == "JSON":
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = json.load(f)
                        raw_ts = content.get("timestamp")
                        if raw_ts:
                            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                    except Exception as e:
                        pass

            if ts is None:
                records.append(
                    ArchiveFrameRecord(
                        station_id=station_id,
                        timestamp=datetime(1970, 1, 1, tzinfo=timezone.utc),
                        file_path=str(file_path),
                        file_format=file_format,
                        product_type="MAX_Z",
                        resolution_km=3.0,
                        file_size_bytes=file_size,
                        is_valid=False,
                        qc_status="INVALID_TIMESTAMP",
                        error_details="Could not parse timestamp from filename or metadata header",
                    )
                )
                continue

            # Temporal filtering
            if start_date and ts < start_date:
                continue
            if end_date and ts > end_date:
                continue

            # Duplicate timestamp check
            if ts in seen_timestamps:
                records.append(
                    ArchiveFrameRecord(
                        station_id=station_id,
                        timestamp=ts,
                        file_path=str(file_path),
                        file_format=file_format,
                        product_type="MAX_Z",
                        resolution_km=3.0,
                        file_size_bytes=file_size,
                        is_valid=False,
                        qc_status="DUPLICATE",
                        error_details="Duplicate observation scan timestamp detected",
                    )
                )
                continue

            seen_timestamps.add(ts)

            # Record clean valid scan
            records.append(
                ArchiveFrameRecord(
                    station_id=station_id,
                    timestamp=ts,
                    file_path=str(file_path),
                    file_format=file_format,
                    product_type="MAX_Z",
                    resolution_km=3.0,
                    file_size_bytes=file_size,
                    is_valid=True,
                    qc_status="VALID",
                    error_details=None,
                )
            )

        # Sort chronologically
        records.sort(key=lambda r: r.timestamp)
        self._catalog.extend(records)
        return records

    def export_index_catalog(self, output_path: str) -> None:
        """Exports the in-memory archive index to JSON format."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(r) for r in self._catalog]
        # Serialize datetimes to ISO format
        for item in data:
            if isinstance(item["timestamp"], datetime):
                item["timestamp"] = item["timestamp"].isoformat()

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Archive index with {len(data)} entries exported to {output_path}")

    @property
    def catalog(self) -> List[ArchiveFrameRecord]:
        return self._catalog
