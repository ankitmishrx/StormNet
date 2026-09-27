"""Radar Data Ingestion CLI & Service Pipeline for STORMNET.

Usage:
    python -m ml.preprocessing.radar.ingest <file_path> [--grid-size 3] [--sector delhi-ncr]
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
import numpy as np

from ml.preprocessing.radar.interfaces import RadarFrame, RadarObservation
from ml.preprocessing.radar.validator import RadarValidator, RadarValidationError
from ml.preprocessing.radar.processors import ReflectivityProcessor
from ml.preprocessing.radar.grid import CommonGridGenerator
from ml.preprocessing.radar.georeference import create_bbox_polygon


def parse_radar_file(file_path: str) -> Dict[str, Any]:
    """Reads and parses raw radar input file (JSON / ODIM / NetCDF)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Radar input file not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    else:
        raise RadarValidationError(f"Unsupported radar format '{ext}'. Supported in Phase 4: [.json, .geojson].")


def process_radar_ingestion(
    file_path: str,
    target_grid_km: float = 3.0,
    sector_id: str = "delhi-ncr",
) -> Dict[str, Any]:
    """Executes the full radar ingestion, validation, gridding, and PostGIS storage pipeline."""
    # 1. Read input
    raw_payload = parse_radar_file(file_path)

    # 2. Extract and validate metadata
    radar_id = raw_payload.get("radar_id", "DWR-UNKNOWN")
    ts_str = raw_payload.get("timestamp")
    if not ts_str:
        raise RadarValidationError("Missing required 'timestamp' field in radar metadata.")

    # Parse ISO timestamp
    if ts_str.endswith("Z"):
        ts_clean = ts_str[:-1] + "+00:00"
    else:
        ts_clean = ts_str
    observation_time = datetime.fromisoformat(ts_clean)
    is_sample = "SAMPLE" in raw_payload.get("source", "").upper()
    RadarValidator.validate_timestamp(observation_time, is_sample=is_sample)

    # 3. Validate coordinates and bounding box
    antenna_lat = float(raw_payload.get("antenna_lat", 28.5847))
    antenna_lon = float(raw_payload.get("antenna_lon", 77.2069))
    RadarValidator.validate_coordinates(antenna_lat, antenna_lon)

    raw_bbox = raw_payload.get("bounding_box", [76.50, 28.00, 77.80, 29.20])
    bbox_tuple: Tuple[float, float, float, float] = (
        float(raw_bbox[0]), float(raw_bbox[1]), float(raw_bbox[2]), float(raw_bbox[3])
    )
    RadarValidator.validate_bounding_box(bbox_tuple)

    source_resolution_km = float(raw_payload.get("source_resolution_km", 0.5))

    # 4. Generate Target Common Grid
    grid_gen = CommonGridGenerator(grid_size_km=target_grid_km, bbox=bbox_tuple, sector_id=sector_id)
    n_lats, n_lons = grid_gen.get_grid_dimensions()
    lats_mesh, lons_mesh = grid_gen.get_lat_lon_mesh()

    # Populate 2D grid from cell points
    grid_matrix = np.zeros((n_lats, n_lons), dtype=np.float32)
    raw_cells: List[Dict[str, Any]] = raw_payload.get("cells", [])

    cells_processed = 0
    invalid_cells = 0
    observations_list: List[RadarObservation] = []

    for c in raw_cells:
        lat = float(c.get("lat", 0.0))
        lon = float(c.get("lon", 0.0))
        dbz = float(c.get("reflectivity_dbz", 0.0))

        # Check physical bounds
        if dbz < RadarValidator.MIN_VALID_DBZ or dbz > RadarValidator.MAX_VALID_DBZ:
            invalid_cells += 1
            continue

        # Find closest grid indices
        j = int(np.argmin(np.abs(lats_mesh - lat)))
        i = int(np.argmin(np.abs(lons_mesh - lon)))

        if 0 <= j < n_lats and 0 <= i < n_lons:
            grid_matrix[j, i] = max(grid_matrix[j, i], dbz)
            cells_processed += 1
            observations_list.append(
                RadarObservation(
                    latitude=lat,
                    longitude=lon,
                    reflectivity_dbz=dbz,
                    timestamp=observation_time,
                    quality_flag=c.get("quality_flag", "VALID"),
                )
            )

    # 5. Filter Clutter & Validate Gridded Field
    cleaned_grid = ReflectivityProcessor.filter_ground_clutter(grid_matrix)
    health = RadarValidator.validate_reflectivity_grid(cleaned_grid)

    # 6. Extract Vector Contours for Lightweight GIS Serving
    vector_contours = ReflectivityProcessor.extract_reflectivity_contours(
        cleaned_grid, lats_mesh, lons_mesh, dbz_levels=[20, 35, 45, 55, 60]
    )

    frame_id = str(uuid.uuid4())
    stored_in_db = False

    # 7. Store in PostGIS if available
    try:
        from apps.api.core.database import SessionLocal
        from apps.api.models.radar_frame import RadarFrameModel
        from apps.api.models.radar_observation import RadarObservationModel

        session = SessionLocal()
        try:
            bbox_poly = create_bbox_polygon(*bbox_tuple)
            frame_record = RadarFrameModel(
                id=uuid.UUID(frame_id),
                radar_id=radar_id,
                source=raw_payload.get("source", "DEVELOPMENT_SAMPLE"),
                timestamp=observation_time,
                product_type=raw_payload.get("product_type", "COMPOSITE_REFLECTIVITY"),
                resolution_km=target_grid_km,
                source_resolution_km=source_resolution_km,
                crs="EPSG:4326",
                bounding_box=list(bbox_tuple),
                status="SAMPLE" if "SAMPLE" in raw_payload.get("source", "") else "VALIDATED",
                total_cells_processed=cells_processed,
                max_dbz=health["max_dbz"],
            )
            session.add(frame_record)

            for obs in observations_list[:500]:  # Limit top cell observations
                obs_record = RadarObservationModel(
                    frame_id=uuid.UUID(frame_id),
                    grid_cell_id=f"{sector_id[:3].upper()}-{int(target_grid_km)}KM",
                    timestamp=obs.timestamp,
                    latitude=obs.latitude,
                    longitude=obs.longitude,
                    reflectivity=obs.reflectivity_dbz,
                    quality_flag=obs.quality_flag,
                )
                session.add(obs_record)

            session.commit()
            stored_in_db = True
        except Exception as db_err:
            session.rollback()
            # Offline database fallback
            stored_in_db = False
        finally:
            session.close()
    except ImportError:
        stored_in_db = False

    summary = {
        "frame_id": frame_id,
        "radar_id": radar_id,
        "station_name": raw_payload.get("station_name", "Safdarjung DWR"),
        "source": raw_payload.get("source", "DEVELOPMENT_SAMPLE"),
        "timestamp": observation_time.isoformat(),
        "input_resolution_km": source_resolution_km,
        "target_grid_km": target_grid_km,
        "grid_dimensions": f"{n_lats} x {n_lons} cells",
        "cells_processed": cells_processed,
        "invalid_cells": invalid_cells,
        "max_reflectivity_dbz": health["max_dbz"],
        "min_reflectivity_dbz": health["min_dbz"],
        "mean_reflectivity_dbz": health["mean_dbz"],
        "vector_contour_levels": len(vector_contours),
        "stored_in_postgis": stored_in_db,
        "vector_contours": vector_contours,
    }

    return summary


