# STORMNET Doppler Weather Radar Ingestion Capability Audit

## 1. Executive Summary

This document provides a comprehensive audit of STORMNET's existing Doppler Weather Radar (DWR) ingestion, validation, gridding, database persistence, API serving, and web GIS rendering architecture implemented across Phases 4 through 8.

---

## 2. Ingestion Pipeline Architecture

The radar ingestion pipeline operates as a modular, decoupled processing chain:

```text
Raw Radar Input File (.json / .geojson)
                   │
                   ▼
ml.preprocessing.radar.ingest.parse_radar_file()
                   │
                   ▼
ml.preprocessing.radar.validator.RadarValidator
  ├── Timestamp Validation (ISO 8601, clock drift, sample flag)
  ├── Coordinate Validation (Antenna lat/lon, WGS84 limits)
  ├── Bounding Box Validation (min/max ordering, regional bounds)
  └── Physical dBZ Thresholds (-32.0 to +85.0 dBZ)
                   │
                   ▼
ml.preprocessing.radar.grid.CommonGridGenerator
  └── 1–3 km Cartesian Binning onto Target Mesh (e.g. 45 x 43 cells)
                   │
                   ▼
ml.preprocessing.radar.processors.ReflectivityProcessor
  ├── Ground Clutter & Anomalous Propagation Filtering
  └── Vector Contour Extraction (Iso-reflectivity bands: 20, 35, 45, 55, 60 dBZ)
                   │
                   ▼
PostGIS Storage (RadarFrameModel & RadarObservationModel)
                   │
                   ▼
FastAPI Backend (GET /api/v1/radar/latest & GET /api/v1/radar/status)
                   │
                   ▼
MapLibre GL Frontend (GISViewportShell.tsx — Vector Polygon Rendering)
```

---

## 3. Supported File Formats & Input Schema

- **Currently Implemented Parsers**:
  - Structured Meteorological JSON (`.json`)
  - Standard RFC 7946 GeoJSON FeatureCollections (`.geojson`)
- **Required Metadata Schema**:
  ```json
  {
    "radar_id": "DWR-DEL-SAF",
    "station_name": "Safdarjung DWR, Delhi",
    "timestamp": "2024-06-28T03:00:00Z",
    "antenna_lat": 28.5847,
    "antenna_lon": 77.2069,
    "antenna_height_m": 230.0,
    "product_type": "COMPOSITE_REFLECTIVITY",
    "source_resolution_km": 0.5,
    "bounding_box": [76.50, 28.00, 77.80, 29.20],
    "cells": [
      {
        "lat": 28.6139,
        "lon": 77.2090,
        "reflectivity_dbz": 54.2,
        "quality_flag": "VALID"
      }
    ]
  }
  ```
- **Raw Formats Required for Full Operational Deployment**:
  - HDF5 / ODIM_H5 (WMO standard for operational weather radar volumes)
  - NetCDF4 / Cf-Radial (Standard scientific radar archive format)
  - Raw binary proprietary polar sweeps (e.g. EEC / Enterprise, Vaisala Sigmet, Gematronik Rainbow)

---

## 4. Supported Variables & Physical Units

| Variable | Symbol | Unit | Physical Range | Pipeline Status | Role in Nowcasting |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Radar Reflectivity** | $Z$ | dBZ | $-32.0\text{ to }+85.0$ | **Fully Supported** | Primary proxy for precipitation rate, core intensity, and convective cell boundaries |
| **Doppler Radial Velocity** | $V_r$ | m/s | $-75.0\text{ to }+75.0$ | **Contract Defined** (Interface ready; pending raw sweep ingestion) | Mesocyclone rotation, gust front divergence, microburst shear detection |
| **Spectrum Width** | $\sigma_v$ / $W$ | m/s | $0.0\text{ to }+25.0$ | **Contract Defined** (Interface ready) | Turbulence, shear zone indicator, non-meteorological echo discrimination |
| **Differential Reflectivity** | $Z_{DR}$ | dB | $-4.0\text{ to }+8.0$ | Defined in Data Bridge | Hydrometeor classification, large hail detection ($Z_{DR} \approx 0$ with high $Z$) |
| **Specific Differential Phase** | $K_{DP}$ | deg/km | $-2.0\text{ to }+15.0$ | Defined in Data Bridge | Heavy rainfall quantification, attenuation correction |

---

## 5. Georeferencing & Spatial Grid Alignment

