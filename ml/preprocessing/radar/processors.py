"""Reflectivity Processing and Quality Control for STORMNET.

Implements ground clutter suppression, composite reflectivity derivation,
and vector contour extraction for lightweight GIS transmission.
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from ml.preprocessing.radar.interfaces import RadarFrame, RadarVolume
from ml.preprocessing.radar.validator import RadarValidator


class ReflectivityProcessor:
    """Processes volumetric radar reflectivity into analysis-ready 2D fields."""

    CLUTTER_MIN_DBZ = 12.0  # Echoes below 12 dBZ considered non-precipitating / clear-air

    @classmethod
    def filter_ground_clutter(cls, dbz_matrix: np.ndarray) -> np.ndarray:
        """Applies ground clutter and noise thresholds."""
        cleaned = np.copy(dbz_matrix)
        # Suppress non-meteorological reflections
        cleaned[cleaned < cls.CLUTTER_MIN_DBZ] = 0.0
        return cleaned

    @classmethod
    def compute_composite_reflectivity(cls, volume: RadarVolume, grid_shape: Tuple[int, int]) -> np.ndarray:
        """Computes column-maximum composite reflectivity (Z_comp) across all sweeps."""
        if not volume.sweeps:
            return np.zeros(grid_shape, dtype=np.float32)

        composite = np.zeros(grid_shape, dtype=np.float32)
        for sweep in volume.sweeps:
            if sweep.reflectivity is not None and sweep.reflectivity.shape == grid_shape:
                composite = np.maximum(composite, sweep.reflectivity)

        return cls.filter_ground_clutter(composite)

    @classmethod
    def extract_reflectivity_contours(
        cls,
        grid_matrix: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
        dbz_levels: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Extracts vector GeoJSON polygons for calibrated dBZ intervals.

        Enables ultra-fast web rendering without multi-megabyte tile transmissions.
        """
        if dbz_levels is None:
            dbz_levels = [20, 35, 45, 55, 60]

        contours: List[Dict[str, Any]] = []
        d_lat = float(lats[1] - lats[0]) if len(lats) > 1 else 0.027
        d_lon = float(lons[1] - lons[0]) if len(lons) > 1 else 0.027

        level_colors = {
            20: "#457B9D",
            35: "#2A9D8F",
            45: "#F4A261",
            55: "#E76F51",
            60: "#D90429",
        }

        for level in dbz_levels:
            mask = grid_matrix >= level
            if not np.any(mask):
                continue

            cell_polygons: List[Polygon] = []
            for j in range(grid_matrix.shape[0]):
                for i in range(grid_matrix.shape[1]):
                    if mask[j, i]:
                        c_lon = float(lons[i])
                        c_lat = float(lats[j])
                        cell_poly = box(
                            c_lon - d_lon / 2.0,
                            c_lat - d_lat / 2.0,
                            c_lon + d_lon / 2.0,
                            c_lat + d_lat / 2.0,
                        )
                        cell_polygons.append(cell_poly)

            if cell_polygons:
                # Merge adjacent cells into unified multi-polygons
                merged = unary_union(cell_polygons)
                if isinstance(merged, Polygon):
                    coords = [list(merged.exterior.coords)]
                elif isinstance(merged, MultiPolygon):
                    coords = [list(poly.exterior.coords) for poly in merged.geoms]
                else:
                    continue

                contours.append({
                    "dbz_level": level,
                    "color": level_colors.get(level, "#D90429"),
                    "geometry": {
                        "type": "MultiPolygon" if isinstance(merged, MultiPolygon) else "Polygon",
                        "coordinates": [[[c[0], c[1]] for c in ring] for ring in coords] if isinstance(merged, Polygon) else [[[[c[0], c[1]] for c in ring]] for ring in coords],
                    },
                })

        return contours
