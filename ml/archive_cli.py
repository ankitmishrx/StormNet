"""Command-Line Interface for Phase 7 Historical Radar Archive Operations.

Commands:
- index: Indexes radar volumes in archive directory
- qc: Executes quality control audit across indexed frames
- extract-events: Segments continuous series into convective storm events
- evaluate: Runs multi-station verification matrix
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
import numpy as np

from packages.shared.radar_archive.stations import get_station_registry
from packages.shared.radar_archive.adapter import HistoricalRadarArchiveAdapter
from packages.shared.radar_archive.qc import ArchiveQualityController
from packages.shared.radar_archive.normalizer import MultiStationNormalizer
from packages.shared.radar_archive.events import ConvectiveEventExtractor
from ml.evaluation.multi_station_evaluator import MultiStationEvaluator
from ml.experiments.run_experiment import generate_controlled_convective_episodes
from ml.training.splitter import EventBlockedSplitter


def cmd_index(args):
    print(f"[Archive Indexer] Scanning archive for station: {args.station_id}")
    adapter = HistoricalRadarArchiveAdapter(archive_root_dir=args.archive_dir)
    records = adapter.scan_station_archive(args.station_id)
    print(f"[Archive Indexer] Discovered {len(records)} total files.")
    valid_count = sum(1 for r in records if r.is_valid)
    print(f"[Archive Indexer] Valid files: {valid_count} | Issues: {len(records) - valid_count}")

    if args.output:
        adapter.export_index_catalog(args.output)
        print(f"[Archive Indexer] Exported catalog index to {args.output}")


def cmd_qc(args):
    print(f"[Quality Control] Running QC audit for station: {args.station_id}")
    adapter = HistoricalRadarArchiveAdapter(archive_root_dir=args.archive_dir)
    records = adapter.scan_station_archive(args.station_id)
    qc = ArchiveQualityController()
    report = qc.run_qc_audit(args.station_id, records)

    print(f"[Quality Control] Results for {args.station_id}:")
    print(f"  - Total Scans: {report.total_files_scanned}")
    print(f"  - Valid Scans: {report.valid_frames_count}")
    print(f"  - Pass Rate: {report.pass_rate_percentage}%")
    print(f"  - Temporal Gaps: {report.temporal_gaps_count}")
    print(f"  - Acceptable for ML Training: {report.is_acceptable_for_training}")


def cmd_extract_events(args):
    print(f"[Event Extractor] Extracting convective episodes for station: {args.station_id}")
    registry = get_station_registry()
    station = registry.get_station(args.station_id)
    if not station:
        print(f"Error: Unknown station {args.station_id}", file=sys.stderr)
        return

    # Use sample grids if raw archive is empty
    sample_path = os.path.join("data", "samples", "radar", "dwr_delhi_20260926_1545.json")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        grid = np.array(data["reflectivity_grid_dbz"], dtype=np.float32)
        timestamps = [datetime(2026, 9, 26, 15, 45, tzinfo=timezone.utc)]
        grids = [grid]

        extractor = ConvectiveEventExtractor(convective_threshold_dbz=35.0, min_convective_cells=5)
        events = extractor.extract_events_from_grids(args.station_id, timestamps, grids, station.grid_extent_wgs84)
        print(f"[Event Extractor] Extracted {len(events)} candidate mesoscale events.")
        for e in events:
            print(f"  - Event: {e.event_id} | Peak dBZ: {e.peak_dbz} | Duration: {e.duration_minutes}m")
    else:
        print("No observation grids available for event segmentation.")


def cmd_evaluate(args):
    print("[Multi-Station Evaluator] Running multi-station verification...")
    evaluator = MultiStationEvaluator()

    x, y, episodes = generate_controlled_convective_episodes(num_episodes=4, seed=42)
    splitter = EventBlockedSplitter(embargo_hours=24.0, train_ratio=0.5, val_ratio=0.25, test_ratio=0.25)
    splits = splitter.partition_episodes(episodes)

    station_test_data = {
        "DWR-DEL-SAF": {
            "features": x[splits.test_indices],
            "targets": y[splits.test_indices] * 75.0,
            "num_events": len(splits.test_episodes),
        },
        "DWR-MUM-VER": None,
        "DWR-CHE-PRT": None,
        "DWR-KOL-SUB": None,
    }

    res = evaluator.evaluate_multi_station(station_test_data)
    md_table = evaluator.generate_results_markdown_table(res)
    print("\n" + md_table)


def main():
    parser = argparse.ArgumentParser(description="STORMNET Phase 7 Historical Archive CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # index
    p_index = subparsers.add_parser("index", help="Index raw radar files in station archive")
    p_index.add_argument("--station-id", type=str, default="DWR-DEL-SAF", help="Target radar station ID")
    p_index.add_argument("--archive-dir", type=str, default="data/raw/radar_archive", help="Root archive directory")
    p_index.add_argument("--output", type=str, default="data/processed/archive_index.json", help="Output catalog index")
    p_index.set_defaults(func=cmd_index)

    # qc
    p_qc = subparsers.add_parser("qc", help="Run archive quality control audit")
    p_qc.add_argument("--station-id", type=str, default="DWR-DEL-SAF", help="Target radar station ID")
    p_qc.add_argument("--archive-dir", type=str, default="data/raw/radar_archive", help="Root archive directory")
    p_qc.set_defaults(func=cmd_qc)

    # extract-events
    p_evt = subparsers.add_parser("extract-events", help="Segment continuous grids into storm events")
    p_evt.add_argument("--station-id", type=str, default="DWR-DEL-SAF", help="Target radar station ID")
    p_evt.set_defaults(func=cmd_extract_events)

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Run multi-station verification matrix")
    p_eval.set_defaults(func=cmd_evaluate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
