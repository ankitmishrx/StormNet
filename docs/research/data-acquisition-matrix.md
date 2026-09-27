# STORMNET Meteorological Data Acquisition Matrix & Modality Audit

## 1. Modality Mapping to STORMNET Operational Requirements

The table below maps the currently ingested dataset (`pub_noaa_isd_vidp_delhi_2024`) against all core capabilities required for 0–6 hour convective-scale nowcasting of thunderstorms, hail, and cloudbursts (SIH26084):

| Required Capability | Current Dataset | Available? | Needed Source | Operational Role |
| :--- | :--- | :--- | :--- | :--- |
| **Surface weather (T, Td, P, Wind)** | NOAA ISD | **YES** | NOAA ISD / IMD AWS | Boundary-layer thermodynamic stability, gust front & temperature drop verification |
| **Radar reflectivity (Column Max / CAPPI)** | NOAA ISD | **NO** | IMD DWR / Open Radar | Core convective core detection, precipitation intensity, updraft cell geometry |
| **Radar Doppler radial velocity** | NOAA ISD | **NO** | IMD DWR Level II | Mesocyclone rotation, microburst shear, storm divergence / convergence signatures |
| **Satellite thermal infrared (10.8 µm)** | NOAA ISD | **NO** | INSAT-3D/3DR/3DS / EUMETSAT | Cloud-top brightness temperature, rapid convective initiation detection before radar echoes |
| **Cloud-top microphysics & cooling rates**| NOAA ISD | **NO** | INSAT-3DR / MSG IODC | Cloud-top cooling rate ($\Delta T / \Delta t \le -10\text{ K/15 min}$), overshooting top identification |
| **Total lightning (IC + CG flashes)** | NOAA ISD | **NO** | IITM Damini / NASA ISS-LIS | Lightning jump algorithm, convective electrification, severe updraft proxy |
| **High-resolution quantitative precipitation** | NOAA ISD | **PARTIAL** (single gauge) | DWR QPE / Rain Gauge Mesonet / GPM | High-resolution precipitation field ($1\text{ km}, 5\text{ min}$) for localized flash flood / cloudbursts |
| **Storm-cell tracking (TITAN / SCIT)** | NOAA ISD | **NO** | Doppler Radar / Satellite | Cell centroid tracking, propagation vector, cell merging / splitting dynamics |
| **Hail probability (POH / MESH)** | NOAA ISD | **NO** | Dual-Pol Radar + In-Situ | Differential reflectivity ($Z_{DR}$) drop, high $Z$ above freezing level, ground hail reports |
| **Downburst / Microburst detection** | NOAA ISD | **PARTIAL** (surface gust only)| Radar Velocity + Surface AWS | Low-level velocity divergence signature paired with surface wind gust and pressure jump |
| **Cloudburst detection ($\ge 100\text{ mm/hr}$)**| NOAA ISD | **NO** | Radar QPE + Gauge Array | Spatial contiguous area accumulation ($100\text{ mm/hr}$ over $\approx 20\text{--}30\text{ km}^2$) |

---

## 2. Minimum Scientifically Meaningful Real Data Stack

To train, evaluate, and operationally deploy a defensible convective nowcasting model (0–6 hours at 1–3 km grid resolution), the system requires the following **five-modality data stack**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   MINIMUM REAL DATA STACK FOR STORMNET                 │
└────────────────────────────────────────────────────────────────────────┘
          │                                  │
          ▼                                  ▼
   RADAR (Primary)                    SATELLITE (Complement)
   • Max Reflectivity (dBZ)           • TIR1 10.8 µm Brightness Temp (K)
   • Radial Velocity (m/s)            • Water Vapor 6.8 µm Band
   • 1–3 km, 5–10 min                 • Cloud-Top Cooling Rate (K/hr)
   • Lead time: 0–2 hr                • 3–4 km, 15 min; Lead time: 0–6 hr
          │                                  │
          ├─────────────────┬────────────────┘
          ▼                 ▼
   LIGHTNING (Auxiliary)  SURFACE OBSERVATIONS (Validation & Constraint)
   • Total Flash Count    • 2 m Temperature (°C), Dew Point (°C)
   • Flash Density/km²    • Surface Pressure (hPa), 10 m Wind Speed/Gust (km/h)
   • 1–3 km, 5 min        • In-situ point telemetry; 15–30 min cadence
          │
          ▼
   HIGH-RESOLUTION PRECIPITATION (Target Ground Truth)
   • Calibrated Rain Rate (mm/hr)
   • 1–3 km, 15–30 min
