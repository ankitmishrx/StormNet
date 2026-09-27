# STORMNET — Data Leakage Prevention & Scientific Validation Protocol
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr)  
**Document Reference:** `docs/research/data-leakage-prevention.md`  

---

## 1. Threat Model: Temporal & Spatial Data Leakage in Meteorological Nowcasting

In operational meteorology and time-series nowcasting, subtle forms of data leakage can inflate apparent benchmark accuracy while leading to catastrophic failure during real convective events. STORMNET systematically defends against four primary vectors of data contamination:

```
+------------------------------------------------------------------------------------+
|                                 LEAKAGE VECTORS                                    |
+------------------------------------+-----------------------------------------------+
| Vector 1: Lookahead / Future Leak  | Ingesting radar/satellite scans with t > T_now|
| Vector 2: Convective Autocorrelation| Train/Test split across adjacent 5-min frames |
| Vector 3: Label Contamination      | Using future maximum reflectivity in features |
| Vector 4: Spatial Bleed            | Overlapping grid buffers between split sectors|
+------------------------------------+-----------------------------------------------+
```

---

## 2. Leakage Defense Mechanisms

### 2.1 Causal Windowing Verification
The temporal alignment module executes programmatic assertions before any feature is ingested into a fused grid cell:

```python
def assert_causal_integrity(observation_time: datetime, anchor_time: datetime) -> None:
    if observation_time > anchor_time:
        raise TemporalLeakageError(
            f"Causal violation: Observation timestamp {observation_time.isoformat()} "
            f"exceeds anchor window timestamp {anchor_time.isoformat()}."
        )
```

### 2.2 Event-Based Block Cross-Validation (Purging & Embargo)
Convective weather systems exhibit strong spatial and temporal autocorrelation ($> 0.85$ correlation across 15-minute frames of the same squall line). Standard random k-fold cross-validation or random frame splitting causes severe optimistic bias.

STORMNET mandates **Event-Based Block Splitting**:
1. **Event Quarantine:** A convective storm event (e.g. Western Disturbance passage on 2026-05-15) is treated as an indivisible atomic entity.
2. **Temporal Embargo:** A mandatory buffer of $\ge 24$ hours of quiet convective conditions separates training, validation, and test datasets.
3. **Spatial Separation:** When training on Delhi-NCR, validation must be held out either chronologically across distinct meteorological seasons or geographically on independent sectors (e.g., Mumbai MMR or Kolkata).

### 2.3 Strict Separation of Label Derivation
Convective hazard labels (e.g. Cloudburst $> 100$ mm/hr, Severe Hail $\ge 2$ cm diameter, Squall $\ge 60$ km/h) are derived strictly from forward-looking lead times:

$$y_{t+\Delta t} = f(\text{Observed Weather at } t+\Delta t)$$

Input features at time $t$ are derived strictly from backward-looking and instantaneous windows:

$$\mathbf{x}_t = g(\text{Observed Sensors at } \tau \le t)$$

Features must never include forward derivatives, cumulative rainfall from subsequent time steps, or future lightning strike bursts.

---

## 3. Automated Leakage Auditing in Pipeline

1. **Timestamp Monotonicity Check:** Verifies that all observations ingested for frame $t_k$ satisfy $t_{\text{obs}} \le t_k$.
2. **Duplicate Ingestion Quarantine:** Ensures identical observation hashes are not processed multiple times with distorted timestamps.
3. **Partition Boundary Integrity:** Verifies that training dataset partition IDs never intersect with test partition event dates.