def main():
    parser = argparse.ArgumentParser(description="STORMNET Radar Ingestion Pipeline")
    parser.add_argument("file_path", type=str, help="Path to input radar file (.json, .geojson, .h5)")
    parser.add_argument("--grid-size", type=float, default=3.0, choices=[1.0, 2.0, 3.0], help="Target common grid resolution in km")
    parser.add_argument("--sector", type=str, default="delhi-ncr", help="Forecast sector identifier")

    args = parser.parse_args()

    try:
        result = process_radar_ingestion(
            file_path=args.file_path,
            target_grid_km=args.grid_size,
            sector_id=args.sector,
        )

        print("\n==================================================")
        print("RADAR INGESTION COMPLETED")
        print("==================================================")
        print(f"Frame ID:           {result['frame_id']}")
        print(f"Radar ID:           {result['radar_id']} ({result['station_name']})")
        print(f"Source:             {result['source']}")
        print(f"Timestamp:          {result['timestamp']}")
        print(f"Input Resolution:   {result['input_resolution_km']} km")
        print(f"Target Grid:        {result['target_grid_km']} km ({result['grid_dimensions']})")
        print(f"Cells Processed:    {result['cells_processed']}")
        print(f"Invalid Cells:      {result['invalid_cells']}")
        print(f"Max Reflectivity:   {result['max_reflectivity_dbz']} dBZ")
        print(f"Contour Levels:     {result['vector_contour_levels']}")
        print(f"Stored in PostGIS:  {result['stored_in_postgis']}")
        print("==================================================\n")

    except Exception as e:
        print(f"\n[ERROR] Radar Ingestion Failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
