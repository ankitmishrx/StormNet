"""1–3 km Common Meteorological Grid Generator for STORMNET.

Standardizes high-resolution multi-source Doppler radar and satellite observations
onto regular 1 km, 2 km, or 3 km Cartesian cells (default: 3 km per SIH26084).
"""

import math
from typing import Dict, List, Tuple, Optional
import numpy as np
from shapely.geometry import Polygon, box


class CommonGridGenerator:
    """Generates regular geospatial tessellation and re-samples observation arrays."""

    # Approximate degree equivalents at temperate / tropical latitudes (~28°N in India)
    KM_PER_DEGREE_LAT = 110.852
    KM_PER_DEGREE_LON = 97.944  # at 28.0°N

    DEFAULT_SECTOR_BBOX = (76.50, 28.00, 77.80, 29.20)  # Delhi-NCR composite domain

    def __init__(
        self,
        grid_size_km: float = 3.0,
        bbox: Tuple[float, float, float, float] = DEFAULT_SECTOR_BBOX,
        sector_id: str = "delhi-ncr",
    ):
        """Initializes grid generator with target resolution in kilometers (1.0, 2.0, or 3.0)."""
        if grid_size_km not in [1.0, 2.0, 3.0]:
            raise ValueError(f"Unsupported grid size {grid_size_km} km. Supported: [1.0, 2.0, 3.0].")

        self.grid_size_km = float(grid_size_km)
        self.sector_id = sector_id
        self.min_lon, self.min_lat, self.max_lon, self.max_lat = bbox

        # Compute cell step in degrees
        self.d_lat = self.grid_size_km / self.KM_PER_DEGREE_LAT
        self.d_lon = self.grid_size_km / self.KM_PER_DEGREE_LON

        # Compute grid dimensions
        self.n_lons = int(math.ceil((self.max_lon - self.min_lon) / self.d_lon))
        self.n_lats = int(math.ceil((self.max_lat - self.min_lat) / self.d_lat))

        # Adjust max bounds to match exact grid integer steps
        self.max_lon = self.min_lon + self.n_lons * self.d_lon
        self.max_lat = self.min_lat + self.n_lats * self.d_lat

    def get_grid_dimensions(self) -> Tuple[int, int]:
        """Returns (n_lats, n_lons)."""
        return self.n_lats, self.n_lons

    def get_lat_lon_mesh(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generates 1D latitude and longitude coordinate arrays (centers of cells)."""
        lons = self.min_lon + (np.arange(self.n_lons) + 0.5) * self.d_lon
        lats = self.min_lat + (np.arange(self.n_lats) + 0.5) * self.d_lat
        return lats, lons

    def generate_cell_id(self, grid_x: int, grid_y: int) -> str:
        """Generates standardized cell identifier, e.g. 'DEL-3KM-X024-Y031'."""
        prefix = self.sector_id[:3].upper()
        res_str = f"{int(self.grid_size_km)}KM"
        return f"{prefix}-{res_str}-X{grid_x:03d}-Y{grid_y:03d}"

    def get_cell_polygon(self, grid_x: int, grid_y: int) -> Polygon:
        """Computes bounding Shapely Polygon for a specific grid cell."""
        cell_min_lon = self.min_lon + grid_x * self.d_lon
        cell_max_lon = cell_min_lon + self.d_lon
        cell_min_lat = self.min_lat + grid_y * self.d_lat
        cell_max_lat = cell_min_lat + self.d_lat

        return box(cell_min_lon, cell_min_lat, cell_max_lon, cell_max_lat)

    def resample_reflectivity_to_grid(
        self,
        source_grid: np.ndarray,
        source_lats: np.ndarray,
        source_lons: np.ndarray,
    ) -> np.ndarray:
        """Resamples raw source radar reflectivity to target common grid

        using logarithmic radar power averaging: 10 * log10(mean(10^(dBZ/10))).
        """
        target_lats, target_lons = self.get_lat_lon_mesh()
        target_matrix = np.full((self.n_lats, self.n_lons), 0.0, dtype=np.float32)

        # Vectorized or nearest-neighbor cell mapping
        lat_step = target_lats[1] - target_lats[0] if len(target_lats) > 1 else self.d_lat
        lon_step = target_lons[1] - target_lons[0] if len(target_lons) > 1 else self.d_lon

        for j in range(self.n_lats):
            lat_center = target_lats[j]
            # Find matching indices in source
            lat_mask = np.abs(source_lats - lat_center) <= (lat_step / 2.0)
            if not np.any(lat_mask):
                continue

            for i in range(self.n_lons):
                lon_center = target_lons[i]
                lon_mask = np.abs(source_lons - lon_center) <= (lon_step / 2.0)
                if not np.any(lon_mask):
                    continue

                sub_grid = source_grid[np.ix_(lat_mask, lon_mask)]
                valid_vals = sub_grid[sub_grid > 5.0]  # Only average meteorological returns

                if valid_vals.size > 0:
                    # Logarithmic power averaging
                    linear_power = 10.0 ** (valid_vals / 10.0)
                    mean_linear = np.mean(linear_power)
                    target_matrix[j, i] = float(10.0 * np.log10(max(1e-3, mean_linear)))
                else:
                    target_matrix[j, i] = 0.0

        return target_matrix
