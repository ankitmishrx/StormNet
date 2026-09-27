# Phase 8.5 — Data Readiness Audit

**Document Identifier:** `AUDIT-PHASE8.5-DATA-READINESS`  
**Problem Statement:** SIH26084 (Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Audit Date:** 2026-09-26  
**Auditor:** Scientific Validation & Provenance Audit Group  
**Classification:** Scientific Integrity & Data Readiness Audit  

---

## Executive Status

- **IMD DWR:** **NOT AVAILABLE** (0 files in `data/external/imd_radar/`; 1 development sample scan in `data/samples/radar/`)
- **INSAT:** **NOT AVAILABLE** (0 files in `data/external/insat/`; 1 development sample frame in `data/samples/satellite/`)
- **Lightning:** **NOT AVAILABLE** (0 files in `data/external/lightning/`; 1 development sample feed in `data/samples/lightning/`)
- **Rain Gauge:** **NOT AVAILABLE** (0 files in `data/external/rain_gauge/`; 1 development sample feed in `data/samples/aws/`)

---

## Dataset Inventory

| Dataset | Provider | Type | Files | Coverage | Status |
|---|---|---|---:|---|---|
| `data/external/imd_radar/` | IMD / MoES | Real Doppler Radar | 0 | None (Empty dropzone, only `.gitkeep`) | **NOT AVAILABLE** |
| `data/external/insat/` | ISRO SAC / MOSDAC | Real Satellite Products | 0 | None (Empty dropzone, only `.gitkeep`) | **NOT AVAILABLE** |
| `data/external/lightning/` | IITM Pune / MoES | Real Lightning Feed | 0 | None (Empty dropzone, only `.gitkeep`) | **NOT AVAILABLE** |
| `data/external/rain_gauge/` | IMD / State SDMAs | Real Rain Gauge Logs | 0 | None (Empty dropzone, only `.gitkeep`) | **NOT AVAILABLE** |
| `data/samples/radar/dwr_delhi_20260926_1545.json` | IMD (Mock) | Sample JSON Scan | 1 | Delhi-NCR (20 cells, single snapshot) | `SAMPLE_DATA` |
| `data/samples/satellite/insat_3dr_delhi_20260926_1545.json` | INSAT-3DR (Mock) | Sample JSON Frame | 1 | Delhi-NCR (4 points, single snapshot) | `SAMPLE_DATA` |
| `data/samples/lightning/lln_delhi_20260926_1545.json` | IITM (Mock) | Sample JSON Feed | 1 | Delhi-NCR (5 strikes, single 5-min window) | `SAMPLE_DATA` |
| `data/samples/aws/aws_delhi_20260926_1545.json` | IMD AWS (Mock) | Sample JSON Feed | 1 | Delhi-NCR (4 stations, single snapshot) | `SAMPLE_DATA` |
| `data/processed/fused/...parquet` | STORMNET Pipeline | Gridded Multimodal Tensor | 1 | Delhi-NCR ($1,935$ spatial grid cells) | `SAMPLE_DATA` (Derived) |
| `experiments/exp_001_spatiotemporal_unet/...pt` | Synthetic Kinematic Generator | Synthetic Weights | 3 | Synthetic 2D Gaussian Convective Cores | `SYNTHETIC_DATA` |

---

## Provenance Verification

Every data artifact in the repository is strictly classified according to the STORMNET provenance standard:

1. **`REAL_AUTHORIZED_DATA`:** **0 files present**. No authenticated live or archival observations from IMD, ISRO MOSDAC, or IITM are physically mounted in the environment.
2. **`HISTORICAL_DATA`:** **0 files present**. Zero multi-year ($2021–2025$) Doppler Weather Radar volume files exist across Delhi, Mumbai, Chennai, and Kolkata.
3. **`SAMPLE_DATA`:** **4 sample fixtures + 1 derived parquet partition**. Used exclusively for unit testing, schema validation, and end-to-end software integration.
4. **`SYNTHETIC_DATA`:** **4 episodes (60 sequences) in `exp_001`**. Controlled mathematical test simulations using 2D Gaussian convective cells with physical decay.
5. **`REPLAY_DATA`:** **0 files present**. No operational stream replays are active.

---

## Pipeline Verification

- **Executed Runs:** The ingestion, validation, and registration pipeline was executed exclusively on the development sample radar file (`data/samples/radar/dwr_delhi_20260926_1545.json`), successfully creating manifest `data/manifests/sample_delhi_radar.json` and validation report `reports/data-validation/sample_delhi_radar.json`.
- **Real Data Execution:** The pipeline was **NOT EXECUTED on real observational data** because zero legitimate observational files exist in `data/external/`.
- Zero execution results have been fabricated.

---

## Model Validation Status

- **Development Validation:** **VERIFIED**. Core software pipelines, tensor transformations, API contracts, and GIS visualizations are verified and passing 63 of 63 automated tests.
- **Synthetic Validation:** **VERIFIED**. Spatiotemporal U-Net was benchmarked against Persistence and Optical Flow baselines on controlled synthetic convective simulations (`exp_001_spatiotemporal_unet`).
- **Historical Validation:** **NOT VERIFIED / NOT EXECUTED**. Zero multi-year radar archive files exist.
- **Real-World Validation:** **NOT VERIFIED / NOT EXECUTED**. Zero physical radar observations or ground-truth rain gauge measurements have been ingested into the model.

---

## Blockers

1. **Institutional Data Access:** Absence of an active National Data Centre (NDC) Pune institutional credential or MoES research agreement to access raw Doppler Weather Radar volume files.
2. **Satellite Archive Retrieval:** Absence of registered MOSDAC user credentials / OpenSearch API tokens to download INSAT-3D/3DR HDF5 products.
3. **Ground Truth Validation Data:** Absence of physical rain-gauge network records (IMD AWS/ARG) for real-world QPE calibration.

---

## Exact Next Step

Submit a formal data requisition under SIH26084 to the India Meteorological Department National Data Centre (IMD NDC, Pune) requesting 5 severe convective storm events in WMO ODIM_H5 format for radar station `DWR-DEL-SAF` from the 2024 monsoon season.
