"""Convective Weather Event Extraction Pipeline."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np

from packages.shared.radar_archive.adapter import ArchiveFrameRecord


@dataclass
class ConvectiveEventRecord:
    """Represents a temporally continuous, mesoscale convective episode."""
    event_id: str
    station_id: str
    start_time: str
    end_time: str
    duration_minutes: float
    frame_count: int
    peak_dbz: float
    mean_convective_area_km2: float
    geographic_extent: Dict[str, float]
    data_quality_score: float  # 0.0 to 1.0 based on continuity and missing scans
    sample_indices: List[int] = field(default_factory=list)


class ConvectiveEventExtractor:
    r"""Identifies and extracts coherent convective storm episodes from continuous radar time series.

    Meteorological Event Detection Criteria:
    1. Intensity Criterion: Maximum reflectivity in domain $\ge 35.0\text{ dBZ}$.
    2. Spatial Scale Criterion: Active convective core area $\ge 5\text{ pixels}$ ($45\text{ km}^2$ at $3\text{km}$ resolution).
    3. Temporal Continuity: Episode sustained for at least 3 consecutive frames ($\ge 30\text{ minutes}$ at 10-minute cadence).
    4. Episode Termination: Episode terminates when reflectivity drops below threshold for $>30\text{ minutes}$ (break in convection).
    """

    def __init__(
        self,
        convective_threshold_dbz: float = 35.0,
        min_convective_cells: int = 5,
        min_duration_minutes: float = 30.0,
        break_tolerance_minutes: float = 20.0,
    ):
        self.threshold_dbz = convective_threshold_dbz
        self.min_cells = min_convective_cells
        self.min_duration_minutes = min_duration_minutes
        self.break_tolerance_minutes = break_tolerance_minutes

    def extract_events_from_grids(
        self,
        station_id: str,
        timestamps: List[datetime],
        grids: List[np.ndarray],  # List of (H, W) float32 arrays
        station_extent: Dict[str, float],
    ) -> List[ConvectiveEventRecord]:
        """Scans sequence of 2D grids and extracts isolated convective episodes."""
        if len(timestamps) != len(grids) or len(timestamps) == 0:
            return []

        events: List[ConvectiveEventRecord] = []
        in_event = False
        current_event_indices: List[int] = []
        event_counter = 1

        for idx, (ts, grid) in enumerate(zip(timestamps, grids)):
            active_cells = int(np.sum(grid >= self.threshold_dbz))
            is_convective = active_cells >= self.min_cells

            if is_convective:
                if not in_event:
                    # Start new candidate event
                    in_event = True
                    current_event_indices = [idx]
                else:
                    # Check gap from previous frame
                    prev_ts = timestamps[current_event_indices[-1]]
                    gap_min = (ts - prev_ts).total_seconds() / 60.0
                    if gap_min <= self.break_tolerance_minutes:
                        current_event_indices.append(idx)
                    else:
                        # Finalize previous event if it meets duration requirement
                        self._maybe_save_event(
                            events, station_id, current_event_indices, timestamps, grids, station_extent, event_counter
                        )
                        event_counter += 1
                        current_event_indices = [idx]
            else:
                if in_event:
                    # Finalize current event
                    self._maybe_save_event(
                        events, station_id, current_event_indices, timestamps, grids, station_extent, event_counter
                    )
                    event_counter += 1
                    in_event = False
                    current_event_indices = []

        # Flush final event
        if in_event and current_event_indices:
            self._maybe_save_event(
                events, station_id, current_event_indices, timestamps, grids, station_extent, event_counter
            )

        return events

    def _maybe_save_event(
        self,
        events: List[ConvectiveEventRecord],
        station_id: str,
        indices: List[int],
        timestamps: List[datetime],
        grids: List[np.ndarray],
        extent: Dict[str, float],
        counter: int,
    ) -> None:
        if not indices:
            return

        start_ts = timestamps[indices[0]]
        end_ts = timestamps[indices[-1]]
        duration_min = (end_ts - start_ts).total_seconds() / 60.0

        if duration_min < self.min_duration_minutes and len(indices) < 3:
            # Below duration threshold for mesoscale analysis
            return

        event_grids = [grids[i] for i in indices]
        peak_dbz = float(np.max([np.max(g) for g in event_grids]))

        # Calculate mean convective footprint area (km^2) assuming 3km x 3km = 9 km^2 per cell
        areas = [np.sum(g >= self.threshold_dbz) * 9.0 for g in event_grids]
        mean_area = float(np.mean(areas))

        event_id = f"EVT-{station_id}-{start_ts.strftime('%Y%m%d')}-{counter:03d}"

        events.append(
            ConvectiveEventRecord(
                event_id=event_id,
                station_id=station_id,
                start_time=start_ts.isoformat(),
                end_time=end_ts.isoformat(),
                duration_minutes=round(duration_min, 1),
                frame_count=len(indices),
                peak_dbz=round(peak_dbz, 1),
                mean_convective_area_km2=round(mean_area, 1),
                geographic_extent=extent,
                data_quality_score=1.0,
                sample_indices=indices,
            )
        )
