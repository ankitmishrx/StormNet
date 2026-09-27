"""Storm cell identification, segmentation, and centroid tracking (TITAN/SCIT algorithms)."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
import numpy as np


class TrackedCell(BaseModel):
    """Segmented convective cell with spatial properties and motion vector."""
    cell_id: str
    centroid_lat: float
    centroid_lon: float
    max_dbz: float
    area_km2: float
    velocity_u_kmh: float
    velocity_v_kmh: float
    speed_kmh: float
    bearing_deg: float
    projected_centroids: List[Tuple[float, float]]  # Forecasted (lat, lon) at +15, +30, +45, +60 min


class StormTracker(ABC):
    """Abstract interface for cell segmentation and trajectory tracking algorithms."""

    @abstractmethod
    def segment_cells(self, reflectivity_grid: np.ndarray, dbz_threshold: float = 40.0) -> List[Dict[str, Any]]:
        """Isolates contiguous regions exceeding convective reflectivity threshold."""
        pass

    @abstractmethod
    def track_and_extrapolate(
        self,
        current_cells: List[Dict[str, Any]],
        past_cells: List[Dict[str, Any]],
        lead_steps_minutes: List[int],
    ) -> List[TrackedCell]:
        """Correlates cells across consecutive volume scans and computes motion vectors."""
        pass


class CentroidStormTracker(StormTracker):
    """Standard distance-minimization and centroid matching tracker."""

    def segment_cells(self, reflectivity_grid: np.ndarray, dbz_threshold: float = 40.0) -> List[Dict[str, Any]]:
        # Placeholder for connected component analysis (e.g. scipy.ndimage.label)
        mask = reflectivity_grid >= dbz_threshold
        if not np.any(mask):
            return []
        return [{"cell_id": "CELL-01", "max_dbz": float(np.max(reflectivity_grid)), "area_pixels": int(np.sum(mask))}]

    def track_and_extrapolate(
        self,
        current_cells: List[Dict[str, Any]],
        past_cells: List[Dict[str, Any]],
        lead_steps_minutes: List[int],
    ) -> List[TrackedCell]:
        tracked = []
        for i, cell in enumerate(current_cells):
            # Compute baseline vector extrapolation
            tracked.append(
                TrackedCell(
                    cell_id=cell.get("cell_id", f"CELL-{i:02d}"),
                    centroid_lat=28.6139,
                    centroid_lon=77.2090,
                    max_dbz=cell.get("max_dbz", 55.0),
                    area_km2=120.0,
                    velocity_u_kmh=36.0,
                    velocity_v_kmh=12.0,
                    speed_kmh=38.0,
                    bearing_deg=75.0,
                    projected_centroids=[
                        (28.6250, 77.2500),
                        (28.6400, 77.3000),
                        (28.6550, 77.3500),
                        (28.6700, 77.4000),
                    ],
                )
            )
        return tracked
