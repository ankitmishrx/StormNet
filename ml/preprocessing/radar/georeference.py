"""Geospatial Georeferencing Utilities for Doppler Radar Data.

Implements curved-earth atmospheric refraction (4/3 R_E model) and
transformation between polar radar coordinates and EPSG:4326 WGS84.
"""

import math
from typing import Tuple, List
import numpy as np
from shapely.geometry import Polygon, box

# Standard Earth constants
EARTH_RADIUS_KM = 6371.0
EFFECTIVE_EARTH_RADIUS_KM = (4.0 / 3.0) * EARTH_RADIUS_KM  # 8494.67 km


def polar_to_ground_range(slant_range_km: float, elevation_deg: float) -> Tuple[float, float]:
    """Calculates ground range (s) and height above antenna (h) in km

    using the standard 4/3 effective Earth radius atmospheric refraction model.
    """
    elev_rad = math.radians(elevation_deg)
    r = slant_range_km
    r_prime = EFFECTIVE_EARTH_RADIUS_KM

    # Height above antenna: sqrt(r^2 + R'^2 + 2rR'sin(elev)) - R'
    h = math.sqrt(r**2 + r_prime**2 + 2.0 * r * r_prime * math.sin(elev_rad)) - r_prime

    # Ground range along curved earth surface
    s = r_prime * math.asin((r * math.cos(elev_rad)) / (r_prime + h))

    return s, h


def radar_bin_to_latlon(
    antenna_lat: float,
    antenna_lon: float,
    ground_range_km: float,
    azimuth_deg: float,
) -> Tuple[float, float]:
    """Transforms ground distance and azimuth from radar into WGS84 (lat, lon)."""
    lat1 = math.radians(antenna_lat)
    lon1 = math.radians(antenna_lon)
    az_rad = math.radians(azimuth_deg)

    d_div_r = ground_range_km / EARTH_RADIUS_KM

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d_div_r)
        + math.cos(lat1) * math.sin(d_div_r) * math.cos(az_rad)
    )

    lon2 = lon1 + math.atan2(
        math.sin(az_rad) * math.sin(d_div_r) * math.cos(lat1),
        math.cos(d_div_r) - math.sin(lat1) * math.sin(lat2),
    )

    return math.degrees(lat2), math.degrees(lon2)


def compute_radar_coverage_polygon(
    antenna_lat: float,
    antenna_lon: float,
    max_range_km: float = 250.0,
    num_points: int = 64,
) -> Polygon:
    """Computes a Shapely Polygon representing the maximum radar range footprint."""
    coords: List[Tuple[float, float]] = []
    for i in range(num_points):
        az = (i * 360.0) / num_points
        lat, lon = radar_bin_to_latlon(antenna_lat, antenna_lon, max_range_km, az)
        coords.append((lon, lat))  # GeoJSON / Shapely order: (x, y) = (lon, lat)

    coords.append(coords[0])  # Close ring
    return Polygon(coords)


def create_bbox_polygon(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> Polygon:
    """Creates a Shapely Polygon representing an axis-aligned bounding box."""
    return box(min_lon, min_lat, max_lon, max_lat)
