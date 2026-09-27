"""Feature Dataset Exporter: Serializes FusedGridFrames to Parquet and metadata sidecars."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from ml.preprocessing.fusion.interfaces import FusedGridFrame


class FeatureDatasetExporter:
    """Exports multi-source fused grid observations to Parquet scientific datasets."""

    def __init__(self, output_base_dir: str = "data/processed/fused"):
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def export_frame(
        self, frame: FusedGridFrame, format_type: str = "parquet"
    ) -> Dict[str, Any]:
        """Serializes a FusedGridFrame into partitioned directory structure."""
        ts_str = frame.timestamp.strftime("%Y%m%d_%H%M%S")
        date_partition = frame.timestamp.strftime("%Y%m%d")

        partition_dir = self.output_base_dir / f"date={date_partition}" / f"sector={frame.sector_id}"
        partition_dir.mkdir(parents=True, exist_ok=True)

        # Prepare tabular records
        records: List[Dict[str, Any]] = []
        for cell in frame.cells:
            records.append({
                "frame_id": str(frame.id),
                "grid_id": cell.grid_id,
                "timestamp": cell.timestamp.isoformat(),
                "latitude": cell.latitude,
                "longitude": cell.longitude,
                "grid_size_km": cell.grid_size_km,
                "radar_reflectivity_dbz": cell.radar_reflectivity_dbz,
                "radar_max_dbz": cell.radar_max_dbz,
                "radar_precip_rate_mm_hr": cell.radar_precip_rate_mm_hr,
                "radar_quality": cell.radar_quality.value,
                "satellite_brightness_temp_k": cell.satellite_brightness_temp_k,
                "satellite_cloud_cooling_rate_k_hr": cell.satellite_cloud_cooling_rate_k_hr,
                "satellite_quality": cell.satellite_quality.value,
                "lightning_strike_count": cell.lightning_strike_count,
                "lightning_density_per_km2": cell.lightning_density_per_km2,
                "lightning_rate_per_min": cell.lightning_rate_per_min,
                "lightning_trend": cell.lightning_trend,
                "lightning_quality": cell.lightning_quality.value,
                "atmospheric_temp_c": cell.atmospheric_temp_c,
                "atmospheric_humidity_pct": cell.atmospheric_humidity_pct,
                "atmospheric_pressure_hpa": cell.atmospheric_pressure_hpa,
                "atmospheric_wind_speed_kmh": cell.atmospheric_wind_speed_kmh,
                "atmospheric_quality": cell.atmospheric_quality.value,
                "composite_quality": cell.composite_quality.value,
            })

        data_file = partition_dir / f"fused_features_{ts_str}.parquet"
        metadata_file = partition_dir / f"fused_features_{ts_str}_meta.json"

        exported_format = "parquet"
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.Table.from_pylist(records)
            pq.write_table(table, data_file, compression="SNAPPY")
        except ImportError:
            # Fallback to JSON if pyarrow is unavailable
            data_file = partition_dir / f"fused_features_{ts_str}.json"
            exported_format = "json"
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)

        # Write sidecar metadata manifest
        sidecar_meta = {
            "fused_frame_id": str(frame.id),
            "timestamp": frame.timestamp.isoformat(),
            "sector_id": frame.sector_id,
            "resolution_km": frame.resolution_km,
            "record_count": len(records),
            "data_file": str(data_file),
            "format": exported_format,
            "sensor_availability": {
                "radar": frame.radar_available,
                "satellite": frame.satellite_available,
                "lightning": frame.lightning_available,
                "atmospheric": frame.atmospheric_available,
            },
            "completeness_score": frame.completeness_score,
            "lineage": frame.lineage_metadata,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(sidecar_meta, f, indent=2)

        return sidecar_meta
