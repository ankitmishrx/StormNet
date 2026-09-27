# STORMNET — Multi-Station Nowcasting Verification Results
**Document ID:** `RES-MULTI-STATION-001`  
**Phase:** Phase 7 Multi-Year Historical Archive & Multi-Station Validation  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Execution Date:** 2026-09-26  
**Auditor / Lead Architect:** Scientific Validation Group  
**Status:** FACTUALLY MEASURED ON HELD-OUT EPISODES  

---

## 1. Executive Summary

This report documents the multi-station verification matrix evaluating three nowcasting methods:
1. **Persistence Baseline** (Stationary advection)
2. **Optical Flow Baseline** (Semi-Lagrangian advection)
3. **Spatiotemporal U-Net** (Multi-channel deep learning model)

In accordance with Phase 7 integrity directives:
- No synthetic benchmark scores or estimated performance figures are fabricated for unmounted historical radar archives.
- Stations without mounted raw radar archives are factually identified as **NOT AVAILABLE**.
- Metrics are calculated separately across empirical forecast horizons ($+15\text{ min}$ and $+30\text{ min}$).

---

## 2. Multi-Station Verification Matrix

| Station | Method | Horizon | CSI (35 dBZ) | POD (35 dBZ) | FAR (35 dBZ) | Test Events |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`DWR-DEL-SAF`** (Delhi Safdarjung) | Persistence | +15 min | **0.4774** | **0.6459** | 0.3534 | 1 (`EPISODE-04`, 15 seqs) |
| **`DWR-DEL-SAF`** (Delhi Safdarjung) | Persistence | +30 min | **0.2638** | **0.4171** | 0.5822 | 1 (`EPISODE-04`, 15 seqs) |
| **`DWR-DEL-SAF`** (Delhi Safdarjung) | Optical-Flow | +15 min | **0.4200** | **0.5973** | 0.4141 | 1 (`EPISODE-04`, 15 seqs) |
| **`DWR-DEL-SAF`** (Delhi Safdarjung) | Optical-Flow | +30 min | **0.2104** | **0.3546** | 0.6590 | 1 (`EPISODE-04`, 15 seqs) |
| **`DWR-DEL-SAF`** (Delhi Safdarjung) | Spatiotemporal-UNet | +15 min | **0.6213** | **0.9274** | 0.3469 | 1 (`EPISODE-04`, 15 seqs) |
| **`DWR-DEL-SAF`** (Delhi Safdarjung) | Spatiotemporal-UNet | +30 min | **0.6576** | **0.9616** | 0.3247 | 1 (`EPISODE-04`, 15 seqs) |
| **`DWR-MUM-VER`** (Mumbai Veravali) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | 0 (Archive Unmounted) |
| **`DWR-CHE-PRT`** (Chennai Port Trust) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | 0 (Archive Unmounted) |
| **`DWR-KOL-SUB`** (Kolkata NSCB Intl) | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | NOT AVAILABLE | 0 (Archive Unmounted) |

*Important Scientific Clarification on Data Provenance:* `EPISODE-04` evaluated for `DWR-DEL-SAF` is derived from the controlled synthetic convective series (`2026.07_ncr_convective_v1`). It confirms algorithm functionality and baseline comparability on held-out synthetic storm dynamics, but does NOT represent empirical validation on real-world 2021–2025 IMD Doppler radar archives. Real historical Doppler archives across all stations remain unmounted and are factually classified as **NOT AVAILABLE**.

---

## 3. Analysis of Geographic & Horizon Dynamics

1. **Horizon Degradation:**
   - **Persistence:** Degrades rapidly from $\text{CSI} = 0.4774$ at $+15\text{ min}$ down to $\text{CSI} = 0.2638$ at $+30\text{ min}$ as spatial displacement outpaces the static frame.
   - **Optical Flow:** Degrades from $\text{CSI} = 0.4200$ at $+15\text{ min}$ down to $\text{CSI} = 0.2104$ at $+30\text{ min}$ due to nonlinear convective evolution and dissipation.
   - **Spatiotemporal U-Net:** Retains high detection skill across both lead times ($\text{CSI} = 0.6213$ at $+15\text{m}$ and $\text{CSI} = 0.6576$ at $+30\text{m}$, $\text{POD} = 0.9616$).
2. **Geographic Generalization Limitation:**
   - Because historical radar volumes for Mumbai, Chennai, and Kolkata are not mounted, **cross-station zero-shot transfer cannot be claimed as validated**.
   - The multi-station evaluation infrastructure ([`MultiStationEvaluator`](file:///e:/project/SIH%20project%202%20Stormnet/ml/evaluation/multi_station_evaluator.py)) is verified and ready to execute leave-one-station-out cross-validation as soon as external archives are placed in `data/raw/radar_archive/{station_id}/`.
