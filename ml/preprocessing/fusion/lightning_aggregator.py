"""Lightning Grid Aggregator: Transforms point discharge events into spatial grid metrics."""

from typing import Any, Dict, List, Optional, Tuple
from ml.preprocessing.fusion.interfaces import LightningObservation, TemporalWindow


class LightningGridAggregator:
    """Aggregates discrete lightning strikes onto the common 1–3 km spatial grid."""

    def __init__(self, grid_size_km: float = 3.0):
        self.grid_size_km = grid_size_km
        self.cell_area_km2 = grid_size_km * grid_size_km

    def aggregate_to_grid(
        self,
        strikes: List[LightningObservation],
        grid_cells: List[Dict[str, Any]],
        window: TemporalWindow,
        previous_rates: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregates strikes into cell-level features: strike_count, density, rate, trend."""
        # Half size in degrees (~0.009 deg per km for latitude)
        deg_lat_half = (self.grid_size_km / 111.0) / 2.0
        deg_lon_half = (self.grid_size_km / 100.0) / 2.0

        window_minutes = max(1.0, window.duration_seconds / 60.0)
        previous_rates = previous_rates or {}

        results: Dict[str, Dict[str, Any]] = {}

        # Initialize all cells with 0
        for cell in grid_cells:
            grid_id = cell["grid_id"]
            results[grid_id] = {
                "strike_count": 0,
                "density_per_km2": 0.0,
                "rate_per_min": 0.0,
                "trend": "STABLE",
                "acceleration": 0.0,
            }

        # Bin strikes into corresponding cell bounding boxes
        for s in strikes:
            lat = s.latitude
            lon = s.longitude

            for cell in grid_cells:
                clat = cell["center_lat"]
                clon = cell["center_lon"]
                grid_id = cell["grid_id"]

                if (clat - deg_lat_half <= lat <= clat + deg_lat_half) and (
                    clon - deg_lon_half <= lon <= clon + deg_lon_half
                ):
                    results[grid_id]["strike_count"] += 1
                    break

        # Compute derived rates, densities, and trends
        for grid_id, metrics in results.items():
            count = metrics["strike_count"]
            density = round(count / self.cell_area_km2, 4)
            rate = round(count / window_minutes, 2)
            prev_rate = previous_rates.get(grid_id, 0.0)

            # Trend calculation
            if prev_rate == 0.0:
                trend = "INCREASING" if rate > 0 else "STABLE"
            elif rate > prev_rate * 1.2:
                trend = "INCREASING"
            elif rate < prev_rate * 0.8:
                trend = "DECREASING"
            else:
                trend = "STABLE"

            accel = round((rate - prev_rate) / window_minutes, 3)

            metrics["density_per_km2"] = density
            metrics["rate_per_min"] = rate
            metrics["trend"] = trend
            metrics["acceleration"] = accel

        return results
