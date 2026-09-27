# STORMNET — Multi-Source Meteorological Data Fusion Architecture
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr)  
**Document Reference:** `docs/architecture/data-fusion.md`  

---

## 1. Objective and Architectural Flow

Convective initiation, thunderstorm intensification, hail generation, and cloudburst events cannot be accurately nowcasted from single-sensor views alone. A radar reflectivity core may look identical for non-severe and severe storms without co-located lightning flash rate surges (indicating intense updrafts) and satellite rapid infrared cooling (indicating explosive cloud-top ascent).

The STORMNET Multi-Source Fusion Engine unifies heterogeneous observation modalities onto a **common 1–3 km spatial grid** across **synchronized temporal windows**:

```
 [Doppler Radar]       [INSAT Satellite]       [Lightning LLN]       [AWS Surface]
   (Reflectivity)          (TIR1 / CTT)           (Flashes)          (T, RH, Wind)
         |                      |                      |                   |
         v                      v                      v                   v
   [Validation]           [Validation]           [Validation]        [Validation]
         |                      |                      |                   |
         v                      v                      v                   v
 [Curved Earth 4/3]     [Mercator/WGS84]       [Point Coord]       [Station Coord]
         \                      |                      |                  /
          \                     |                      |                 /
           +--------------------+----------------------+----------------+
                                        |
                                        v
                       [Causal Temporal Synchronization]
                         (e.g., 5-minute sliding window)
                                        |
                                        v
                          [Spatial Grid Binning (3 km)]
                                        |
                                        v
                          [Feature Extraction & QC]
                                        |
                                        v
                                 [FusedGridFrame]
                                  /            \
                                 /              \
                                v                v
                      [PostGIS Persistence]   [FastAPI Endpoints]
                                |
                                v
                      [ML-Ready Parquet Export]
```

---

## 2. Normalized Fused Feature Schema

For each grid cell $g$ and temporal anchor window $t_k$, the fusion engine constructs a normalized feature record:

| Feature Category | Variable Name | Physical Unit | Missing Representation | Source Provider |
| :--- | :--- | :--- | :--- | :--- |
| **Radar** | `radar_reflectivity_dbz` | dBZ (15.0 to 75.0) | `null` + `MISSING` flag | IMD Doppler Weather Radar |
| **Radar** | `radar_max_dbz` | dBZ | `null` + `MISSING` flag | DWR Column Composite |
| **Radar** | `radar_precip_rate_mm_hr` | mm/h ($Z=200R^{1.6}$) | `null` + `MISSING` flag | DWR Derived Proxy |
| **Satellite** | `satellite_brightness_temp_k` | Kelvin (180 to 320) | `null` + `MISSING` flag | INSAT-3D/3DR TIR1 (10.8 µm) |
| **Satellite** | `satellite_cloud_cooling_rate_k_hr`| K/h | `null` + `MISSING` flag | Temporal Derivative $\Delta T / \Delta t$ |
| **Lightning** | `lightning_strike_count` | Count ($\ge 0$) | 0 (if sensor online) | IITM/IMD Lightning Network |
| **Lightning** | `lightning_density_per_km2` | strikes/$\text{km}^2$ | 0 (if sensor online) | Binned by Cell Area ($9\,\text{km}^2$) |
| **Lightning** | `lightning_rate_per_min` | strikes/min | 0 (if sensor online) | Count / Window Duration |
| **Lightning** | `lightning_trend` | Categorical | `STABLE` / `INCREASING` / `DECREASING` | Rate change vs preceding window |
| **Atmospheric**| `atmospheric_temp_c` | °C (-10 to 50) | `null` + `MISSING` flag | Surface AWS Telemetry |
| **Atmospheric**| `atmospheric_humidity_pct` | % (0 to 100) | `null` + `MISSING` flag | Surface AWS Telemetry |
| **Atmospheric**| `atmospheric_pressure_hpa` | hPa (900 to 1050) | `null` + `MISSING` flag | Surface AWS Telemetry |
| **Atmospheric**| `atmospheric_wind_speed_kmh` | km/h (0 to 200) | `null` + `MISSING` flag | Surface AWS Telemetry |

---

## 3. Graceful Missing Source Policy

The fusion engine is strictly deterministic and fault-tolerant. When an operational stream is offline or out of coverage:
1. The missing sensor feature values remain strictly `null` (never fabricated with artificial averages).
2. The `sensor_availability` boolean flags record the outage (`satellite_available: false`).
3. The `completeness_score` drops accordingly (e.g. 3 of 4 sources = $0.75$).
4. Downstream machine learning inference models receive explicit masking flags indicating absent modalities.

---

## 4. API Endpoints

- `GET /api/v1/fusion/latest?sector_id=delhi-ncr`: Returns the most recently synchronized fused grid frame.
- `GET /api/v1/fusion/{timestamp}`: Retrieves a historical or replay fused frame by timestamp.
- `GET /api/v1/fusion/grid/{grid_id}`: Retrieves multi-sensor time-series features for an individual 3 km cell.
- `GET /api/v1/fusion/status`: Operational sensor availability, stream latencies, and data freshness tier.
- `GET /api/v1/fusion/sources`: Enumerates registered meteorological adapters and health metrics.
