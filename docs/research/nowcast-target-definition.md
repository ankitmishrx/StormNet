# STORMNET — Convective Nowcasting Target Definition & Sequence Specification
**Document ID:** `SPEC-NOWCAST-TARGET-001`  
**Phase:** Phase 6 Convective Nowcasting Engine  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Creation Date:** 2026-09-26  
**Status:** FORMALLY SPECIFIED & GROUNDED IN OBSERVATIONAL DATA  

---

## 1. Problem Formulation

The primary task of the STORMNET nowcasting engine is spatio-temporal extrapolation of multi-source meteorological observations over short-range horizons ($0–6\text{ hours}$), with primary empirical validation focused on the $0–60\text{ minute}$ convective initiation and advection window.

Mathematically, let $\mathcal{X}_{t} \in \mathbb{R}^{C \times H \times W}$ represent the fused multi-sensor grid state at observation time $t$. Given a causal input sequence of $T_{\text{in}}$ consecutive historical frames:
$$\mathbf{X}_{t} = \left( \mathcal{X}_{t - (T_{\text{in}}-1)\Delta t}, \, \mathcal{X}_{t - (T_{\text{in}}-2)\Delta t}, \, \dots, \, \mathcal{X}_{t} \right)$$
the model $f_{\theta}$ parameterizes the conditional distribution or deterministic expectation of future radar reflectivity fields over $T_{\text{out}}$ future lead steps:
$$\widehat{\mathbf{Y}}_{t} = f_{\theta}(\mathbf{X}_{t}) = \left( \widehat{Z}_{t + \Delta t}, \, \widehat{Z}_{t + 2\Delta t}, \, \dots, \, \widehat{Z}_{t + T_{\text{out}}\Delta t} \right)$$
where $\widehat{Z}_{t + k\Delta t} \in \mathbb{R}^{1 \times H \times W}$.

---

## 2. Input Features & Channel Definition ($C=4$)

The input features are derived directly from the Phase 5 multi-source fused grid (`ml/preprocessing/fusion/interfaces.py`):

| Channel Index | Meteorological Variable | Source Instrument | Raw Unit | Normalized Range $[0, 1]$ | Physical Meaning |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **$C_0$** | Composite Reflectivity ($Z$) | C-Band Doppler Radar | $\text{dBZ}$ | $Z_{\text{norm}} = \frac{\text{clamp}(Z, 0, 75)}{75.0}$ | Hydrometeor backscatter / precipitation core intensity |
| **$C_1$** | Brightness Temperature ($T_B$) | INSAT-3DR TIR1 ($10.8\,\mu\text{m}$) | $\text{Kelvin}$ | $T_{\text{norm}} = \frac{350.0 - \text{clamp}(T_B, 150, 350)}{200.0}$ | Cloud-top altitude / convective updraft vigor (colder = higher) |
| **$C_2$** | Lightning Strike Density ($D_L$) | Earth Networks / IITM LLN | $\text{strikes/km}^2$ | $D_{\text{norm}} = \frac{\text{clamp}(D_L, 0, 10)}{10.0}$ | Convective electrification / mixed-phase graupel collision |
| **$C_3$** | Surface Wind Speed ($V_{\text{sfc}}$) | Surface AWS Stations | $\text{km/h}$ | $V_{\text{norm}} = \frac{\text{clamp}(V_{\text{sfc}}, 0, 100)}{100.0}$ | Low-level convergence / cold pool outflow boundary |

*Zero Future Leakage:* Every frame in $\mathbf{X}_t$ strictly satisfies $t_{\text{frame}} \le t$.

---

## 3. Target Variable & Threshold Definitions

### 3.1 Primary Continuous Target
- **Target Variable:** Maximum column radar reflectivity factor $Z$ ($\text{dBZ}$) at future timesteps $t + \tau$.
- **Physical Reason for Selection:** Radar reflectivity is the fundamental ground-truth remote sensing measurement directly correlated with precipitation intensity, hail core presence, and convective storm boundaries.

### 3.2 Categorical Verification Thresholds
To evaluate meteorological skill scores (CSI, POD, FAR), predictions are evaluated at three standardized meteorological thresholds:

1. **Light Precipitation ($\tau \ge 20.0\text{ dBZ}$):**
   - Corresponds to rain rate $R \ge 0.65\text{ mm/hr}$.
   - Detects the broad footprint of convective rain showers and stratiform anvils.
2. **Moderate Convection / Heavy Showers ($\tau \ge 35.0\text{ dBZ}$):**
   - Corresponds to rain rate $R \ge 5.6\text{ mm/hr}$.
   - Detects active thunderstorm cells and localized convective downdrafts.
3. **Severe Convective Core / Hail Potential ($\tau \ge 45.0\text{ dBZ}$):**
   - Corresponds to rain rate $R \ge 23.7\text{ mm/hr}$ and high probability of graupel/hail aloft.
   - Triggers operational thunderstorm warnings and aviation alerts.

---

## 4. Spatial & Temporal Dimensions

- **Spatial Resolution:** $3.0\text{ km} \times 3.0\text{ km}$ uniform Cartesian grid (WGS84 `EPSG:4326`).
- **Domain Dimensions:** $H = 64, W = 64$ cells ($192\text{ km} \times 192\text{ km}$ spatial bounding box centered on Delhi-NCR).
- **Temporal Cadence ($\Delta t$):** $5\text{ minutes}$ ($300\text{ seconds}$).
- **Input Sequence Length ($T_{\text{in}}$):** $4\text{ frames}$ (Historical window: $t - 15\text{m}$, $t - 10\text{m}$, $t - 5\text{m}$, $t$).
- **Prediction Sequence Length ($T_{\text{out}}$):**
  - **MVP Validated Horizon:** $6\text{ frames}$ ($+5, +10, +15, +20, +25, +30\text{ minutes}$).
  - **Extended Architecture Horizon:** Up to $72\text{ frames}$ ($0–6\text{ hours}$ at 5-minute steps).

---

## 5. Target Construction Method

1. **Raw Ingestion:** Synchronized multi-source observations are binned into 5-minute causal windows via `MultiSourceFusionEngine`.
2. **Cell Array Mapping:** Feature values are indexed to a $64 \times 64$ grid tensor. Cells outside radar coverage or missing data are padded with zero and tagged in quality masks.
3. **Sequence Slicing:** A rolling window extracts paired sample tensors $(\mathbf{X}_t, \mathbf{Y}_t)$ where:
   - $\mathbf{X}_t = \mathcal{X}_{[t-3, t]}$ (shape: `[4, 4, 64, 64]`)
   - $\mathbf{Y}_t = Z_{[t+1, t+6]}$ (shape: `[1, 6, 64, 64]`)
4. **Leakage Check:** An automated assertion validates that $\min(\text{timestamps}(\mathbf{Y}_t)) > \max(\text{timestamps}(\mathbf{X}_t))$.
