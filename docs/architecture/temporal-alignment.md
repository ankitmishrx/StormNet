# STORMNET — Temporal Synchronization & Alignment Architecture
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr)  
**Document Reference:** `docs/architecture/temporal-alignment.md`  

---

## 1. Executive Summary

Meteorological sensors operate at distinct sampling cadences, transmission latencies, and physical trigger mechanisms:
- **Doppler Weather Radar (DWR):** Volume scans every 10–15 minutes (or 5-minute rapid scan mode).
- **Geostationary Satellites (INSAT-3D/3DR):** Full disk every 30 minutes; rapid sector scan every 15 minutes.
- **Lightning Location Network (IITM / IMD):** Event-driven microsecond pulse arrival; continuous real-time stream.
- **Automatic Weather Stations (AWS):** Periodic 15-minute or 1-hour surface telemetric packets.

To feed these disparate observations into a coherent spatio-temporal feature tensor for convective nowcasting, STORMNET establishes a **Causal Temporal Windowing Engine**.

```
Temporal Stream:
  Radar:       |-- Scan 14:00 --|                     |-- Scan 14:15 --|
  Satellite:         |-- Frame 14:04 --|                    |-- Frame 14:19 --|
  Lightning:   ..*..*....***...*..**..*..**....*...***..*..***...*..**
  AWS Surface:    [AWS 14:00]                            [AWS 14:15]

Common Sync Window [13:55:00 - 14:00:00] (T_anchor = 14:00:00):
  Radar:       Assigned (14:00:00)
  Satellite:   Assigned preceding frame (13:49:00 <= T <= 14:00:00)
  Lightning:   Aggregated strike count & density within [13:55:00, 14:00:00]
  AWS:         Interpolated or nearest observation <= 14:00:00
```

---

## 2. Synchronization Window Definition

A **Target Observation Window** $W(t_k)$ is defined by an anchor timestamp $t_k$ and a configurable window duration $\Delta t_w$:

$$W(t_k) = [t_k - \Delta t_w, \, t_k]$$

- **Default Window Duration ($\Delta t_w$):** 5 minutes (300 seconds), aligned with operational rapid-scan DWR intervals and high-convective evolution rates.
- **Cadence Options:** 5-minute (high-resolution rapid nowcast), 10-minute, or 15-minute (standard volume scan synoptic cycle).

### 2.1 Causal Constraint (Anti-Leakage Rule)
Under no circumstances may an observation with timestamp $t_{\text{obs}} > t_k$ be admitted into window $W(t_k)$:

$$\forall \, o \in W(t_k), \quad t_{\text{obs}}(o) \le t_k$$

Any observation where $t_{\text{obs}} > t_k$ is strictly rejected as a **Future Temporal Leakage Violation**.

---

## 3. Sensor-Specific Alignment Strategies

| Sensor Stream | Native Cadence | Alignment Strategy | Latency Tolerance | Missing Policy |
| :--- | :--- | :--- | :--- | :--- |
| **Radar (DWR)** | 10–15 min | Nearest-preceding volume scan within $[t_k - 15\,\text{min}, \, t_k]$ | $\le 15$ min | If no scan within 15 min, mark `RADAR_UNAVAILABLE` |
| **Satellite (INSAT)** | 15–30 min | Nearest-preceding cloud-top IR frame within $[t_k - 30\,\text{min}, \, t_k]$ | $\le 30$ min | If no frame within 30 min, mark `SATELLITE_UNAVAILABLE` |
| **Lightning (LLN)** | Continuous | Integral aggregation over $[t_k - \Delta t_w, \, t_k]$ | $\le 30$ sec | Strike count = 0 if no flashes detected |
| **AWS Surface** | 15–60 min | Nearest-preceding station report within $[t_k - 60\,\text{min}, \, t_k]$ | $\le 60$ min | Spatial IDW or cell mean; if all stations silent, mark `AWS_UNAVAILABLE` |

---

## 4. Multi-Horizon Sequence Construction

For sequential time-series input (e.g. feeding LSTM or ConvLSTM backbones in subsequent phases), the aligner produces a historical sliding window of length $L$:

$$S(t_k) = \left\{ W(t_k - (L-1)\Delta t_w), \, \dots, \, W(t_k - \Delta t_w), \, W(t_k) \right\}$$

- Standard Sequence Length $L = 4$ (representing $T-15\text{m}$, $T-10\text{m}$, $T-5\text{m}$, $T-0$).
- All frames in $S(t_k)$ maintain invariant cell coordinates $[x_i, y_j]$ across the entire sequence.

---

## 5. Drift and Staleness Classification

An observation $o$ associated with anchor $t_k$ is flagged based on temporal age $\delta t = t_k - t_{\text{obs}}(o)$:
- **VALID:** $\delta t \le \text{Threshold}_{\text{nominal}}$
- **STALE:** $\text{Threshold}_{\text{nominal}} < \delta t \le \text{Threshold}_{\text{max}}$
- **EXPIRED / UNAVAILABLE:** $\delta t > \text{Threshold}_{\text{max}}$ (feature replaced with `None` / `null`, never with fabricated numbers).