```

### Detailed Modality Specifications:

### A. Doppler Weather Radar
- **Required Variables**: Reflectivity factor ($Z$, dBZ), Volume scan elevations, Radial Doppler velocity ($V_r$, m/s), Spectrum width ($W$).
- **Ideal Spatial Resolution**: $1.0\text{ km} \times 1.0\text{ km}$ Cartesian CAPPI / Max-Z composite.
- **Acceptable Temporal Resolution**: $5\text{ to }10\text{ minutes}$.
- **Historical Period Required**: At least 2 full convective seasons (Monsoon and Pre-monsoon, e.g. 2023–2024, $\approx 50\text{--}100$ severe convective storm events).
- **Geographic Coverage Required**: Delhi NCR radar umbrella ($250\text{ km}$ radius centered on $28.59^\circ\text{ N}, 77.22^\circ\text{ E}$).
- **Role in Model**: **Primary predictive backbone**. Supplies input frames $T-30\text{ to }T_0$ and target frames $T_0\text{ to }T+6\text{ hr}$ for spatiotemporal extrapolation and convective development modeling.

### B. Geostationary Satellite Imagery
- **Required Variables**: Thermal Infrared ($10.8\text{ µm}$ brightness temperature), Water Vapor channel ($6.7\text{--}7.3\text{ µm}$ mid-tropospheric moisture), Visible channel (daytime cloud optical thickness).
- **Ideal Spatial Resolution**: $3.0\text{ to }4.0\text{ km}$.
- **Acceptable Temporal Resolution**: $15\text{ minutes}$ (standard scan) or $5\text{ minutes}$ (rapid scan).
- **Historical Period Required**: Synchronous with radar historical archive ($2023\text{--}2024$).
- **Geographic Coverage Required**: Regional domain covering Northern/Central India ($20^\circ\text{--}35^\circ\text{ N}, 70^\circ\text{--}85^\circ\text{ E}$).
- **Role in Model**: **Pre-convective initiation and synoptic context**. Detects rapid cumulus cloud-top cooling 30–60 minutes before the first radar echo appears; tracks storm anvils and synoptic cloud shields over 2–6 hour horizons where radar advection degrades.

### C. Total Lightning Detection
- **Required Variables**: Flash timestamp, geodetic coordinates, strike type (Cloud-to-Ground / Intra-Cloud), peak current (kA).
- **Ideal Spatial Resolution**: Binned to $1.0\text{ to }3.0\text{ km}$ grid cells.
- **Acceptable Temporal Resolution**: $5\text{ minutes}$.
- **Historical Period Required**: Synchronous with radar storm events.
- **Geographic Coverage Required**: Domain covering Delhi NCR and surrounding states (Haryana, UP, Rajasthan, Punjab).
- **Role in Model**: **Severe weather trigger & hazard head feature**. Lightning jumps correlate directly with intense updraft surges, large hail probability, and microburst generation.

### D. Surface Weather Observations (Current Status: AVAILABLE via NOAA ISD)
- **Required Variables**: $2\text{ m}$ Air Temperature, Dew Point, Mean Sea Level Pressure, $10\text{ m}$ Wind Speed and Direction, Wind Gusts.
- **Ideal Spatial Resolution**: Dense mesonet ($10\text{--}20\text{ km}$ station spacing across NCR). Single airport site (VIDP) currently available.
- **Acceptable Temporal Resolution**: $15\text{ to }30\text{ minutes}$.
- **Historical Period Required**: 1–2 years (Full 2024 currently available).
- **Geographic Coverage Required**: Localized to target cities and surrounding airport stations.
- **Role in Model**: **Thermodynamic constraint & ground-truth validation**. Validates cold pool propagation, surface temperature drops, gust fronts, and pressure perturbations caused by convective downdrafts.

### E. Precipitation / Rain Gauge Ground Truth
- **Required Variables**: Accumulated precipitation (mm), instantaneous rainfall rate (mm/hr).
- **Ideal Spatial Resolution**: $1.0\text{ to }3.0\text{ km}$ gridded analysis.
- **Acceptable Temporal Resolution**: $15\text{ minutes}$.
- **Historical Period Required**: Synchronous with radar convective events.
- **Geographic Coverage Required**: Delhi NCR basin.
- **Role in Model**: **Quantitative Precipitation Forecast (QPF) loss function & cloudburst verification**. Calibrates radar reflectivity into surface rain rates ($Z\text{-}R$ relation) and validates localized cloudburst thresholds ($\ge 100\text{ mm/hr}$).

---

## 3. Investigation of Accessible Public Alternatives

The following candidate public datasets have been systematically audited for potential integration into STORMNET:

### 1. NASA GPM IMERG (Integrated Multi-satellitE Retrievals for GPM)
- **Provider**: NASA GES DISC / JAXA
- **Product**: GPM 3IMERGHHE (Early/Late Run) and 3IMERGHH (Final Run)
- **Spatial Resolution**: $0.1^\circ \times 0.1^\circ$ ($\approx 10\text{ km} \times 10\text{ km}$)
- **Temporal Resolution**: $30\text{ minutes}$
- **Geographic Coverage**: Global ($60^\circ\text{ S} - 60^\circ\text{ N}$), including all of India.
- **Variables**: Precipitation calibrated rate ($\text{mm/hr}$), precipitation uncalibrated rate, probability of liquid phase.
- **Historical Period**: June 2000 – Present.
- **Access Requirements**: Free NASA Earthdata account; automated HTTP downloads require basic HTTP auth token in `~/.netrc`.
- **License**: NASA Open Data Policy (Unrestricted).
- **India Coverage**: **Complete coverage** over all Indian states and oceanic waters.
- **Convective Nowcasting Suitability**: **Medium**. Excellent for regional quantitative precipitation estimation (QPE) and multi-hour accumulation trends.
- **Limitations**: **Spatial resolution ($10\text{ km}$) is too coarse** to resolve localized convective updrafts, tornadic supercells, or urban cloudbursts without downscaling.

### 2. ECMWF ERA5 Hourly Reanalysis
- **Provider**: European Centre for Medium-Range Weather Forecasts (ECMWF) / Copernicus Climate Change Service (C3S)
- **Product**: ERA5 Hourly Data on Single Levels and Pressure Levels
- **Spatial Resolution**: $0.25^\circ \times 0.25^\circ$ ($\approx 28\text{ km} \times 28\text{ km}$ or $31\text{ km}$ over tropics)
- **Temporal Resolution**: $1\text{ hour}$
- **Geographic Coverage**: Global, including India.
- **Variables**: Convective Available Potential Energy (CAPE), Convective Inhibition (CIN), Surface Pressure, Total Column Water, Vertical Wind Shear ($0\text{--}6\text{ km}$), $2\text{ m}$ Temperature, $2\text{ m}$ Dew Point.
- **Historical Period**: 1940 – Present (5-day latency).
- **Access Requirements**: Copernicus CDS API key (free registration required).
- **License**: Copernicus open license.
- **India Coverage**: **Complete coverage**.
- **Convective Nowcasting Suitability**: **Low-Medium**. Useful strictly as background thermodynamic conditioning (environmental CAPE, shear vectors) for machine learning feature fusion.
- **Limitations**: **Spatial resolution ($28\text{ km}$) and hourly frequency are far too coarse** for convective nowcasting; cannot resolve individual thunderstorm cells or fast-moving gust fronts.

### 3. EUMETSAT IODC (Indian Ocean Data Coverage) Meteosat-9/Meteosat-11
- **Provider**: EUMETSAT
- **Product**: SEVIRI Level 1.5 Image Data (Indian Ocean service at $45.5^\circ\text{ E}$)
- **Spatial Resolution**: $3.0\text{ km}$ (sub-satellite point) to $\approx 3.5\text{--}4.0\text{ km}$ over Northern India; $1.0\text{ km}$ High-Resolution Visible (HRV).
- **Temporal Resolution**: $15\text{ minutes}$.
- **Geographic Coverage**: Indian Ocean, Arabian Sea, Bay of Bengal, and Indian Subcontinent.
- **Variables**: 12 spectral channels (VIS0.6, VIS0.8, NIR1.6, IR3.9, WV6.2, WV7.3, IR8.7, IR9.7, IR10.8, IR12.0, IR13.4, HRV).
- **Historical Period**: Continuous operational archive for Indian Ocean service (2016 – Present).
- **Access Requirements**: Free registration on EUMETSAT Data Store; programmatic access via EUMDAC Python library or OAuth2 token.
- **License**: EUMETSAT Data Policy (Free for research and educational purposes).
- **India Coverage**: **Complete coverage of India and surrounding oceans**.
- **Convective Nowcasting Suitability**: **Very High**. Excellent geostationary alternative to INSAT-3D for thermal infrared cloud-top monitoring, overshooting top detection, and pre-convective cooling rates.
- **Limitations**: Slanted viewing angle over Northern India ($45.5^\circ\text{ E}$ geostationary orbital slot means view angle $\approx 45^\circ\text{--}50^\circ$ over Delhi NCR, requiring parallax correction).

### 4. MIT SEVIR (Storm Event Imagery & Radar Dataset)
- **Provider**: MIT Lincoln Laboratory / AWS Open Data
- **Product**: Spatiotemporal aligned sequences of NEXRAD VIL, GOES IR069, IR107, VIS, and GLM flashes.
- **Spatial Resolution**: $1.0\text{ km}$ (VIL), $2.0\text{ km}$ (IR), $0.5\text{ km}$ (VIS).
- **Temporal Resolution**: $5\text{ minutes}$.
- **Geographic Coverage**: Continental United States (CONUS).
- **Variables**: Vertically Integrated Liquid (VIL), Brightness Temperatures, Lightning Flash counts.
- **Historical Period**: 2018–2019 (10,000+ severe convective events).
- **Access Requirements**: Open AWS S3 bucket (`s3://sevir`), no credentials or API key required.
- **License**: CC BY 4.0.
- **India Coverage**: **NONE** (CONUS only).
- **Convective Nowcasting Suitability**: **Very High for Model Architecture Pre-training**. Provides the exact multi-sensor alignment required by STORMNET.
- **Limitations**: Cannot validate Indian weather phenomena (monsoon cloudbursts, western disturbances, nor'westers).

### 5. NASA ISS-LIS (Lightning Imaging Sensor on ISS)
- **Provider**: NASA Global Hydrology Resource Center (GHRC) DAAC
- **Product**: ISS LIS Quality Controlled Science Data (HDF4/HDF5)
- **Spatial Resolution**: $\approx 4.0\text{ km}$ at nadir.
- **Temporal Resolution**: Orbital pass sampling ($\approx 90\text{ seconds}$ viewing window per overpass).
- **Geographic Coverage**: Tropical and subtropical latitudes ($55^\circ\text{ S} - 55^\circ\text{ N}$), including all of India.
- **Variables**: Total lightning optical event, group, and flash coordinates, radiance, pulse duration.
- **Historical Period**: 2017 – 2023.
- **Access Requirements**: Free NASA Earthdata credentials.
- **License**: NASA Open Data Policy.
- **India Coverage**: **Yes** (during orbital overpasses).
- **Convective Nowcasting Suitability**: **Low for operational real-time nowcasting** (non-geostationary low-Earth orbit); **High for lightning model calibration and climatology**.
- **Limitations**: Low-Earth orbit does not provide continuous 24/7 monitoring over any single Indian city.

---

## 4. Master Data Acquisition Matrix

| Modality | Current Dataset in STORMNET | Required for Nowcasting? | Candidate Public Source | India Coverage | Access Requirement | Current Project Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Surface Station Weather** | `pub_noaa_isd_vidp_delhi_2024` | **YES** | NOAA ISD (NCEI) | **YES** (Delhi VIDP Airport) | Open HTTPS (None) | **AVAILABLE** |
| **Doppler Weather Radar (Reflectivity)** | None (Sample JSON only) | **MANDATORY** | IMD Doppler Weather Radar (Delhi DWR) | **YES** (Direct regional coverage) | Institutional MoES MoU | **ACCESS BLOCKED** |
| **Doppler Weather Radar (Benchmark)** | None | **BENCHMARK ONLY** | MIT SEVIR (AWS Open Data) | **NO** (CONUS only) | Open S3 (`s3://sevir`) | **AVAILABLE** (for pre-training) |
| **Geostationary Satellite (IR/WV)** | None (Sample JSON only) | **MANDATORY** | EUMETSAT IODC (Meteosat-9/11) | **YES** ($45.5^\circ\text{ E}$ orbit) | Free EUMETSAT Registration | **PARTIAL** (Registration required) |
| **Geostationary Satellite (INSAT)** | None (Sample JSON only) | **PREFERRED** | ISRO MOSDAC (INSAT-3D/3DR) | **YES** (Nadir over India) | MOSDAC Portal / MoU | **ACCESS BLOCKED** |
| **Total Lightning (Continuous)** | None (Sample JSON only) | **HIGH PRIORITY** | IITM Damini Lightning Network | **YES** (Dense Indian ground network)| MoES / IITM Authorization | **ACCESS BLOCKED** |
| **Total Lightning (Climatological)**| None | **CALIBRATION** | NASA ISS-LIS Science Data | **YES** (Orbital passes over India) | NASA Earthdata Login | **PARTIAL** (Auth required) |
| **Precipitation (Sub-hourly)** | NOAA ISD `AA1` (Point gauge) | **HIGH PRIORITY** | NASA GPM IMERG Early/Late Run | **YES** ($0.1^\circ$ resolution) | NASA Earthdata Login | **PARTIAL** (Auth required) |
| **Precipitation (Dense Mesonet)** | None | **HIGH PRIORITY** | IMD ARG Network (Delhi NCR) | **YES** (Regional gauges) | Institutional IMD Feed | **ACCESS BLOCKED** |
| **Atmospheric Thermodynamics** | NOAA ISD ($T, T_d, P$) | **HELPFUL** | ECMWF ERA5 Hourly Reanalysis | **YES** ($0.25^\circ$ resolution) | Copernicus CDS API | **AVAILABLE** (Free API Key) |

---

## 5. Scientific Validation Policy & Modality Rules

1. **Surface Station Observations Alone are Insufficient**:
   - `pub_noaa_isd_vidp_delhi_2024` proves end-to-end data ingestion, temporal synchronization, and common-grid mapping.
   - However, surface station data alone **CANNOT** be used to evaluate, claim, or validate spatial convective nowcasting accuracy (e.g. CSI, POD, FAR, or F1 score).
   - Any claim that STORMNET has achieved "validated nowcasting performance" using only station data is scientifically invalid and strictly prohibited.

2. **Preferred Multi-Source Configuration**:
   $$\text{Preferred Configuration} = \text{Radar (DWR)} + \text{Satellite (IR/WV)} + \text{Lightning} + \text{Surface Station Mesonet}$$
   This multi-sensor combination captures the complete physical lifecycle of convective storms: boundary layer moisture convergence $\to$ rapid cloud-top ascent and glaciation $\to$ updraft electrification $\to$ precipitation core descent, downbursts, and cloudburst rainfall.

3. **Partially Available Modalities Policy**:
   - If only a subset of modalities is available (e.g. Surface Observations + GPM IMERG or Surface Observations + EUMETSAT Satellite), localized experiments may be executed.
   - However, all evaluation outputs must carry prominent disclosures:
     ```text
     [DISCLOSURE: PARTIAL MODALITY EXPERIMENT]
     Validated using Surface In-situ / Coarse Satellite data only.
     Radar reflectivity inputs were unavailable.
     This experiment DOES NOT constitute operational convective nowcasting validation.
     ```
