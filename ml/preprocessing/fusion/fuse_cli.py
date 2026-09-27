"""Command Line Interface for Multi-Source Meteorological Data Fusion."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ml.preprocessing.fusion import (
    SatelliteAdapter,
    LightningAdapter,
    AtmosphericAdapter,
    MultiSourceFusionEngine,
    FeatureDatasetExporter,
)
from ml.preprocessing.radar.ingest import process_radar_ingestion
from ml.preprocessing.radar.grid import CommonGridGenerator


def run_multi_source_fusion(
    radar_file: str,
    satellite_file: Optional[str] = None,
    lightning_file: Optional[str] = None,
    aws_file: Optional[str] = None,
    grid_size_km: float = 3.0,
    output_dir: str = "data/processed/fused",
) -> None:
    """Executes end-to-end multi-source meteorological fusion pipeline."""
    print("==================================================")
    print("STORMNET MULTI-SOURCE METEOROLOGICAL DATA FUSION")
    print("==================================================")
    print(f"Target Common Grid : {grid_size_km} km")
    print(f"Output Directory   : {output_dir}")

    # 1. Process Radar Data
    print(f"\n[1/5] Ingesting Radar : {radar_file}")
    from ml.preprocessing.radar.ingest import parse_radar_file
    raw_radar = parse_radar_file(radar_file)
    radar_result = process_radar_ingestion(radar_file, target_grid_km=grid_size_km)

    ts_str = radar_result["timestamp"]
    anchor_timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    raw_bbox = raw_radar.get("bounding_box", [76.5, 28.0, 77.8, 29.2])
    bbox = (float(raw_bbox[0]), float(raw_bbox[1]), float(raw_bbox[2]), float(raw_bbox[3]))

    # Generate grid cells from bounding box
    grid_gen = CommonGridGenerator(grid_size_km=grid_size_km, bbox=bbox)
    lats, lons = grid_gen.get_lat_lon_mesh()
    grid_cells = []
    for j, lat in enumerate(lats):
        for i, lon in enumerate(lons):
            grid_cells.append({
                "grid_id": grid_gen.generate_cell_id(i, j),
                "center_lat": float(lat),
                "center_lon": float(lon),
            })
    print(f"      Grid dimension : {len(grid_cells)} cells ({len(lats)}x{len(lons)} at {grid_size_km} km)")

    # Prepare radar observations for fusion
    radar_obs_list = []
    for c in raw_radar.get("cells", []):
        radar_obs_list.append({
            "latitude": float(c.get("lat", 0.0)),
            "longitude": float(c.get("lon", 0.0)),
            "reflectivity_dbz": float(c.get("reflectivity_dbz", 0.0)),
            "max_dbz": float(c.get("reflectivity_dbz", 0.0)),
        })
    print(f"      Radar cells with echo: {len(radar_obs_list)}")

    # 2. Ingest Satellite Data
    sat_obs = None
    if satellite_file and Path(satellite_file).exists():
        print(f"\n[2/5] Ingesting Satellite: {satellite_file}")
        sat_adapter = SatelliteAdapter()
        sat_obs = sat_adapter.load_from_file(satellite_file)
        print(f"      Satellite observations loaded: {len(sat_obs)}")
    else:
        print("\n[2/5] Satellite data: NOT PROVIDED / UNAVAILABLE")

    # 3. Ingest Lightning Data
    ltg_obs = None
    if lightning_file and Path(lightning_file).exists():
        print(f"\n[3/5] Ingesting Lightning: {lightning_file}")
        ltg_adapter = LightningAdapter()
        ltg_obs = ltg_adapter.load_from_file(lightning_file)
        print(f"      Lightning strikes loaded: {len(ltg_obs)}")
    else:
        print("\n[3/5] Lightning data: NOT PROVIDED / UNAVAILABLE")

    # 4. Ingest Surface AWS Data
    aws_obs = None
    if aws_file and Path(aws_file).exists():
        print(f"\n[4/5] Ingesting AWS Surface: {aws_file}")
        aws_adapter = AtmosphericAdapter()
        aws_obs = aws_adapter.load_from_file(aws_file)
        print(f"      Surface AWS stations loaded: {len(aws_obs)}")
    else:
        print("\n[4/5] Surface AWS data: NOT PROVIDED / UNAVAILABLE")

    # 5. Execute Multi-Source Fusion Engine
    print("\n[5/5] Executing Multi-Source Fusion Engine...")
    engine = MultiSourceFusionEngine(grid_size_km=grid_size_km, window_duration_seconds=300)
    fused_frame = engine.fuse_frame(
        anchor_timestamp=anchor_timestamp,
        grid_cells=grid_cells,
        radar_grid_observations=radar_obs_list,
        satellite_observations=sat_obs,
        lightning_observations=ltg_obs,
        atmospheric_observations=aws_obs,
        sector_id="delhi-ncr",
        is_sample=True,
    )

    # 6. Export to Parquet Dataset
    exporter = FeatureDatasetExporter(output_base_dir=output_dir)
    export_meta = exporter.export_frame(fused_frame)

    print("\n==================================================")
    print("FUSION PIPELINE COMPLETED")
    print("==================================================")
    print(f"Frame UUID         : {fused_frame.id}")
    print(f"Anchor Timestamp   : {fused_frame.timestamp.isoformat()}")
    print(f"Data Freshness     : {fused_frame.data_freshness.value}")
    print(f"Radar Stream       : {'ONLINE' if fused_frame.radar_available else 'OFFLINE'}")
    print(f"Satellite Stream   : {'ONLINE' if fused_frame.satellite_available else 'OFFLINE'}")
    print(f"Lightning Stream   : {'ONLINE' if fused_frame.lightning_available else 'OFFLINE'}")
    print(f"Atmospheric Stream : {'ONLINE' if fused_frame.atmospheric_available else 'OFFLINE'}")
    print(f"Completeness Score : {fused_frame.completeness_score * 100:.1f}% ({int(fused_frame.completeness_score * 4)}/4 streams)")
    print(f"Cells Synthesized  : {fused_frame.cells_count}")
    print(f"Exported Parquet   : {export_meta['data_file']}")
    print(f"Format             : {export_meta['format'].upper()}")
    print("==================================================")


if __name__ == "__main__":
    from typing import Optional

    parser = argparse.ArgumentParser(description="STORMNET Multi-Source Meteorological Fusion CLI")
    parser.add_argument("--radar", default="data/samples/radar/dwr_delhi_20260926_1545.json", help="Path to radar file")
    parser.add_argument("--satellite", default="data/samples/satellite/insat_3dr_delhi_20260926_1545.json", help="Path to satellite file")
    parser.add_argument("--lightning", default="data/samples/lightning/lln_delhi_20260926_1545.json", help="Path to lightning file")
    parser.add_argument("--aws", default="data/samples/aws/aws_delhi_20260926_1545.json", help="Path to surface AWS file")
    parser.add_argument("--grid-size", type=float, default=3.0, help="Target common grid size (km)")
    parser.add_argument("--output-dir", default="data/processed/fused", help="Export directory for Parquet datasets")

    args = parser.parse_args()
    run_multi_source_fusion(
        radar_file=args.radar,
        satellite_file=args.satellite,
        lightning_file=args.lightning,
        aws_file=args.aws,
        grid_size_km=args.grid_size,
        output_dir=args.output_dir,
    )
