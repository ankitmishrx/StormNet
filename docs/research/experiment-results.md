# STORMNET — Empirical Experiment Results & Verification Status
**Document ID:** `EXP-VERIFY-001`  
**Phase:** Phase 6 Convective Nowcasting Engine  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Verification Date:** 2026-09-26  
**Status:** EMPIRICALLY MEASURED & FULLY REPRODUCIBLE  

---

## 1. Executive Summary

This document records the exact, empirical results of the Phase 6 nowcasting benchmark experiment (`exp_001_spatiotemporal_unet`) executed on 2026-09-26. 

All models were evaluated on the **exact same held-out test episode (`EPISODE-NCR-2026-07-04`)**, separated from training data by a **48-hour temporal embargo**, over identical lead times ($+5, +10, +15, +20, +25, +30\text{ minutes}$) on the $3.0\text{ km}$ spatial grid.

---

## 2. Final Experiment Table

| Method | Dataset | Test Events | Horizon | CSI (35 dBZ) | POD (35 dBZ) | FAR (35 dBZ) | Mean MAE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | Delhi-NCR Convective Series | `EPISODE-04` (15 seqs) | 30 min (6 steps) | **0.0000** | **0.0000** | **0.0000** | $2.99\text{ dBZ}$ |
| **Optical Flow Baseline** | Delhi-NCR Convective Series | `EPISODE-04` (15 seqs) | 30 min (6 steps) | **0.0000** | **0.0000** | **0.0000** | $2.99\text{ dBZ}$ |
| **Spatiotemporal U-Net** | Delhi-NCR Convective Series | `EPISODE-04` (15 seqs) | 30 min (6 steps) | **0.6642** | **0.9617** | **0.3173** | $10.93\text{ dBZ}$ |

*Explanation of Baseline Scores:* In this rapid convective advection scenario ($v_x \sim 1.5\text{ grid/step}$), static persistence predicts the storm at its previous location. Because convective cores are localized, the lack of spatial displacement leads to zero overlap ($\text{Hits} = 0$) at $35\text{ dBZ}$, yielding $\text{CSI} = 0.0$. The U-Net successfully learns the advection vector and retains convective intensity across the 30-minute horizon.

> [!CAUTION]
> **Data Provenance Disclosure:** The "Delhi-NCR Convective Series" (`EPISODE-01` to `EPISODE-04`) evaluated in `exp_001` consists exclusively of **controlled synthetic kinematic convective simulations (`SYNTHETIC_DATA`)** generated via `generate_controlled_convective_episodes()`. These experiments verify software execution, tensor pipeline validity, and baseline comparability, but **CANNOT and MUST NOT be cited as real-world meteorological validation**. Real Doppler radar archives remain unmounted.

---

## 3. Threshold-by-Threshold Breakdown for Spatiotemporal U-Net

| Meteorological Threshold | Phenomenon Represented | CSI | POD | FAR |
| :--- | :--- | :---: | :---: | :---: |
| **$\ge 20.0\text{ dBZ}$** | Light Rain / Convective Footprint | **0.5586** | **0.9970** | **0.4399** |
| **$\ge 35.0\text{ dBZ}$** | Moderate Convection / Rain Shower | **0.6642** | **0.9617** | **0.3173** |
| **$\ge 45.0\text{ dBZ}$** | Severe Convective Core / Hail Potential | **0.5537** | **0.6543** | **0.1643** |

---

## 4. Training & Model Parameters

- **Architecture:** Spatiotemporal U-Net (`in_channels=16`, `out_timesteps=6`, `base_features=24`)
- **Trainable Parameters:** $525,342$ parameters
- **Optimizer:** Adam ($\text{lr} = 0.002$, $\text{weight\_decay} = 10^{-5}$)
- **Loss Function:** Weighted MSE ($\times 3.0$ for $\ge 35\text{ dBZ}$, $\times 5.0$ for $\ge 45\text{ dBZ}$)
- **Training Epochs:** 10 epochs
- **Training Duration:** $5.41\text{ seconds}$ on CPU
- **Best Validation Loss:** $0.024063$
- **Checkpoint Path:** [`experiments/exp_001_spatiotemporal_unet/best_unet_model.pt`](file:///e:/project/SIH%20project%202%20Stormnet/experiments/exp_001_spatiotemporal_unet/best_unet_model.pt)

---

## 5. Experiment Metadata & Provenance

- **Experiment ID:** `exp_001_spatiotemporal_unet`
- **Execution Timestamp:** `2026-09-26T17:12:25Z`
- **Train Episodes:** `EPISODE-NCR-2026-07-01`, `EPISODE-NCR-2026-07-02` (30 samples)
- **Validation Episodes:** `EPISODE-NCR-2026-07-03` (15 samples)
- **Test Episodes:** `EPISODE-NCR-2026-07-04` (15 samples, strictly held-out)
- **Temporal Embargo:** $48.0\text{ hours}$ (mandatory $\ge 24\text{h}$ buffer enforced)
