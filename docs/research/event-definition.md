# STORMNET — Convective Weather Event Definition & Extraction Criteria
**Document ID:** `SPEC-EVENT-DEF-001`  
**Phase:** Phase 7 Multi-Year Historical Archive & Multi-Station Validation  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Creation Date:** 2026-09-26  
**Status:** FORMALLY SPECIFIED & STANDARDIZED  

---

## 1. Objective & Motivation

Machine learning nowcasting models evaluated on randomly shuffled individual radar frames suffer from extreme temporal autocorrelation leakage (often inflating apparent CSI scores above $0.85$ while failing completely during live operations). 

To ensure scientifically defensible cross-validation, the basic unit of training, validation, and evaluation in STORMNET must be a **continuous, mesoscale convective event**.

This specification defines the meteorological criteria used by the [`ConvectiveEventExtractor`](file:///e:/project/SIH%20project%202%20Stormnet/packages/shared/radar_archive/events.py) to automatically identify, segment, and catalog discrete storm episodes from continuous Doppler Weather Radar time series.

---

## 2. Event Extraction Criteria

An observation window is classified and extracted as a distinct **Convective Event** if and only if it satisfies all of the following four criteria:

### 2.1 Criterion 1: Intensity Threshold
- **Reflectivity Condition:** The maximum composite radar reflectivity within the radar observation domain must satisfy:
  $$Z_{\max} \ge 35.0\text{ dBZ}$$
- **Meteorological Justification:** In tropical and subtropical monsoonal environments (India), $35\text{ dBZ}$ marks the boundary between benign stratiform rain ($<35\text{ dBZ}$, rain rates $<5\text{ mm/hr}$) and active convective updrafts containing mixed-phase hydrometeors (graupel and supercooled water).

### 2.2 Criterion 2: Spatial Scale Threshold
- **Active Core Area:** At least 5 grid cells on the $3.0\text{ km} \times 3.0\text{ km}$ Cartesian mesh must simultaneously exceed $35.0\text{ dBZ}$:
  $$A_{\text{conv}} = N_{\ge 35\text{dBZ}} \times 9.0\text{ km}^2 \ge 45.0\text{ km}^2$$
- **Meteorological Justification:** Isolated single-pixel ground clutter or anomalous propagation (AP) spikes rarely exceed $45\text{ km}^2$. This threshold isolates organized multicell thunderstorms, supercells, or squall lines from point radar noise.

### 2.3 Criterion 3: Minimum Event Duration
- **Sustained Convection:** The convective conditions (Criteria 1 & 2) must persist continuously for:
  $$\Delta t_{\text{duration}} \ge 30\text{ minutes}$$
  (Equivalent to at least 6 consecutive 5-minute scans, or 3 consecutive 10-minute volume scans).
- **Meteorological Justification:** Short-lived thermal flutters that dissipate in $<20\text{ minutes}$ do not represent mesoscale hazard episodes suitable for nowcasting sequence construction.

### 2.4 Criterion 4: Temporal Boundary & Episode Termination
- **Break Tolerance:** An ongoing event terminates when the active core area falls below $45\text{ km}^2$ or $Z_{\max} < 35.0\text{ dBZ}$ for a continuous period of:
  $$\Delta t_{\text{break}} > 30\text{ minutes}$$
- If convective echoes redevelop after $>30\text{ minutes}$, a **new event ID** is assigned.

---

## 3. Standardized Event Metadata Schema

Every extracted event is indexed with the following immutable schema:

```json
{
  "event_id": "EVT-DWR-DEL-SAF-20240715-001",
  "station_id": "DWR-DEL-SAF",
  "start_time": "2024-07-15T12:00:00Z",
  "end_time": "2024-07-15T16:30:00Z",
  "duration_minutes": 270.0,
  "frame_count": 28,
  "peak_dbz": 62.5,
  "mean_convective_area_km2": 189.0,
  "geographic_extent": {
    "min_lat": 27.7,
    "max_lat": 29.5,
    "min_lon": 76.2,
    "max_lon": 78.2
  },
  "data_quality_score": 1.0,
  "sample_indices": [102, 103, 104, 105, 106]
}
```

---

## 4. Multi-Station Event Splitting Protocol

1. **Station Independence:** Events from separate radar stations (e.g. `DWR-DEL-SAF` vs `DWR-MUM-VER`) are partitioned independently.
2. **Whole-Event Atomicity:** No individual scan frame from an event can be split between Train and Test sets.
3. **Mandatory Temporal Embargo:** A minimum buffer of $\ge 24\text{ hours}$ (recommended $48\text{ hours}$) is enforced between the end timestamp of any training event and the start timestamp of any validation or test event.
