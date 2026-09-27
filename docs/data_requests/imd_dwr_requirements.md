# IMD Doppler Weather Radar Data Requirements Specification

## 1. Technical Data Requirements Matrix

The table below outlines the precise technical variables and metadata required to evaluate the STORMNET convective nowcasting pipeline:

| Requirement | Priority | Target Unit / Format | Purpose in STORMNET Architecture |
| :--- | :--- | :--- | :--- |
| **Reflectivity Factor ($Z$)** | **Critical** | dBZ ($-30.0\text{ to }+75.0$) | Primary input feature for detecting convective cores, cloudburst precipitation shafts, and cell boundaries. |
| **Observation Timestamp** | **Critical** | UTC / IST (ISO 8601) | Chronological sequence ordering, temporal alignment across sensors, and causal leakage prevention. |
| **Radar Antenna Coordinates** | **Critical** | WGS 84 Lat/Lon/Elevation | Georeferencing polar sweeps to the standard $1\text{--}3\text{ km}$ Cartesian target grid over Delhi NCR. |
| **Radial Doppler Velocity ($V_r$)**| **High** | m/s ($-60.0\text{ to }+60.0$) | Kinematic storm vector estimation, mesocyclone rotation, gust front detection, and microburst divergence. |
| **Elevation / Sweep Metadata** | **High** | Elevation angle ($^\circ$), sweep index | 3D volumetric reconstruction and Constant Altitude PPI (CAPPI) column compositing. |
| **Quality Flags & Clutter Masks** | **High** | Binary mask / Bitflags | Automated suppression of ground clutter, anomalous propagation, and sun spikes. |
| **Rainfall Product (QPE / PAC)** | **Optional** | mm / mm/hr | Calibrated surface precipitation ground truth for evaluating flash flood and cloudburst hazard heads. |
| **Differential Reflectivity ($Z_{DR}$)**| **Optional** | dB ($-4.0\text{ to }+8.0$) | Polarimetric hydrometeor classification and large hail verification ($Z_{DR} \approx 0$ with high $Z$). |
| **Specific Differential Phase ($K_{DP}$)**| **Optional** | deg/km | Heavy rain rate calibration immune to radar beam attenuation. |

---

## 2. Minimum Viable Scientific Data Request (MVDR)

To avoid imposing unnecessary archival retrieval overhead on IMD technical staff, STORMNET defines a **Minimum Viable Data Request**:

### Scope of Minimum Request:
1. **Radar Site**: Single station — **Delhi DWR** (Safdarjung or Palam).
2. **Event Count**: Exactly **3 to 5 discrete severe convective storm events** (rather than continuous multi-month archives).
3. **Event Window**: Consecutive volume scans spanning **3 to 6 hours per event** (e.g. 1 hour pre-initiation, 2–3 hours active convective lifecycle, 1–2 hours dissipation).
4. **Volume Scan Count**: At nominal 10-minute sampling, 18 to 36 volume scans per event $\implies$ total of **approximately 90 to 180 total volume files** ($< 2\text{ GB}$ total compressed data).

### Representative Candidate Event Windows in Delhi NCR:
- **Event 1 (Severe Pre-Monsoon Squall & Dust Storm)**: May 25, 2023 (14:00 to 20:00 IST).
- **Event 2 (Monsoon Convective Downburst & Thunderstorm)**: July 09, 2023 (06:00 to 15:00 IST — extreme NCR rainfall).
- **Event 3 (Intense Summer Thunderstorm & Hail Episode)**: April 13, 2024 (16:00 to 22:00 IST).
- **Event 4 (Record Monsoon Cloudburst / Extreme Rain Episode)**: June 28, 2024 (01:00 to 07:00 IST — record $228\text{ mm}$ event at Delhi Safdarjung).

### Fallback Policy if Event Extraction is Unavailable:
If extracting discrete historical event slices is not feasible under standard IMD operational procedures, StormNet requests guidance on a **single continuous 7-day to 14-day historical block** during the peak 2024 monsoon season (e.g. June 25 to July 08, 2024).
