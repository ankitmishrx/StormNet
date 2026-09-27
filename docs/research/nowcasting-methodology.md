# STORMNET — Convective Nowcasting Methodology & Modeling Framework
**Document ID:** `METH-NOWCAST-001`  
**Phase:** Phase 6 Convective Nowcasting Engine  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Creation Date:** 2026-09-26  
**Status:** VALIDATED RESEARCH METHODOLOGY  

---

## 1. Problem Formulation

Convective-scale weather phenomena (severe thunderstorms, cloudbursts $>100\text{ mm/hr}$, destructive hail, and downbursts) are characterized by rapid lifecycle transitions ($\sim 30–120\text{ minutes}$) and localized spatial scales ($\sim 2–20\text{ km}$). Numerical Weather Prediction (NWP) models struggle at lead times $<3\text{ hours}$ due to spin-up latency and convective parameterization approximations.

STORMNET addresses this gap by formulating nowcasting as an empirical, data-driven spatio-temporal extrapolation problem over $0–6\text{ hours}$, with an MVP validated lead time of $0–30\text{ minutes}$ at $5\text{-minute}$ steps.

---

## 2. Input Data & Channels

The model ingests 4 synchronized physical observation channels across a 4-step lookback window $[t-15\text{m}, t-10\text{m}, t-5\text{m}, t]$:

1. **Radar Composite Reflectivity ($Z$):** C-Band Doppler radar reflectivity ($0–75\text{ dBZ}$) capturing hydrometeor mass.
2. **Satellite Brightness Temperature ($T_B$):** INSAT-3DR TIR1 channel ($150–350\text{ K}$) capturing cloud-top cooling and vertical expansion.
3. **Lightning Flash Density ($D_L$):** Ground-based multi-lateration network counting total flash pulses ($\text{strikes/km}^2$).
4. **Surface Wind Speed ($V_{\text{sfc}}$):** Automatic Weather Station anemometer observations capturing convective outflow gust fronts.

---

## 3. Target Definition

- **Target Variable:** Future column-maximum radar reflectivity $Z$ ($\text{dBZ}$) over $T_{\text{out}} = 6$ lead times ($+5, +10, +15, +20, +25, +30\text{ minutes}$).
- **Target Resolution:** $3.0\text{ km} \times 3.0\text{ km}$ spatial mesh on Delhi-NCR.
- **Evaluation Thresholds:**
  - $\tau = 20.0\text{ dBZ}$ (Light Rain / Echo Area)
  - $\tau = 35.0\text{ dBZ}$ (Moderate Convection)
  - $\tau = 45.0\text{ dBZ}$ (Severe Convective Core / Hail Aloft)

---

## 4. Spatiotemporal U-Net Architecture

The network utilizes a lightweight 2D-Temporal U-Net structure ($525,342$ parameters) designed for rapid CPU/GPU inference:
- **Input Layer:** Projects $(B, C \times T_{\text{in}} = 16, H=64, W=64)$ features into a 32-channel feature space.
- **Encoder:** 3 downsampling stages using $3 \times 3$ double convolutions, batch normalization, and LeakyReLU activations ($\alpha=0.1$) with $2 \times 2$ MaxPool.
- **Bottleneck:** Deep representation layer operating at $1/8$ spatial resolution ($8 \times 8$).
- **Decoder:** 3 transpose convolutional upsampling stages with concatenated skip connections to preserve fine convective boundary details.
- **Output Head:** $1 \times 1$ convolution producing $T_{\text{out}} = 6$ future normalized reflectivity frames with Sigmoid activation $[0, 1]$, subsequently rescaled to $[0, 75\text{ dBZ}]$.

---

## 5. Event-Blocked Training & Evaluation Protocol

To prevent catastrophic temporal leakage:
- Storm observations are grouped into **whole mesoscale episodes**.
- Episodes are split chronologically with a **mandatory $\ge 24\text{-hour}$ temporal embargo**.
- **Zero sample overlap:** Test episodes are never seen during training or validation.
- Normalization parameters are calculated exclusively from training episodes.

---

## 6. Meteorological Skill Metrics

Models are evaluated using standard contingency metrics derived from $2 \times 2$ confusion matrices (Hits $H$, Misses $M$, False Alarms $F$, Correct Negatives $C$):

$$\text{POD} = \frac{H}{H + M} \quad\quad \text{FAR} = \frac{F}{H + F} \quad\quad \text{CSI} = \frac{H}{H + M + F}$$

$$\text{MAE} = \frac{1}{N}\sum |Z_{\text{pred}} - Z_{\text{obs}}| \quad\quad \text{RMSE} = \sqrt{\frac{1}{N}\sum (Z_{\text{pred}} - Z_{\text{obs}})^2}$$

---

## 7. Limitations & Operational Scope

1. **Validated Horizon:** Currently validated on held-out episodes up to **$+30\text{ minutes}$**. Extrapolation beyond 30 minutes requires physical confidence decay.
2. **Heuristic Hazard Attribution:** Cloudburst and hail hazard probability cards remain a **Research Prototype** until direct multi-sensor ground-truth label integration occurs in subsequent phases.
3. **Hardware Requirements:** The $525\text{k}$-parameter U-Net runs on standard multi-core CPUs in $<15\text{ ms}$, ensuring full edge compatibility without requiring server GPUs.
