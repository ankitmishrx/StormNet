"""STORMNET Dataset Manifest & Provenance System.

Provides immutable metadata tracking, SHA-256 integrity verification, and data classification
for all observational, open public, and development datasets ingested into STORMNET.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class DatasetProvenance(str, Enum):
    """Rigorous classification of dataset authenticity and provenance."""
    PUBLIC_REAL_DATA = "PUBLIC_REAL_DATA"
    AUTHORIZED_IMD_DATA = "AUTHORIZED_IMD_DATA"
    AUTHORIZED_MOSDAC_DATA = "AUTHORIZED_MOSDAC_DATA"
    SAMPLE_DATA = "SAMPLE_DATA"
    SYNTHETIC_DATA = "SYNTHETIC_DATA"
    REPLAY_DATA = "REPLAY_DATA"

    # Backward compatibility aliases
    REAL_AUTHORIZED_DATA = "REAL_AUTHORIZED_DATA"
    HISTORICAL_DATA = "HISTORICAL_DATA"


def compute_file_sha256(filepath: Union[str, Path]) -> str:
    """Computes the hex SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_directory_sha256(directory_path: Union[str, Path]) -> str:
    """Computes a combined SHA-256 hash across all files in a directory deterministically."""
    path = Path(directory_path)
    if not path.is_dir():
        return compute_file_sha256(path)

    all_hashes = []
    for file in sorted(path.rglob("*")):
        if file.is_file() and not file.name.startswith("."):
            all_hashes.append(f"{file.name}:{compute_file_sha256(file)}")

    if not all_hashes:
        return hashlib.sha256(b"empty_directory").hexdigest()

    combined = "\n".join(all_hashes).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


@dataclass
class DatasetManifest:
    """Standardized manifest recording provenance, integrity, and parameters of an ingested dataset."""
    dataset_id: str
    provider: str
    product: str
    source_url: str = ""
    access_method: str = "DOWNLOAD"
    license: str = ""
    provenance: str = DatasetProvenance.SAMPLE_DATA.value
    variables: List[str] = field(default_factory=list)
    spatial_resolution: str = "3.0 km"
    temporal_resolution: str = "15 min"
    start_time: str = ""
    end_time: str = ""
    geographic_coverage: Dict[str, Any] = field(default_factory=dict)
    file_count: int = 0
    total_size: int = 0
    checksum: str = ""  # SHA-256 hash
    download_timestamp: str = ""
    validation_status: str = "PENDING"

    # Backward compatible fields
    source: str = ""
    acquisition_date: str = ""
    observation_period: Dict[str, str] = field(default_factory=dict)
    format: str = "json"
    access_status: str = "AUTHORIZED"
    license_status: str = ""
    processing_version: str = "v1.0"
    data_provenance: str = ""
    file_manifest: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Sync forward and backward compatible fields
        if not self.data_provenance:
            self.data_provenance = self.provenance
        if not self.provenance:
            self.provenance = self.data_provenance
        if not self.license_status and self.license:
            self.license_status = self.license
        if not self.license and self.license_status:
            self.license = self.license_status
        if not self.source:
            self.source = f"{self.provider}_{self.product}"
        if not self.start_time and self.observation_period:
            self.start_time = self.observation_period.get("start_time", "")
            self.end_time = self.observation_period.get("end_time", "")
        elif self.start_time and not self.observation_period:
            self.observation_period = {"start_time": self.start_time, "end_time": self.end_time}
        if not self.download_timestamp:
            self.download_timestamp = self.acquisition_date or datetime.now(timezone.utc).isoformat()
        if not self.acquisition_date:
            self.acquisition_date = self.download_timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Converts manifest to standard dictionary."""
        return asdict(self)

    def save(self, manifests_dir: Union[str, Path] = "data/manifests") -> Path:
        """Saves the manifest JSON into the designated manifests directory."""
        dir_path = Path(manifests_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        target_path = dir_path / f"{self.dataset_id}.json"

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        return target_path

    @classmethod
    def load(cls, manifest_path: Union[str, Path]) -> "DatasetManifest":
        """Loads and instantiates a DatasetManifest from a JSON file."""
        path = Path(manifest_path)
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)
