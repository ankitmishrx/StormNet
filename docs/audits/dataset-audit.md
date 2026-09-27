# STORMNET — Dataset Audit & Provenance Verification
**Document ID:** `AUDIT-DATA-001`  
**Phase:** Phase 5.5 Scientific Verification  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Audit Date:** 2026-09-26  
**Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary

This audit establishes the provenance, classification, physical boundaries, and scientific authenticity of every dataset present in the STORMNET repository.

### Critical Classification Standard:
- **REAL:** Telemetry directly captured by physical meteorological instruments without synthetic alteration.
- **HISTORICAL:** Archived real observations from past convective storm events.
- **DEVELOPMENT / SAMPLE:** Curated semi-realistic test fixtures engineered to validate parsers, coordinate transforms, spatial gridding, and API serialization without live sensor credentials.
- **SYNTHETIC:** Numerically generated artificial data created by mathematical functions or random seeds.

**Repository Finding:**  
**100% of the datasets currently stored in the repository are classified as DEVELOPMENT / SAMPLE data.**  
There are **zero operational real-time feeds** and **zero fabricated pseudo-scientific datasets claiming to be live observations**.

---

## 2. Dataset-by-Dataset Audit

### Dataset 1: Delhi-NCR Radar Sample (`dwr_delhi_20260926_1545.json`)
- **File Location:** [`data/samples/radar/dwr_delhi_20260926_1545.json`](file:///e:/project/SIH%20project%202%20Stormnet/data/samples/radar/dwr_delhi_20260926_1545.json)
- **Classification:** **DEVELOPMENT / SAMPLE DATA**
- **Provenance / Origin:** Handcrafted JSON fixture modeling IMD Safdarjung C-Band Doppler Weather Radar (DWR-DEL-SAF).
- **Is it Real?** No.
- **Is it Historical?** No (synthesized against severe convective event geometry).
- **Is it Synthetic?** Yes (structured to IMD DWR product specifications).
- **Spatial Resolution:** Discrete irregular convective cores mapped to $3.0\text{ km}$ Cartesian grid.
- **Temporal Resolution:** Single volume scan timestep representing a 5-minute scan cycle.
- **Variables Present:**
  - `reflectivity_dbz`: Max 61.5 dBZ (convective core) down to 40.0 dBZ.
  - `marshall_palmer_rain_rate`: Derived via $Z = 200 R^{1.6}$.
- **Observation Timestamp:** `2026-09-26T10:15:00Z` (15:45 IST).
- **Geographic Coverage:** Delhi-NCR bounding box `[76.5°E, 28.0°N, 77.8°E, 29.2°N]` (WGS84 `EPSG:4326`).
- **Audit Verification:** Marked explicitly in metadata with `"source": "IMD Safdarjung C-Band DWR (SAMPLE / DEVELOPMENT)"` and `"is_sample": true`.

---

### Dataset 2: Delhi-NCR INSAT-3DR Satellite Sample (`insat_3dr_delhi_20260926_1545.json`)
- **File Location:** [`data/samples/satellite/insat_3dr_delhi_20260926_1545.json`](file:///e:/project/SIH%20project%202%20Stormnet/data/samples/satellite/insat_3dr_delhi_20260926_1545.json)
- **Classification:** **DEVELOPMENT / SAMPLE DATA**
- **Provenance / Origin:** Modeled after ISRO/IMD INSAT-3DR geostationary meteorological imager Rapid Scan Sector.
- **Is it Real?** No.
- **Is it Historical?** No.
- **Is it Synthetic?** Yes (calibrated to realistic physical Kelvin limits).
- **Spatial Resolution:** $4.0\text{ km}$ sub-satellite nadir resolution resampled to $3.0\text{ km}$.
- **Temporal Resolution:** 15-minute standard sector cadence (latency: 180 seconds).
- **Variables Present:**
  - `channel`: `TIR1_10.8UM` (Thermal Infrared 1).
  - `brightness_temperature_k`: Range $218.4\text{ K}$ (deep convective overshooting cloud top) to $298.0\text{ K}$ (warm ground).
  - `cooling_rate_k_hr`: Temporal trend (e.g., $-14.5\text{ K/hr}$ indicating rapid cloud top ascent).
- **Observation Timestamp:** `2026-09-26T10:15:00Z` (15:45 IST).
- **Geographic Coverage:** Delhi-NCR region `[76.5°E, 28.0°N, 77.8°E, 29.2°N]`.
- **Physical Bounds Audit:** Passes physical threshold validation ($150\text{ K} \le T_B \le 350\text{ K}$).

---

### Dataset 3: Delhi-NCR Lightning Location Network Sample (`lln_delhi_20260926_1545.json`)
- **File Location:** [`data/samples/lightning/lln_delhi_20260926_1545.json`](file:///e:/project/SIH%20project%202%20Stormnet/data/samples/lightning/lln_delhi_20260926_1545.json)
- **Classification:** **DEVELOPMENT / SAMPLE DATA**
- **Provenance / Origin:** Modeled after IITM Pune / Earth Networks Indian Lightning Location Network.
- **Is it Real?** No.
- **Is it Historical?** No.
- **Is it Synthetic?** Yes (calibrated burst pattern).
- **Spatial Resolution:** Point observations with spatial accuracy $\pm 250\text{ m}$.
- **Temporal Resolution:** Millisecond-level pulse resolution aggregated over 5-minute window (`300s`).
- **Variables Present:**
  - `event_type`: `CG` (Cloud-to-Ground) and `IC` (Intra-Cloud).
  - `peak_current_ka`: $-42.5\text{ kA}$ to $+18.2\text{ kA}$ (within $-500\text{ kA}$ to $+500\text{ kA}$ bounds).
  - `sensors_reporting`: $6$ to $8$ multi-lateration ground sensors.
- **Observation Timestamps:** 5 distinct strike events between `2026-09-26T10:11:15Z` and `2026-09-26T10:14:52Z` (all causally precede anchor `10:15:00Z`).
- **Geographic Coverage:** Delhi urban core (`28.61°N–28.64°N`, `77.19°E–77.23°E`).

---

### Dataset 4: Delhi Surface AWS Sample (`aws_delhi_20260926_1545.json`)
- **File Location:** [`data/samples/aws/aws_delhi_20260926_1545.json`](file:///e:/project/SIH%20project%202%20Stormnet/data/samples/aws/aws_delhi_20260926_1545.json)
- **Classification:** **DEVELOPMENT / SAMPLE DATA**
- **Provenance / Origin:** Modeled after IMD Delhi surface Automatic Weather Station network (Safdarjung, Palam, Ridge, Lodhi Road).
- **Is it Real?** No.
- **Is it Historical?** No.
- **Is it Synthetic?** Yes (thermodynamically consistent pre-squall surface conditions).
- **Spatial Resolution:** Point observation network with $\sim 10–15\text{ km}$ inter-station spacing.
- **Temporal Resolution:** 15-minute reporting cadence (latency: 300 seconds).
- **Variables Present:**
  - `temperature_c`: $33.2^\circ\text{C}$ to $35.1^\circ\text{C}$.
  - `relative_humidity_pct`: $69.0\%$ to $81.0\%$.
  - `pressure_hpa`: $1003.5\text{ hPa}$ to $1004.8\text{ hPa}$.
  - `wind_speed_kmh`: $18.0\text{ km/h}$ to $42.0\text{ km/h}$.
  - `wind_direction_deg`: Convective outflow directions ($70^\circ$ to $90^\circ$).
- **Observation Timestamp:** `2026-09-26T10:15:00Z`.
- **Geographic Coverage:** Delhi Metropolitan Region.

---

### Dataset 5: Multi-Source Fused Parquet Dataset (`fused_features_20260926_101500.parquet`)
- **File Location:** [`data/processed/fused/date=20260926/sector=delhi-ncr/fused_features_20260926_101500.parquet`](file:///e:/project/SIH%20project%202%20Stormnet/data/processed/fused/date=20260926/sector=delhi-ncr/fused_features_20260926_101500.parquet)
- **Classification:** **PROCESSED DERIVATIVE OF SAMPLE DATA**
- **Format:** Apache Parquet (Snappy compressed, columnar storage, 19.14 KB).
- **Record Count:** 1,935 rows (representing the full $45 \times 43$ Delhi-NCR grid mesh at $3.0\text{ km}$).
- **Spatial Resolution:** $3.0\text{ km}$ uniform grid cell centroids.
- **Temporal Resolution:** Aligned 5-minute synchronization window (`10:10:00Z` to `10:15:00Z`).
- **Features Fused:**
  1. Radar: `radar_reflectivity_dbz`, `radar_max_dbz`, `radar_precip_rate_mm_hr`.
  2. Satellite: `satellite_brightness_temp_k`, `satellite_cooling_rate_k_hr`.
  3. Lightning: `lightning_strike_count`, `lightning_density_per_km2`, `lightning_rate_per_min`, `lightning_trend`.
  4. Atmospheric: `atmospheric_temp_c`, `atmospheric_humidity_pct`, `atmospheric_pressure_hpa`, `atmospheric_wind_speed_kmh`.
  5. Quality: `quality_flags`, `composite_quality`.
- **Lineage Metadata Sidecar:** [`fused_features_20260926_101500_meta.json`](file:///e:/project/SIH%20project%202%20Stormnet/data/processed/fused/date=20260926/sector=delhi-ncr/fused_features_20260926_101500_meta.json) containing manifest UUID, sensor availability, and pipeline version `1.0.0`.

---

### Dataset 6: UI Demonstration Fixtures (`apps/web/data/sample/`)
- **File Locations:**
  - [`apps/web/data/sample/storms.ts`](file:///e:/project/SIH%20project%202%20Stormnet/apps/web/data/sample/storms.ts) (Storm cells: `ST-001`, `ST-002`, `ST-003`).
  - [`apps/web/data/sample/forecast.ts`](file:///e:/project/SIH%20project%202%20Stormnet/apps/web/data/sample/forecast.ts) (0 to 360 min forecast timeline frames).
- **Classification:** **FRONTEND UI DEMONSTRATION FIXTURES**
- **Purpose:** Power the interactive GIS map, storm selection, timeline scrubbing, and hazard cards when running without a live database or during frontend development.
- **Scientific Status:** Explicitly labeled in code and UI as:  
  `"Data Status: DEMO / SAMPLE DATA"` and `"STATUS: RESEARCH PROTOTYPE / NOT VALIDATED"`.

---

## 3. Data Integrity & Prohibited Practices Confirmation

1. **No Real Operational Data Claim:** At no point does the codebase claim that these sample JSON files represent real live telemetry from IMD or ISRO.
2. **No Data Fabrication Claim:** No synthetic values are presented as experimentally observed scientific truths.
3. **No Hidden Overfitting:** No neural network has been trained on these sample fixtures.