- **Coordinate Reference System (CRS)**: EPSG:4326 (WGS 84 geodetic latitude/longitude).
- **Target Spatial Grid**:
  - Default Sector: `delhi-ncr`
  - Bounding Box: $[76.50^\circ\text{ E}, 28.00^\circ\text{ N}, 77.80^\circ\text{ E}, 29.20^\circ\text{ N}]$
  - Target Grid Spacing: $1.0\text{ to }3.0\text{ km}$ ($45\text{ rows} \times 43\text{ columns}$ at $3.0\text{ km}$).
- **Resampling Method**:
  - Polar to Cartesian conversion via nearest cell assignment / maximum reflectivity binning.
  - Preserves maximum convective cores (Max-Z rule) without artificial smoothing of peak dBZ cores.
  - Cells lacking observational radar coverage are explicitly quarantined as `QualityFlag.MISSING` (or masked), never artificially filled with synthetic zero reflectivity.

---

## 6. Automated Quality-Control Engine

The [`RadarValidator`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/radar/validator.py) enforces strict physical and operational checks:

1. **Clock Drift & Latency Check**: Enforces observation timestamp within 24 hours for live mode; tags historical samples with explicit `SAMPLE` or `HISTORICAL` freshness tiers.
2. **Geodetic Bounds Check**: Verifies radar antenna coordinates inside India bounding box ($6.0^\circ - 38.0^\circ\text{ N}, 68.0^\circ - 98.0^\circ\text{ E}$).
3. **Bounding Box Geometric Sanity**: Enforces $\text{min\_lon} < \text{max\_lon}$ and $\text{min\_lat} < \text{max\_lat}$.
4. **Physical Range Clamping**: Clamps and flags any reflectivity outside $[-32.0, +85.0\text{ dBZ}]$. Values $> 85.0\text{ dBZ}$ are flagged as non-meteorological artifacts (e.g. sun spikes, RF interference).
5. **Ground Clutter Filtering**: [`ReflectivityProcessor.filter_ground_clutter`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/radar/processors.py#L12) applies median window filtering and anomalous propagation (AP) masking to eliminate static ground targets (buildings, terrain).

---

## 7. Database Persistence & API Integration

- **PostGIS Storage**:
  - Schema: [`RadarFrameModel`](file:///e:/project/SIH%20project%202%20Stormnet/apps/api/models/radar_frame.py) and [`RadarObservationModel`](file:///e:/project/SIH%20project%202%20Stormnet/apps/api/models/radar_observation.py).
  - Stores frame metadata, geodetic polygon bounding boxes, and observation points with PostGIS spatial indexes (`GIST`).
- **FastAPI Endpoints**:
  - `GET /api/v1/radar/latest`: Delivers latest radar frame detail, summary statistics (max dBZ, mean dBZ, valid cells), and pre-computed vector contour levels.
  - `GET /api/v1/radar/frames`: Paginated list of historical observation frames.
  - `GET /api/v1/radar/status`: Real-time operational telemetry and data freshness tier (`LIVE`, `HISTORICAL`, `SAMPLE`, `STALE`).
  - `GET /api/v1/radar/{frame_id}`: Lookup of specific archived radar frames.

---

## 8. Web GIS & MapLibre Rendering Path

- **Client Component**: [`apps/web/components/map/GISViewportShell.tsx`](file:///e:/project/SIH%20project%202%20Stormnet/apps/web/components/map/GISViewportShell.tsx).
- **Rendering Mechanism**:
  - Consumes vector contours directly from API (`radar-reflectivity-source`).
  - Renders multi-tiered polygon fills styled according to the standard meteorological dBZ color table:
    - $\ge 20\text{ dBZ}$ (Light Rain / Cloud): `#00e400`
    - $\ge 35\text{ dBZ}$ (Moderate Rain): `#ffff00`
    - $\ge 45\text{ dBZ}$ (Heavy Thunderstorm Core): `#ff7e00`
    - $\ge 55\text{ dBZ}$ (Severe Convective Core / Hail Risk): `#ff0000`
    - $\ge 60\text{ dBZ}$ (Violent Convection / Large Hail / Cloudburst): `#99004c`
  - Dynamic opacity control ($0.0\text{ to }1.0$) supported via [`LayerToggleMenu.tsx`](file:///e:/project/SIH%20project%202%20Stormnet/apps/web/components/map/LayerToggleMenu.tsx).
