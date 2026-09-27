# STORMNET — Phase 7.5 Historical Data Availability & Validation Reality Check

**Document Identifier:** `AUDIT-PHASE7.5-DATA-REALITY`  
**Problem Statement:** SIH26084 (Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Audit Date:** 2026-09-26  
**Auditor:** Scientific Validation & Audit Group  
**Classification:** Scientific Integrity, Data Provenance & Reality Check Audit  

---

## 1. Actual Data Inventory

An exhaustive inspection of the local repository and filesystem was conducted. The complete, factual inventory of every dataset actually present is detailed below:

| Field | Dataset 1: Radar Sample | Dataset 2: Satellite Sample | Dataset 3: Lightning Sample | Dataset 4: AWS Sample | Dataset 5: Fused Features | Dataset 6: Model Checkpoint |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Filename / Path** | `data/samples/radar/dwr_delhi_20260926_1545.json` | `data/samples/satellite/insat_3dr_delhi_20260926_1545.json` | `data/samples/lightning/lln_delhi_20260926_1545.json` | `data/samples/aws/aws_delhi_20260926_1545.json` | `data/processed/fused/date=20260926/sector=delhi-ncr/fused_features_20260926_101500.parquet` | `experiments/exp_001_spatiotemporal_unet/best_unet_model.pt` |
| **Source** | `DEVELOPMENT_SAMPLE` (Mock of IMD Safdarjung DWR) | `DEVELOPMENT_SAMPLE` (Mock of INSAT-3DR TIR1) | `DEVELOPMENT_SAMPLE` (Mock of IITM Lightning Network) | `DEVELOPMENT_SAMPLE` (Mock of IMD AWS Network) | STORMNET Preprocessing Pipeline (`fuse_cli.py`) | STORMNET Training Pipeline (`train.py`) |
| **Type** | Sample | Sample | Sample | Sample | Sample (Derived) | Synthetic (Trained on synthetic) |
| **Station / Domain** | Delhi (`DWR-DEL-SAF`) | Delhi-NCR (`sector_id: delhi-ncr`) | Delhi-NCR (`sector_id: delhi-ncr`) | Delhi-NCR (Safdarjung, Palam, Noida, Gurugram) | Delhi-NCR (`sector_id: delhi-ncr`) | Synthetic Delhi proxy coordinates |
| **Date Range** | `2026-09-26T10:15:00Z` (Single snapshot) | `2026-09-26T10:12:00Z` (Single snapshot) | `2026-09-26T10:11:12Z` to `10:14:50Z` | `2026-09-26T10:15:00Z` (Single snapshot) | `2026-09-26T10:10:00Z` to `10:15:00Z` | Base date `2026-07-15` to `2026-07-21` (Synthetic) |
| **Number of Files** | 1 file (2,839 bytes) | 1 file (1,238 bytes) | 1 file (1,618 bytes) | 1 file (1,636 bytes) | 1 parquet (19,598 bytes) + 1 json (1,572 bytes) | 1 checkpoint (6,382,555 bytes) + 2 json reports |
| **Observations / Frames** | 1 frame (20 grid cells) | 1 frame (4 point observations) | 5 strike events | 4 station observations | 1 fused frame (1,935 spatial grid cells) | 60 sequences generated in-memory (4 episodes) |
| **Temporal Resolution** | Single snapshot | Single snapshot | Point strike events | Single snapshot | 5-minute aggregation window | 5-minute steps ($T_{\text{in}}=4$, $T_{\text{out}}=6$) |
| **Spatial Resolution** | Source 0.5 km, Target 3.0 km | 4.0 km | Point locations (approx 100 m) | Point stations | 3.0 km Cartesian grid (EPSG:4326) | $64 \times 64$ tensor grid |
| **Variables** | `reflectivity_dbz`, `quality_flag` | `brightness_temp_kelvin`, `cloud_top_temp_kelvin`, `cooling_rate_k_hr` | `type`, `peak_current_ka`, `polarity`, `sensors_participating`, `chi_sq` | `temperature_c`, `humidity_pct`, `pressure_hpa`, `wind_speed_kmh`, `precipitation_rate_mmh` | 24 multi-sensor features (radar, sat, ltg, atm, quality) | 4 input channels (radar, sat, ltg, wind); 1 output (radar dBZ) |
| **File Format** | JSON | JSON | JSON | JSON | Apache Parquet / JSON | PyTorch binary (`.pt`) / JSON |

*Raw Data Directory (`data/raw/`):* **EMPTY (0 files, 0 bytes)**.  
*Historical Radar Data ($2021–2025$):* **0 files present**.

---

## 2. Station Coverage

Evaluation of actual data presence against the four configured target stations in `config/radar_stations.yaml`:

| Configured Station | Hardware / Frequency | Actual Files in Repository | Coverage Status |
| :--- | :--- | :---: | :--- |
| **Delhi** (`DWR-DEL-SAF` / `DWR-DEL-PAL`) | S-Band ($2.8\text{ GHz}$) / C-Band ($5.6\text{ GHz}$) | 1 sample JSON (`dwr_delhi_20260926_1545.json`) | **PARTIALLY AVAILABLE** (Sample only, no archive) |
| **Mumbai** (`DWR-MUM-VER`) | S-Band ($2.8\text{ GHz}$) | 0 files | **NOT AVAILABLE** |
| **Chennai** (`DWR-CHE-PRT`) | S-Band ($2.8\text{ GHz}$) | 0 files | **NOT AVAILABLE** |
| **Kolkata** (`DWR-KOL-SUB`) | S-Band ($2.8\text{ GHz}$) | 0 files | **NOT AVAILABLE** |

---

## 3. Multi-Year Coverage (2021–2025)

The following matrix records the factual presence of multi-year Doppler Weather Radar archives for all target stations:

| Year | Station | Data Available | Frames | Events |
| :---: | :--- | :---: | :---: | :---: |
| **2021** | Delhi (`DWR-DEL-SAF` / `DWR-DEL-PAL`) | **NOT AVAILABLE** | 0 | 0 |
| **2021** | Mumbai (`DWR-MUM-VER`) | **NOT AVAILABLE** | 0 | 0 |
| **2021** | Chennai (`DWR-CHE-PRT`) | **NOT AVAILABLE** | 0 | 0 |
| **2021** | Kolkata (`DWR-KOL-SUB`) | **NOT AVAILABLE** | 0 | 0 |
| **2022** | Delhi (`DWR-DEL-SAF` / `DWR-DEL-PAL`) | **NOT AVAILABLE** | 0 | 0 |
| **2022** | Mumbai (`DWR-MUM-VER`) | **NOT AVAILABLE** | 0 | 0 |
| **2022** | Chennai (`DWR-CHE-PRT`) | **NOT AVAILABLE** | 0 | 0 |
| **2022** | Kolkata (`DWR-KOL-SUB`) | **NOT AVAILABLE** | 0 | 0 |
| **2023** | Delhi (`DWR-DEL-SAF` / `DWR-DEL-PAL`) | **NOT AVAILABLE** | 0 | 0 |
| **2023** | Mumbai (`DWR-MUM-VER`) | **NOT AVAILABLE** | 0 | 0 |
| **2023** | Chennai (`DWR-CHE-PRT`) | **NOT AVAILABLE** | 0 | 0 |
| **2023** | Kolkata (`DWR-KOL-SUB`) | **NOT AVAILABLE** | 0 | 0 |
| **2024** | Delhi (`DWR-DEL-SAF` / `DWR-DEL-PAL`) | **NOT AVAILABLE** | 0 | 0 |
| **2024** | Mumbai (`DWR-MUM-VER`) | **NOT AVAILABLE** | 0 | 0 |
| **2024** | Chennai (`DWR-CHE-PRT`) | **NOT AVAILABLE** | 0 | 0 |
| **2024** | Kolkata (`DWR-KOL-SUB`) | **NOT AVAILABLE** | 0 | 0 |
| **2025** | Delhi (`DWR-DEL-SAF` / `DWR-DEL-PAL`) | **NOT AVAILABLE** | 0 | 0 |
| **2025** | Mumbai (`DWR-MUM-VER`) | **NOT AVAILABLE** | 0 | 0 |
| **2025** | Chennai (`DWR-CHE-PRT`) | **NOT AVAILABLE** | 0 | 0 |
| **2025** | Kolkata (`DWR-KOL-SUB`) | **NOT AVAILABLE** | 0 | 0 |

---

## 4. Actual Experiments

Determination of whether multi-station experiments were actually executed:

### 4.1 Real Multi-Station Experiments
- **Mumbai (`DWR-MUM-VER`):** **NOT EXECUTED** (No data mounted)
- **Chennai (`DWR-CHE-PRT`):** **NOT EXECUTED** (No data mounted)
- **Kolkata (`DWR-KOL-SUB`):** **NOT EXECUTED** (No data mounted)

### 4.2 Synthetic Single-Station Benchmark Execution (`DWR-DEL-SAF` Proxy)
- **Dataset:** Controlled synthetic convective series (`2026.07_ncr_convective_v1` generated via `generate_controlled_convective_episodes(seed=42)`)
- **Station:** `DWR-DEL-SAF` (Synthetic proxy coordinates)
- **Train/Test Period:** Synthetic timeline spanning 2026-07-15 to 2026-07-21 (Train: Episodes 1 & 2; Validation: Episode 3; Test: Episode 4)
- **Number of Events:** 4 synthetic mesoscale convective episodes (60 total sequences; 15 test sequences in held-out `EPISODE-04`)
- **Models Evaluated:** Persistence, Semi-Lagrangian Optical Flow, Spatiotemporal U-Net
- **Actual Measured Metrics:**

| Model | Forecast Horizon | CSI ($\ge 35\text{ dBZ}$) | POD ($\ge 35\text{ dBZ}$) | FAR ($\ge 35\text{ dBZ}$) | Test Event |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Persistence Baseline** | +15 min | **0.4774** | **0.6459** | 0.3534 | `EPISODE-04` (15 synthetic seqs) |
| **Persistence Baseline** | +30 min | **0.2638** | **0.4171** | 0.5822 | `EPISODE-04` (15 synthetic seqs) |
| **Optical Flow Baseline** | +15 min | **0.4200** | **0.5973** | 0.4141 | `EPISODE-04` (15 synthetic seqs) |
| **Optical Flow Baseline** | +30 min | **0.2104** | **0.3546** | 0.6590 | `EPISODE-04` (15 synthetic seqs) |
| **Spatiotemporal U-Net** | +15 min | **0.6213** | **0.9274** | 0.3469 | `EPISODE-04` (15 synthetic seqs) |
| **Spatiotemporal U-Net** | +30 min | **0.6576** | **0.9616** | 0.3247 | `EPISODE-04` (15 synthetic seqs) |

*Note on Measured Values:* These are exact measured values from deterministic execution. Zero real-world radar evaluations were executed.

---

## 5. Synthetic / Sample Data Audit

A repository-wide search for terms `synthetic`, `sample`, `mock`, `demo`, `fixture`, and `generated` confirms:

1. **`generate_controlled_convective_episodes` (`ml/experiments/run_experiment.py`):**
   - Implements a synthetic 2D Gaussian convective core generator with kinematic drift ($v_x, v_y$), physical decay, inverted thermal brightness temperature, lightning density proxies, and surface wind scaling.
   - **Involvement:** Directly used to create `EPISODE-01` through `EPISODE-04` used to train and evaluate `SpatiotemporalUNet`.
2. **`data/samples/radar/dwr_delhi_20260926_1545.json`:**
   - Sample JSON file used for radar preprocessing unit tests and single-scan API integration.
3. **`data/samples/satellite/`, `data/samples/lightning/`, `data/samples/aws/`:**
   - Single-scan sample JSON fixtures used to verify multi-source fusion alignment.

**Scientific Audit Ruling:**  
Synthetic datasets were actively involved in Phase 6 and Phase 7 testing. They serve solely to verify code paths, tensor dimensions, temporal embargo enforcement, and baseline comparability. **Under no circumstances do they constitute real-world meteorological validation.**

---

## 6. Claim Audit & Neutralization

The repository documentation was thoroughly audited for overreaching claims:

1. **"multi-year validated":** **0 occurrences** found.
2. **"multi-station validated":** **0 occurrences** found.
3. **"2021-2025 validated":** **0 occurrences** found.
4. **"real-world validated":** **0 occurrences** found.
5. **"operational":**
   - Used only in descriptive contexts: "operational standard" (UI design guidelines matching IMD/MoES forecaster ergonomics), "operational radar formats" (WMO ODIM_H5 specification), and system architecture specifications.
   - All documentation explicitly disclaims operational status:
     - `docs/audits/current-ml-status.md`: *"Do NOT claim operational deployment or equivalence to IMD/NCMRWF supercomputing infrastructure. STORMNET is a high-resolution research prototype."*
     - `docs/audits/final-phase6-status.md`: *"'Operational AI Forecast': Removed. The system is classified as an engineering prototype / research platform."*
6. **Ambiguity Neutralization:**
   - In `docs/audits/phase7-status.md`, Section 2.8 was amended to explicitly state that evaluation was performed exclusively on synthetic sequences for Delhi, and that real multi-station experiments for Mumbai, Chennai, and Kolkata were **NOT EXECUTED**.

---

## 7. Final Status

```yaml
DATA ACCESS: PARTIAL
MULTI-YEAR DATA: NOT AVAILABLE
MULTI-STATION DATA: NOT AVAILABLE
MULTI-STATION EVALUATION: PARTIAL
REAL-WORLD VALIDATION: NOT VERIFIED
SYNTHETIC DATA INVOLVEMENT: PRESENT
```

### Explanatory Summary:
- **DATA ACCESS: PARTIAL** — Single-scan developmental sample files exist for Delhi-NCR; raw historical Doppler Weather Radar archives are unmounted.
- **MULTI-YEAR DATA: NOT AVAILABLE** — Zero archive files present for years 2021, 2022, 2023, 2024, 2025 across all stations.
- **MULTI-STATION DATA: NOT AVAILABLE** — Zero data files present for Mumbai, Chennai, and Kolkata; only sample frame for Delhi.
- **MULTI-STATION EVALUATION: PARTIAL** — Evaluator infrastructure exists and executed on synthetic proxy data for Delhi (`DWR-DEL-SAF`); experiments for Mumbai, Chennai, and Kolkata were **NOT EXECUTED**.
- **REAL-WORLD VALIDATION: NOT VERIFIED** — No empirical validation against physical IMD radar observations has been conducted.
- **SYNTHETIC DATA INVOLVEMENT: PRESENT** — Training, validation, and testing of nowcasting models to date relied on controlled synthetic convective sequences (`generate_controlled_convective_episodes`).
