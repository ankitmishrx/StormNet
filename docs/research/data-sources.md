# STORMNET — Meteorological Data Sources Registry
**Document ID:** `REG-DATA-SOURCES-001`  
**Phase:** Phase 8 Real Meteorological Data Acquisition Bridge  
**Problem Statement:** SIH26084 (Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Creation Date:** 2026-09-26  
**Status:** FACTUALLY GROUNDED REGISTRY  

---

## 1. Executive Summary

STORMNET requires multi-sensor meteorological data to execute high-fidelity 0–6 hour convective nowcasting. To bridge from synthetic/development fixtures to legitimate observational datasets without compromising institutional compliance, this registry specifies the four authorized operational meteorological data sources across the Indian subcontinent:

1. **India Meteorological Department (IMD) Doppler Weather Radar (DWR) Network**
2. **ISRO SAC / MOSDAC Geostationary Satellites (INSAT-3D / INSAT-3DR / INSAT-3DS)**
3. **Ground Lightning Networks (IITM / Earth Networks / IMD Damini)**
4. **IMD Automatic Weather Station (AWS) & Automatic Rain Gauge (ARG) Networks**

> [!IMPORTANT]
> In accordance with SIH26084 data integrity guidelines, **STORMNET does not scrape restricted endpoints, bypass institutional logins, or fabricate observations**. Datasets must be legitimately procured via institutional credentials, MoUs, or open academic portals, and ingested through the local data dropzone.

---

## 2. Source A: IMD Doppler Weather Radar (DWR) Network

### 2.1 Provider & Operational Context
- **Provider:** India Meteorological Department (IMD), Ministry of Earth Sciences (MoES), Government of India.
- **Facility / Coordinating Office:** National Data Centre (NDC) Pune / Radar Operations Division, Mausam Bhavan, New Delhi.
- **Hardware Platforms:**
  - S-band ($2.8\text{ GHz}$, $10.7\text{ cm}$, $1.0^\circ$ beamwidth): Bharat Electronics Limited (BEL) & ISRO indigenous radars (e.g. Safdarjung, Veravali, Port Trust, Kolkata).
  - C-band ($5.6\text{ GHz}$, $5.3\text{ cm}$, $0.9^\circ$ beamwidth): Enterprise Electronics Corporation (EEC) & Gematronik (e.g. Palam Terminal DWR, Jaipur).
  - X-band ($9.3\text{ GHz}$, $3.2\text{ cm}$): Urban / Himalayan high-resolution short-range radars.

### 2.2 Products & Variables
- **Volume Scan Products:**
  - `dBZ` / `TH` / `TV`: Total / Uncorrected & Corrected Reflectivity Factor ($-30.0$ to $+80.0\text{ dBZ}$)
  - `VRAD`: Radial Doppler Velocity ($-64.0$ to $+64.0\text{ m/s}$)
  - `WRAD`: Doppler Spectral Width ($0.0$ to $16.0\text{ m/s}$)
  - `ZDR`: Differential Reflectivity ($-6.0$ to $+10.0\text{ dB}$, dual-pol systems)
  - `KDP`: Specific Differential Phase Shift ($^\circ/\text{km}$)
  - `RHOHV`: Cross-Correlation Coefficient ($0.0$ to $1.0$)
- **Derived Cartesian Products:**
  - `MAX_Z`: Composite / Maximum Reflectivity column projection
  - `PPI`: Plan Position Indicator at fixed elevations ($0.5^\circ$ to $21.0^\circ$)
  - `CAPPI`: Constant Altitude Plan Position Indicator ($1.0\text{ km}$ to $12.0\text{ km}$ AGL)
  - `VIL`: Vertically Integrated Liquid content ($\text{kg/m}^2$)
  - `ETOP`: Echo Top Height at 18 dBZ / 35 dBZ ($\text{km MSL}$)

### 2.3 Spatio-Temporal Characteristics
- **Spatial Resolution:**
  - Polar coordinates: $250\text{ m}$ to $500\text{ m}$ range gate spacing, $0.5^\circ$ to $1.0^\circ$ azimuth resolution.
  - Surveillance radius: $250\text{ km}$ (S-band Doppler) / $150\text{ km}$ (C-band Doppler).
  - Standard Cartesian grid projection: $1.0\text{ km}$ (urban core) to $3.0\text{ km}$ (regional domain).
- **Temporal Resolution:**
  - Volume scan cycle: $10\text{ minutes}$ (standard operational mode); $5\text{ minutes}$ (rapid convective scan mode during severe weather warnings).

### 2.4 Data Formats & Protocols
- **Primary Operational Format:** WMO ODIM_H5 (OPERA Data Information Model in HDF5, standard WMO format).
- **Secondary / Legacy Formats:** Vaisala/Sigmet IRIS RAW (`.raw`, `.vol`), NetCDF4 (CF-Radial convention), BUFR.

### 2.5 Access Methods, Licensing & Project Availability
- **Access Portal:** IMD National Data Centre (NDC) Pune online data supply portal (`https://imdpune.gov.in/ndc_new/`) or Ministry of Earth Sciences Open Data portal.
- **Registration Requirements:** Formal institutional registration, government/academic affiliation verification, submission of research project justification (mentioning SIH26084).
- **Usage Restrictions:** Government of India Meteorological Data Sharing Policy. Academic/research non-commercial license. Redistribution of raw volume files is prohibited.
- **Expected Geographic Coverage:** 35+ operational DWR stations across India (Delhi-NCR, Mumbai, Chennai, Kolkata, Hyderabad, Bengaluru, etc.).
- **Current Project Availability:** **NOT AVAILABLE** in local workspace. Requires institutional offline transfer or NDC portal credential grant.

---

## 3. Source B: ISRO SAC / MOSDAC (INSAT-3D / INSAT-3DR / INSAT-3DS)

### 3.1 Provider & Operational Context
- **Provider:** Space Applications Centre (SAC), Indian Space Research Organisation (ISRO), Department of Space, Government of India.
- **Dissemination Center:** Meteorological and Oceanographic Satellite Data Archival Centre (MOSDAC), Ahmedabad (`https://www.mosdac.gov.in`).
- **Spacecraft Constellation:** Geostationary orbit at $74^\circ\text{E}$ (INSAT-3D), $82^\circ\text{E}$ (INSAT-3DR), $87^\circ\text{E}$ (INSAT-3DS).

### 3.2 Products & Variables Relevant to Nowcasting
- **Imager Spectral Radiance Channels (L1B):**
  - `VIS`: Visible ($0.55–0.75\,\mu\text{m}$, daytime convective cloud structure)
  - `SWIR`: Shortwave Infrared ($1.55–1.70\,\mu\text{m}$, snow/ice/water discrimination)
  - `MIR`: Middle Infrared ($3.80–4.00\,\mu\text{m}$, night fog, severe updraft hot spots)
  - `WV`: Water Vapor ($6.50–7.10\,\mu\text{m}$, upper-tropospheric moisture dynamics)
  - `TIR1`: Thermal Infrared 1 ($10.3–11.3\,\mu\text{m}$, cloud top temperature / overshooting tops)
  - `TIR2`: Thermal Infrared 2 ($11.5–12.5\,\mu\text{m}$, split-window moisture correction)
- **Derived Geophysical Products (L2B / L2C):**
  - `CTT`: Cloud Top Temperature ($\text{Kelvin}$) — critical convective indicator ($<220\text{ K}$)
  - `CTP`: Cloud Top Pressure ($\text{hPa}$)
  - `HEM`: Hydro-Estimator Method Rainfall Rate ($\text{mm/hr}$)
  - `IMSRA`: INSAT Multi-spectral Rainfall Algorithm ($\text{mm/hr}$)
  - `CMV`: Cloud Motion Vectors (Atmospheric Motion Vectors in $\text{m/s}$ and degrees)

### 3.3 Spatio-Temporal Characteristics
- **Spatial Resolution:**
  - Visible: $1.0\text{ km} \times 1.0\text{ km}$ at sub-satellite point.
  - SWIR / MIR / TIR1 / TIR2: $4.0\text{ km} \times 4.0\text{ km}$.
  - Water Vapor (WV): $8.0\text{ km} \times 8.0\text{ km}$.
- **Temporal Resolution:**
  - Full-disk scan: Every $30\text{ minutes}$ (staggered $15\text{ minutes}$ between 3D and 3DR).
  - Indian sector rapid scan: Every $15\text{ minutes}$.

### 3.4 Data Formats & Protocols
- **Format:** HDF5 (standard MOSDAC hierarchical format with Geolocation dataset), NetCDF4.
- **File Naming Convention:** `3RIMG_DDMMMYYYY_HHMM_L1B_STD.h5` or `3RIMG_DDMMMYYYY_HHMM_L2B_HEM.h5`.

### 3.5 Access Methods, Licensing & Project Availability
- **Access Portal:** MOSDAC web portal (`https://www.mosdac.gov.in`) and MOSDAC OpenSearch API.
- **Registration Requirements:** Free registered user account for Indian academic/research entities; OpenSearch API key generation.
- **Usage Restrictions:** ISRO Data Policy; research and non-commercial disaster risk reduction use permitted.
- **Expected Coverage:** Full Indian landmass and surrounding ocean basins ($40^\circ\text{E}–120^\circ\text{E}, 40^\circ\text{S}–40^\circ\text{N}$).
- **Current Project Availability:** **NOT AVAILABLE** in local workspace. Awaiting user-supplied MOSDAC account credentials / downloaded HDF5 product files.

---

## 4. Source C: Ground Lightning Detection Networks

### 4.1 Providers & Operational Context
- **Primary Provider:** Indian Institute of Tropical Meteorology (IITM), Pune (Ministry of Earth Sciences) via the Lightning Location Network (LLN).
- **Secondary / Commercial Feeds:** Earth Networks Total Lightning Network (ENTLN) / Vaisala GLD360 / IMD Damini Mobile Network.
- **Sensor Technology:** Time-of-arrival (TOA) and magnetic direction finding (MDF) across VLF/LF ($1\text{ kHz}–1\text{ MHz}$) and VHF ($30\text{ MHz}–300\text{ MHz}$) frequency bands.

### 4.2 Products & Variables
- **Individual Stroke Parameters:**
  - `timestamp`: UTC observation timestamp with microsecond accuracy
  - `latitude`, `longitude`: Stroke ground impact location (WGS-84)
  - `type`: Stroke classification (`CG` = Cloud-to-Ground, `IC` = Intra-Cloud / Cloud-to-Cloud)
  - `peak_current_ka`: Peak current amplitude in kiloamperes (typically $-300\text{ kA}$ to $+300\text{ kA}$)
  - `polarity`: `POSITIVE` or `NEGATIVE`
  - `sensors_participating`: Number of synchronized sensors ($N \ge 4$)
  - `chi_sq`: Location goodness-of-fit error metric ($\chi^2 \le 2.0$)
  - `semi_major_km`, `semi_minor_km`: 50% location error ellipse
- **Aggregated Spatio-Temporal Products:**
  - `flash_count`: Total flashes within grid cell per 5-minute interval
  - `flash_density`: Flashes per $\text{km}^2$ per hour
  - `ic_cg_ratio`: Ratio of intra-cloud to cloud-to-ground strikes (abrupt increase indicates convective updraft intensification / severe hail potential)

### 4.3 Spatio-Temporal Characteristics
- **Spatial Accuracy:** Sensor baseline accuracy $\approx 100\text{ m}–250\text{ m}$ for CG, $\approx 500\text{ m}$ for IC.
- **Temporal Resolution:** Real-time event streaming ($<10\text{ second}$ latency), aggregated into $5\text{-minute}$ nowcasting bins.

### 4.4 Data Formats & Protocols
- **Formats:** Delimited text/CSV, NetCDF4, GeoJSON, REST/WebSocket stream.

### 4.5 Access Methods, Licensing & Project Availability
- **Access Portal:** IITM Pune data portal / MoES Damini API / Commercial feed agreement.
- **Registration Requirements:** MoES institutional request; restricted for national security / critical infrastructure protection.
- **Usage Restrictions:** Academic non-commercial research use only.
- **Current Project Availability:** **NOT AVAILABLE** in local workspace. Single-frame development sample is used for test suites.

---

## 5. Source D: Rain-Gauge Networks (Ground Truth / Evaluation)

### 5.1 Provider & Operational Context
- **Provider:** India Meteorological Department (IMD) / State Disaster Management Authorities (SDMAs).
- **Network Types:**
  - Automatic Weather Stations (AWS): Comprehensive meteorological instrumentation.
  - Automatic Rain Gauges (ARG): Tipping-bucket rain gauges measuring cumulative precipitation.
  - Departmental / Non-Departmental Manual Rain Gauges: 08:30 IST 24-hour accumulations.

### 5.2 Products & Variables
- **Station Metadata:** Station ID, Station Name, District, State, Lat/Lon, Elevation ($m\text{ MSL}$).
- **Hydrometeorological Variables:**
  - `rain_accumulation_mm`: Cumulative precipitation ($\text{mm}$) over observation window
  - `rain_rate_mmh`: Derived rain intensity ($\text{mm/hr}$)
  - `interval_minutes`: Reporting frequency ($15\text{ min}$, $60\text{ min}$, or $24\text{ hr}$)
  - `quality_flag`: `VALID`, `SUSPECT`, `ERRONEOUS`, `ESTIMATED`

### 5.3 Spatio-Temporal Characteristics
- **Spatial Resolution:** Point gauge network (density varies from $5\text{ km}$ in urban Delhi/Mumbai to $25–50\text{ km}$ in rural districts).
- **Temporal Resolution:** $15\text{ minutes}$ (high-density urban telemetry) to $60\text{ minutes}$ (standard AWS).

### 5.4 Data Formats & Protocols
- **Formats:** CSV, JSON, IMD AWS XML feed, Hydro-meteorological text files.

### 5.5 Access Methods, Licensing & Project Availability
- **Access Portal:** IMD AWS Portal (`http://aws.imd.gov.in/`) or NDC Pune rainfall data archive.
- **Registration Requirements:** Public web viewing; bulk historical archive requires NDC Pune application.
- **Current Project Availability:** **NOT AVAILABLE** in local workspace. Sample 4-station snapshot used for development pipeline testing.

---

## 6. Summary Matrix: Project Data Readiness

| Data Source | Operational Provider | Target Format | Authentication / License | Currently Available to Project? |
| :--- | :--- | :--- | :--- | :---: |
| **IMD Doppler Weather Radar** | IMD / MoES | WMO ODIM_H5, NetCDF4 | NDC Pune Academic License | **NO** (0 historical files) |
| **INSAT-3D / 3DR Imager & Products** | ISRO SAC / MOSDAC | HDF5, NetCDF4 | MOSDAC Registered User | **NO** (0 historical files) |
| **Ground Lightning Network** | IITM / MoES | CSV, NetCDF4 | MoES Restricted MoU | **NO** (0 historical files) |
| **Automatic Rain Gauges (ARG/AWS)** | IMD / SDMA | CSV, JSON | IMD Public / NDC Portal | **NO** (0 historical files) |

---

## 7. Next Technical Action for Data Ingestion

Authorized datasets, once procured by the project team, must be placed into the local data dropzone:
- Radar: `data/external/imd_radar/{station_id}/`
- Satellite: `data/external/insat/`
- Lightning: `data/external/lightning/`
- Rain Gauge: `data/external/rain_gauge/`

And registered using the STORMNET CLI:
```bash
python -m ml.data.register --path data/external/imd_radar/DWR-DEL-SAF/ --dataset-id imd_delhi_2024 --provider IMD --product DWR_MAX_Z --provenance REAL_AUTHORIZED_DATA
python -m ml.data.validate --dataset imd_delhi_2024
```
