# STORMNET Radar Ingestion Pipeline & PostGIS Integration Architecture
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting (0–6 hr)  
**File Reference:** `docs/architecture/radar-pipeline.md`  
**Status:** Approved Architecture Document  

---

## 1. End-to-End Radar Processing Pipeline

The radar data pipeline processes volumetric and Cartesian radar observations into standardized 1–3 km gridded PostGIS layers for downstream AI inference and GIS visualization:

```
┌────────────────────────────────────────────────────────┐
│  Radar Source (WMO ODIM_H5, CfRadial, GeoTIFF, JSON)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  1. Ingestion Adapter (ml/preprocessing/radar/)        │
│     - Raw file reading and metadata extraction         │
│     - Station parameters: lat, lon, height, frequency  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  2. Validation Engine (validator.py)                   │
│     - Timestamp sanity (ISO 8601, not future/stale)    │
│     - Physical ranges (-30 to +85 dBZ)                 │
│     - Corrupted/NaN ratio quarantine                   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  3. Quality Control & Processing (processors.py)       │
│     - Ground clutter removal & speckle filtering       │
│     - Composite Reflectivity (Z_comp) calculation      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  4. Geo-Referencing & Transformation (georeference.py) │
│     - Curved earth refraction (4/3 R_E model)          │
│     - Coordinate transformation to EPSG:4326 WGS84     │
│     - Bounding box & spatial envelope calculation      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  5. 1–3 km Common Grid Tessellation (grid.py)          │
│     - Configurable 1 km, 2 km, 3 km target cells       │
│     - Default: 3 km resolution (SIH26084 standard)     │
│     - Logarithmic power averaging: 10*log10(mean(z))   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  6. PostGIS Storage Layer                              │
│     - radar_frames (metadata, spatial bbox)            │
│     - radar_observations (gridded dBZ, GIST index)     │
│     - grid_cells (reusable polygon tessellation)       │
│     - radar_products (vector contour geometries)       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  7. FastAPI REST Services (apps/api/routers/radar.py)  │
│     - GET /api/v1/radar/latest                         │
│     - GET /api/v1/radar/frames                         │
│     - GET /api/v1/radar/{frame_id}/grid                │
│     - GET /api/v1/radar/status                         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  8. GIS Frontend MapLibre (RadarLayer.tsx)             │
│     - Calibrated WMO dBZ palette raster/vector display │
│     - Opacity control, visibility toggle, legend       │
│     - DEMO MODE / SAMPLE DATA freshness indicator      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Ingestion Modules & Core Interfaces

The pipeline resides in `ml/preprocessing/radar/`:

1. **`interfaces.py`**:
   - `RadarDataSource`: Abstract base class defining `load_frame()`, `validate()`, and `get_metadata()`.
   - `RadarObservation`: Data class representing a discrete observation point with latitude, longitude, reflectivity ($dBZ$), and quality flag.
   - `RadarVolume`: Volumetric polar scan container storing vertical sweeps ($0.5^{\circ}$ to $21.0^{\circ}$).
   - `RadarSweep`: Single elevation azimuth-range polar matrix.
   - `RadarFrame`: Standard decoded 2D radar product (e.g. Composite Reflectivity $Z_{\text{comp}}$) with geographic envelope, CRS, resolution, and quality flags.

2. **`validator.py`**:
   - `RadarValidator`: Validates timestamps, coordinates, physical reflectivity boundaries, and quarantine conditions.

3. **`processors.py`**:
   - `ReflectivityProcessor`: Handles ground clutter thresholds ($<10\text{ dBZ}$ masking), speckle filtering, and composite derivation.

4. **`georeference.py`**:
   - `RadarGeoReferencer`: Converts radar range/azimuth into standard `EPSG:4326` coordinates using the 4/3 effective Earth radius model.

5. **`grid.py`**:
   - `CommonGridGenerator`: Computes regular 1 km, 2 km, or 3 km grid tessellations across target meteorological sectors.

6. **`ingest.py`**:
   - CLI tool for automated file ingestion:
     `python -m ml.preprocessing.radar.ingest <file_path> --grid-size 3`

---

## 3. PostGIS Database Schema

The pipeline integrates into PostgreSQL 16 + PostGIS 3.4 with four primary tables:

### 3.1 `radar_frames`
Stores metadata and bounding footprints for each observation scan:
- `id`: UUID (Primary Key)
- `radar_id`: String(64) — e.g. `DWR-DEL-SAF`
- `source`: String(64) — e.g. `DEVELOPMENT_SAMPLE`
- `timestamp`: DateTime (Indexed)
- `product_type`: String(32) — e.g. `COMPOSITE_REFLECTIVITY`
- `resolution_km`: Float — Target grid size (e.g. `3.0`)
- `source_resolution_km`: Float — Raw radar resolution (e.g. `0.5`)
- `crs`: String(32) — `EPSG:4326`
- `bounding_box`: JSONB — `[min_lon, min_lat, max_lon, max_lat]`
- `coverage_area`: Geometry('POLYGON', 4326) with GIST Index
- `status`: String(32) — `PROCESSED`, `VALIDATED`, `SAMPLE`
- `total_cells_processed`: Integer
- `max_dbz`: Float
- `created_at`: DateTime

### 3.2 `radar_observations`
Stores gridded observation values:
- `id`: UUID (Primary Key)
- `frame_id`: UUID (Foreign Key to `radar_frames.id`, Indexed)
- `grid_cell_id`: String(64) (Indexed)
- `timestamp`: DateTime (Indexed)
- `latitude`: Float
- `longitude`: Float
- `reflectivity`: Float ($dBZ$)
- `quality_flag`: String(32) — `VALID`, `DEGRADED`, `CLUTTER_FILTERED`
- `geometry`: Geometry('POINT', 4326) with GIST Index

### 3.3 `grid_cells`
Reusable spatial tessellation:
- `id`: UUID (Primary Key)
- `grid_id`: String(64) (Unique Index) — e.g. `DEL-3KM-X024-Y031`
- `sector_id`: String(32) (Indexed)
- `grid_size_km`: Float — `1.0`, `2.0`, `3.0`
- `center_lat`: Float
- `center_lon`: Float
- `geometry`: Geometry('POLYGON', 4326) with GIST Index

### 3.4 `radar_products`
Cached GeoJSON contours and tile paths for low-latency web serving:
- `id`: UUID (Primary Key)
- `frame_id`: UUID (Foreign Key to `radar_frames.id`)
- `product_type`: String(32)
- `min_dbz`: Float
- `max_dbz`: Float
- `geojson_contours`: JSONB (GeoJSON FeatureCollection)
- `tile_url`: String(512)

---

## 4. REST API Specifications (`/api/v1/radar`)

1. **`GET /api/v1/radar/latest`**
   - Returns the most recently ingested radar frame with summary statistics (max dBZ, coverage, timestamp, source).
2. **`GET /api/v1/radar/frames`**
   - Query params: `sector_id`, `limit`, `offset`.
   - Returns chronological list of radar frames.
3. **`GET /api/v1/radar/{frame_id}`**
   - Returns specific frame metadata.
4. **`GET /api/v1/radar/{frame_id}/grid`**
   - Query params: `format` (`geojson` | `array`), `min_dbz` (default: 15.0).
   - Returns gridded radar reflectivity values optimized for MapLibre rendering.
5. **`GET /api/v1/radar/status`**
   - Returns data freshness status: `LIVE`, `HISTORICAL`, `REPLAY`, `SAMPLE`, `STALE`, or `UNAVAILABLE`.

---

## 5. Data Freshness Model

| Status Code | Criteria | Frontend Visual Badge |
|---|---|---|
| `LIVE` | Fresh data from active radar feed received $\le 10$ minutes ago | Green badge: `LIVE FEED` |
| `HISTORICAL` | Archived operational observations older than 10 minutes | Gray badge: `HISTORICAL ARCHIVE` |
| `REPLAY` | Historical storm case replayed via timeline scrubber | Blue badge: `REPLAY MODE` |
| `SAMPLE` | Development fixture or synthetic test dataset | Amber badge: `DEMO MODE / SAMPLE DATA` |
| `STALE` | Expected real-time feed has exceeded latency thresholds ($>20$ min) | Orange badge: `FEED STALE` |
| `UNAVAILABLE` | Radar site offline, maintenance, or communication loss | Red badge: `SENSOR OFFLINE` |
