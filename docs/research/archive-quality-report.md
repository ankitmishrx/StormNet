# STORMNET — Historical Radar Archive Quality Control Report
**Document ID:** `QC-ARCHIVE-001`  
**Phase:** Phase 7 Multi-Year Historical Archive & Multi-Station Validation  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Creation Date:** 2026-09-26  
**Auditor:** Lead System Architect  
**Classification:** Archive-Level QC Audit  

---

## 1. Executive Summary

This report documents the execution of the [`ArchiveQualityController`](file:///e:/project/SIH%20project%202%20Stormnet/packages/shared/radar_archive/qc.py) pipeline across repository datasets and formalizes the QC pass/fail criteria required for any multi-year Doppler Weather Radar archive before admission into ML training.

---

## 2. Archive Audit Results Across Monitored Radar Stations

### 2.1 Summary Matrix

| Radar Station ID | Station Name | Available Scans | Valid Scans | Corrupted / Zero-Byte | Duplicate Scans | Temporal Gaps (>20m) | Pass Rate | Training Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`DWR-DEL-SAF`** | New Delhi Safdarjung | 1 (Sample) | 1 | 0 | 0 | 0 | **100.0%** | DEVELOPMENT SAMPLE ONLY |
| **`DWR-DEL-PAL`** | New Delhi Palam | 0 | 0 | 0 | 0 | 0 | **0.0%** | NOT AVAILABLE |
| **`DWR-MUM-VER`** | Mumbai Veravali | 0 | 0 | 0 | 0 | 0 | **0.0%** | NOT AVAILABLE |
| **`DWR-CHE-PRT`** | Chennai Port Trust | 0 | 0 | 0 | 0 | 0 | **0.0%** | NOT AVAILABLE |
| **`DWR-KOL-SUB`** | Kolkata NSCB Intl | 0 | 0 | 0 | 0 | 0 | **0.0%** | NOT AVAILABLE |

---

## 3. Detailed Quality Checks Implemented

The `ArchiveQualityController` evaluates each archive frame against nine automated checks:

1. **Zero-Byte / Truncated File Detection:**
   - Any file with size $= 0\text{ bytes}$ or premature EOF is flagged `CORRUPT` and quarantined.
2. **Duplicate Timestamp Resolution:**
   - Scans with matching observation timestamps are detected; only the first valid scan is retained, and duplicates are flagged `DUPLICATE`.
3. **Temporal Gap Detection:**
   - Any interval $>20\text{ minutes}$ between consecutive scans is logged as a `TEMPORAL_GAP`.
4. **Invalid Timestamps:**
   - Filenames with corrupted or non-chronological dates (e.g. month $>12$ or year $<2000$) are rejected as `INVALID_TIMESTAMP`.
5. **Coordinate Reference System (CRS) Conformity:**
   - Validates that bounding coordinates match the station's registered domain in EPSG:4326.
6. **Dimension Conformity:**
   - Requires $64 \times 64$ output cells after multi-station normalization.
7. **Reflectivity Value Range Limits:**
   - Minimum allowable: $-30.0\text{ dBZ}$.
   - Maximum allowable: $+80.0\text{ dBZ}$.
   - Out-of-range anomalies (e.g. $>100\text{ dBZ}$ transmitter spikes) are clipped or quarantined.
8. **NaN / Inf Sentinels:**
   - Replaced deterministically with $0.0\text{ dBZ}$ (clean air) and logged.
9. **Missing Variables:**
   - Ensures mandatory maximum reflectivity product (`MAX_Z`) is present before proceeding.

---

## 4. Minimum Scientific Thresholds for Multi-Year Training

For any historical archive to be deemed admissible for model retraining in Phase 8:
- Minimum valid scans per convective season: $\ge 1,000\text{ scans}$.
- Overall archive pass rate: $\ge 90.0\%$.
- Continuous coverage without unlogged multi-hour gaps during active convective hours (11:00 to 22:00 IST).
