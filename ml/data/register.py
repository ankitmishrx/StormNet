"""Dataset Registration Engine and CLI.

Registers newly supplied meteorological datasets into the STORMNET registry:
1. Inspects dataset directory or file
2. Calculates deterministic SHA-256 checksums
3. Extracts spatio-temporal metadata and file formats
4. Executes validation checks via DatasetValidator
5. Generates immutable DatasetManifest
6. Saves manifest to data/manifests/<dataset_id>.json

Strictly leaves original files untouched (does not move or delete original data).
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ml.data.manifest import (
    DatasetManifest,
    DatasetProvenance,
    compute_file_sha256,
    compute_directory_sha256,
)
from ml.data.validate import DatasetValidator


class DatasetRegistrar:
    """Registers and fingerprints datasets into the local STORMNET data catalog."""

    def __init__(self, manifests_dir: Union[str, Path] = "data/manifests"):
        self.manifests_dir = Path(manifests_dir)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)
        self.validator = DatasetValidator()

    def register_dataset(
        self,
        path: Union[str, Path],
        dataset_id: Optional[str] = None,
        source: Optional[str] = None,
        provider: Optional[str] = None,
        product: Optional[str] = None,
        provenance: Optional[str] = None,
        access_status: str = "AUTHORIZED",
        license_status: str = "IMD Academic MoU",
        processing_version: str = "v1.0",
    ) -> DatasetManifest:
        """Inspects, hashes, validates, and registers a dataset."""
        target_path = Path(path)
        if not target_path.exists():
            raise FileNotFoundError(f"Target dataset path does not exist: {target_path}")

        ds_id = dataset_id or target_path.stem.lower()

        # 1. Inspect Files
        files: List[Path] = []
        if target_path.is_file():
            files = [target_path]
        else:
            files = [f for f in sorted(target_path.rglob("*")) if f.is_file() and not f.name.startswith(".")]

        if not files:
            raise ValueError(f"No valid data files found in path: {target_path}")

        # 2. Calculate Checksums
        file_manifest: List[Dict[str, Any]] = []
        for f in files:
            file_manifest.append({
                "filename": f.name,
                "relative_path": str(f.relative_to(target_path.parent if target_path.is_file() else target_path)),
                "size_bytes": f.stat().st_size,
                "sha256": compute_file_sha256(f),
            })

        top_checksum = compute_directory_sha256(target_path)

        # 3. Detect Formats & Extent
        formats = sorted(list(set(f.suffix.lower() for f in files)))
        primary_format = formats[0].lstrip(".") if formats else "unknown"

        # Determine Provenance
        if provenance:
            prov_val = provenance
        elif "PUBLIC" in str(target_path).upper() or "external/public" in str(target_path).replace("\\", "/"):
            prov_val = DatasetProvenance.PUBLIC_REAL_DATA.value
        elif "SAMPLE" in str(target_path).upper() or "samples" in str(target_path):
            prov_val = DatasetProvenance.SAMPLE_DATA.value
        elif "SYNTHETIC" in str(target_path).upper():
            prov_val = DatasetProvenance.SYNTHETIC_DATA.value
        else:
            prov_val = DatasetProvenance.REAL_AUTHORIZED_DATA.value

        # 4. Validate Dataset Files
        val_report = self.validator.validate(ds_id, target_path, provenance=prov_val)
        val_report.save()

        # Extract timestamps and bounding coordinates from validation metrics if present
        min_ts = datetime.now(timezone.utc).isoformat()
        max_ts = min_ts
        geo_coverage = {
            "min_lat": 27.7,
            "max_lat": 29.5,
            "min_lon": 76.2,
            "max_lon": 78.2,
            "crs": "EPSG:4326",
            "path": str(target_path),
        }

        for chk in val_report.checks:
            if chk.check_name == "timestamp_validity_check" and "min_ts" in chk.metrics:
                min_ts = chk.metrics["min_ts"]
                max_ts = chk.metrics["max_ts"]
            elif chk.check_name == "geographic_bounding_check" and "min_lat" in chk.metrics:
                geo_coverage.update(chk.metrics)
            elif chk.check_name == "crs_conformity_check" and "crs" in chk.metrics:
                geo_coverage["crs"] = chk.metrics["crs"]

        total_bytes = sum(f.stat().st_size for f in files)
        variables_detected = val_report.metadata.get("variables_detected", [])

        # 5. Create Manifest
        manifest = DatasetManifest(
            dataset_id=ds_id,
            source=source or ("IMD_DWR" if "radar" in str(target_path) else ("NOAA_ISD" if "station" in str(target_path) else "METEOROLOGICAL_FEED")),
            provider=provider or ("NOAA NCEI" if "station" in str(target_path) or "noaa" in ds_id.lower() else ("IMD" if "radar" in str(target_path) else "MoES")),
            product=product or ("ISD_HOURLY" if "station" in str(target_path) else ("DWR_MAX_Z" if "radar" in str(target_path) else "COMPOSITE")),
            provenance=prov_val,
            variables=variables_detected,
            start_time=min_ts,
            end_time=max_ts,
            total_size=total_bytes,
            download_timestamp=datetime.now(timezone.utc).isoformat(),
            validation_status=val_report.overall_status,
            acquisition_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            observation_period={"start_time": min_ts, "end_time": max_ts},
            geographic_coverage=geo_coverage,
            file_count=len(files),
            checksum=top_checksum,
            format=primary_format,
            access_status=access_status,
            license_status=license_status,
            processing_version=processing_version,
            data_provenance=prov_val,
            file_manifest=file_manifest,
            metadata={
                "validation_status": val_report.overall_status,
                "validation_pass_rate_pct": val_report.pass_rate_pct,
                "original_path": str(target_path),
            },
        )

        manifest.save(self.manifests_dir)
        return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="STORMNET Dataset Registration Engine")
    parser.add_argument("--path", type=str, required=True, help="Path to dataset directory or file")
    parser.add_argument("--dataset-id", type=str, default=None, help="Unique dataset identifier")
    parser.add_argument("--source", type=str, default=None, help="Originating data source (e.g. IMD_DWR, MOSDAC_INSAT)")
    parser.add_argument("--provider", type=str, default=None, help="Operating agency (e.g. IMD, ISRO, IITM)")
    parser.add_argument("--product", type=str, default=None, help="Product name (e.g. DWR_MAX_Z, TIR1_BRIGHTNESS_TEMP)")
    parser.add_argument("--provenance", type=str, default=None, choices=[
        e.value for e in DatasetProvenance
    ], help="Data authenticity tier")
    parser.add_argument("--license", type=str, default="US Government Open Data / Public Domain", help="Data usage license")
    args = parser.parse_args()

    registrar = DatasetRegistrar()
    manifest = registrar.register_dataset(
        path=args.path,
        dataset_id=args.dataset_id,
        source=args.source,
        provider=args.provider,
        product=args.product,
        provenance=args.provenance,
        license_status=args.license,
    )

    print("==================================================")
    print("STORMNET DATASET REGISTRATION SUCCESSFUL")
    print("==================================================")
    print(f"Dataset ID   : {manifest.dataset_id}")
    print(f"Provider     : {manifest.provider}")
    print(f"Product      : {manifest.product}")
    print(f"Provenance   : {manifest.data_provenance}")
    print(f"Files        : {manifest.file_count}")
    print(f"Checksum     : {manifest.checksum[:16]}...")
    print(f"Manifest Path: data/manifests/{manifest.dataset_id}.json")
    print("Original files remained untouched.")
    print("==================================================")
