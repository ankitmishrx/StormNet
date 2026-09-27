# STORMNET — Public & Open Meteorological Data Sources Research
**Document ID:** `RES-PUBLIC-DATA-001`  
**Phase:** Phase 9 Open/Public Meteorological Data Acquisition  
**Problem Statement:** SIH26084 (Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Creation Date:** 2026-09-26  
**Status:** FACTUALLY GROUNDED PUBLIC REPOSITORY AUDIT  

---

## 1. Executive Summary & Scientific Rationale

While India Meteorological Department (IMD) raw Doppler Weather Radar volume files and ISRO MOSDAC INSAT full-cadence archives remain behind restricted institutional credentialing, modern machine learning nowcasting platforms can maintain scientific integrity and reproducibility by ingesting **legitimately accessible, open, and public meteorological data**.

This document investigates and catalogs open-access meteorological datasets across five core domains:
1. **Weather Radar** (Open operational radar networks & nowcasting benchmarks)
2. **Satellite Imagery** (Open geostationary & multispectral orbital platforms)
3. **Lightning Observations** (Open spaceborne & ground detection archives)
4. **Rainfall / Precipitation (QPE)** (Open high-resolution satellite precipitation products)
5. **Surface Weather Observations** (Open global synoptic & hourly METAR airport networks)

> [!IMPORTANT]
> **No Fake Data Rule:** At no point are public international datasets rebranded as "IMD" or "INSAT" data. All public sources are ingested under their genuine provenance tag (`PUBLIC_REAL_DATA`) with full source URLs, licenses, and spatial resampling disclosures.

---

## 2. Candidate Open Data Sources by Domain

### 2.1 Domain A: Weather Radar

#### Candidate A.1: NOAA NEXRAD Open Radar Archive (AWS Open Data / Google Cloud)
- **Provider:** National Oceanic and Atmospheric Administration (NOAA), USA.
- **Dataset Name:** Next Generation Weather Radar (NEXRAD) Level II & Level III.
- **Variables:** Base Reflectivity (`REF`), Radial Velocity (`VEL`), Spectrum Width (`SW`), Differential Reflectivity (`ZDR`), Correlation Coefficient (`CC`).
- **Spatial Resolution:** $250\text{ m}$ range resolution, $0.5^\circ$ azimuth. Gridded composites at $1.0\text{ km} \times 1.0\text{ km}$.
- **Temporal Resolution:** $4.5–10\text{ minutes}$ (standard volume scan), $2–3\text{ minutes}$ (MESO-SAILS severe rapid scan).
- **Historical Coverage:** 1991 to present (30+ years continuous archive).
- **File / API Format:** WMO Archive II binary (decodeable via Py-ART, ARM, or WSR-88D decoder), NetCDF4.
- **Access Method:** Public S3 bucket `s3://noaa-nexrad-level2/` (HTTP open access: `https://noaa-nexrad-level2.s3.amazonaws.com`).
- **License / Access Restrictions:** Open Public Domain (US Government work). No authentication required. Free egress.
- **Whether Download is Currently Possible:** **YES — Fully open and verified**.
- **Whether Authentication is Required:** **NO**.
- **Suitability for Convective Nowcasting:** **EXCELLENT**. Globally recognized gold standard for convective scale deep learning nowcasting (used by DeepMind Nowcasting, MetNet-1/2/3, Earthformer, DGMR). Useful for pre-training spatio-temporal backbones before transfer to tropical radar regimes.

#### Candidate A.2: SEVIR (Storm Event Imagery and Video Dataset)
- **Provider:** MIT Lincoln Laboratory / Climate Change AI.
- **Dataset Name:** SEVIR (Spatiotemporal dataset of weather events).
- **Variables:** NEXRAD Vertically Integrated Liquid (`VIL`), GOES-16 Visible (`vis`), Shortwave IR (`ir069`), Longwave IR (`ir107`), GLM Flashes (`lght`).
- **Spatial Resolution:** $1.0\text{ km}$ (VIL/VIS), $2.0\text{ km}$ (IR), $384\text{ km} \times 384\text{ km}$ bounding boxes.
- **Temporal Resolution:** 5-minute sampling over 4-hour severe convective episodes.
- **Historical Coverage:** 2018–2019 (10,000+ curated convective storm events).
- **File / API Format:** HDF5 with deterministic spatio-temporal alignment.
- **Access Method:** Public AWS S3 bucket `s3://sevir/`.
- **License:** Creative Commons Attribution 4.0 International (CC-BY 4.0).
- **Whether Download is Currently Possible:** **YES — Fully public**.
- **Whether Authentication is Required:** **NO**.
- **Suitability for Convective Nowcasting:** **EXCELLENT**. Specifically curated for benchmarking deep learning convective extrapolation, lightning generation, and synthetic radar translation.

---

### 2.2 Domain B: Satellite Imagery

#### Candidate B.1: EUMETSAT Meteosat Indian Ocean Data Coverage (IODC)
- **Provider:** European Organisation for the Exploitation of Meteorological Satellites (EUMETSAT).
- **Satellite / Product Name:** Meteosat-9 / Meteosat-10 Indian Ocean Data Coverage (located at $45.5^\circ\text{E}$ / $41.5^\circ\text{E}$, viewing the Indian subcontinent).
- **Variables:** SEVIRI 12 spectral channels: High-Resolution Visible (`HRV`), Thermal IR ($10.8\,\mu\text{m}$, $12.0\,\mu\text{m}$), Water Vapor ($6.2\,\mu\text{m}$, $7.3\,\mu\text{m}$), Ozone ($9.7\,\mu\text{m}$), Cloud Top Height/Temp.
- **Spatial Resolution:** $3.0\text{ km}$ at sub-satellite point for thermal channels, $1.0\text{ km}$ for HRV.
- **Temporal Resolution:** $15\text{ minutes}$ continuous cadence.
- **Historical Coverage:** 2016 to present (IODC operational service).
- **File / API Format:** Native HRIT / LRIT, NetCDF4, GRIB2.
- **Access Method:** EUMETSAT Data Store REST API (`https://data.eumetsat.int`).
- **License / Restrictions:** Open access under EUMETSAT Data Policy for non-commercial research; free registration required for API key.
- **Whether Download is Currently Possible:** **YES** (requires user account on EUMETSAT portal).
- **Whether Authentication is Required:** **YES (Free API key registration)**.
- **Suitability for Convective Nowcasting:** **EXCELLENT**. Covers India directly in real-time and historical archive with 15-minute intervals, providing legitimate geostationary thermal infrared radiances identical in physics to INSAT-3DR TIR1.

#### Candidate B.2: NASA GPM / Global Precipitation Measurement Satellite Constellation
- **Provider:** NASA Goddard Space Flight Center / JAXA.
- **Product Name:** GPM Core Observatory Microwave Imager (GMI) & Dual-frequency Precipitation Radar (DPR).
- **Variables:** Ka/Ku-band reflectivity, Brightness Temperature (10 to 183 GHz), Surface Precipitation.
- **Spatial Resolution:** $5.0\text{ km}$ radar footprints, swath width $245\text{ km}$.
- **Temporal Resolution:** Orbital overpasses (1–2 passes per day per coordinate).
- **Historical Coverage:** 2014 to present.
- **File Format:** HDF5, NetCDF4.
- **Access Method:** NASA Earthdata GES DISC Open Archive (`https://disc.gsfc.nasa.gov/`).
- **License:** Open Access / Public NASA Earth Science Data. Free Earthdata login.
- **Whether Download is Currently Possible:** **YES**.
- **Whether Authentication is Required:** **YES (Free Earthdata account)**.
- **Suitability for Convective Nowcasting:** Moderate for real-time (due to orbital pass frequency), but **HIGH for ground-truth convective core verification**.

---

### 2.3 Domain C: Lightning Observations

#### Candidate C.1: NASA ISS-LIS (Lightning Imaging Sensor on International Space Station)
- **Provider:** NASA Marshall Space Flight Center / GHRC DAAC.
- **Product Name:** ISS LIS Non-Quality-Controlled (NQC) and Final Quality-Controlled Lightning Observations.
- **Variables:** Lightning events, groups, and flashes; radiance; duration; footprint coordinates.
- **Spatial Resolution:** $4.0\text{ km} \times 4.0\text{ km}$ nadir resolution across tropical/subtropical latitudes (covers India between $51.6^\circ\text{S}$ and $51.6^\circ\text{N}$).
- **Temporal Resolution:** Orbital overpasses with millisecond event timestamps.
- **Historical Coverage:** March 2017 to November 2023.
- **File Format:** HDF4 / HDF5 / NetCDF4.
- **Access Method:** NASA Earthdata / GHRC DAAC (`https://ghrc.nsstc.nasa.gov/hydro/`).
- **License:** Open NASA Science Data.
- **Whether Download is Currently Possible:** **YES**.
- **Whether Authentication is Required:** **YES (Free Earthdata login)**.
- **Suitability for Convective Nowcasting:** **GOOD for historical tropical convective calibration**. Calibrates convective updraft intensity over India.

#### Candidate C.2: NOAA GOES-R Geostationary Lightning Mapper (GLM)
- **Provider:** NOAA / NASA.
- **Product Name:** GLM Level 2 Flash / Group / Event Data.
- **Variables:** Flash energy, area, centroid lat/lon, count.
- **Spatial Resolution:** $8.0\text{ km} \times 8.0\text{ km}$ (nadir).
- **Temporal Resolution:** 20-second continuous updates.
- **Historical Coverage:** 2017 to present.
- **File Format:** NetCDF4.
- **Access Method:** AWS Open Data `s3://noaa-goes16/GLM-L2-LCFA/`.
- **License:** Open Public Domain. No authentication required.
- **Suitability for Convective Nowcasting:** Excellent algorithmic reference for geostationary lightning integration.

---

### 2.4 Domain D: Rainfall / Precipitation (Quantitative Precipitation Estimation)

#### Candidate D.1: NASA GPM IMERG (Integrated Multi-satellitE Retrievals for GPM)
- **Provider:** NASA / PMM Science Team.
- **Product Name:** IMERG Early, Late, and Final Half-Hourly Quantitative Precipitation Estimates.
- **Variables:** `precipitationCal` (calibrated rainfall rate in $\text{mm/hr}$), `precipitationUncal`, `probabilityLiquidPrecipitation`, `qualityIndex`.
- **Spatial Resolution:** $0.1^\circ \times 0.1^\circ$ ($\approx 10\text{ km} \times 10\text{ km}$) Cartesian global grid covering $60^\circ\text{S}–60^\circ\text{N}$ (includes full Indian landmass).
- **Temporal Resolution:** $30\text{ minutes}$ intervals.
- **Historical Coverage:** June 2000 to present (24+ years continuous record).
- **File / API Format:** HDF5, NetCDF4, GeoTIFF.
- **Access Method:** NASA GES DISC Open Archive / OPeNDAP server (`https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.07/`).
- **License:** Open Access NASA Earth Science Policy.
- **Whether Download is Currently Possible:** **YES — Active, verified, public**.
- **Whether Authentication is Required:** **YES (Free NASA Earthdata credentials in `~/.netrc`)**.
- **Suitability for Convective Nowcasting:** **HIGH**. Provides continuous, objective $30\text{-minute}$ multi-sensor precipitation ground truth across India for evaluating cloudburst and heavy rainfall nowcasts when rain gauge networks are unavailable.

---

### 2.5 Domain E: Surface Weather Observations

#### Candidate E.1: NOAA Integrated Surface Database (ISD) / Global METAR Network
- **Provider:** NOAA National Centers for Environmental Information (NCEI).
- **Product Name:** Integrated Surface Database (ISD-Hourly) / Global Summary of the Day (GSOD).
- **Variables:** Surface temperature ($^\circ\text{C}$), Dew point ($^\circ\text{C}$), Sea-level pressure ($\text{hPa}$), Wind direction, Wind speed ($\text{m/s}$ or $\text{km/h}$), Peak wind gust, Liquid precipitation depth ($\text{mm}$), Present weather flags (Thunderstorm `TS`, Hail `GR`, Heavy Rain `RA`).
- **Target Indian Stations Present in ISD:**
  - `421810` (VIDP / New Delhi Indira Gandhi International Airport): $28.566^\circ\text{N}, 77.103^\circ\text{E}$
  - `421820` (New Delhi Safdarjung Observatory): $28.583^\circ\text{N}, 77.200^\circ\text{E}$
  - `430030` (VABB / Mumbai Chhatrapati Shivaji Maharaj Intl): $19.088^\circ\text{N}, 72.868^\circ\text{E}$
  - `432790` (VOMM / Chennai Meenambakkam Airport): $12.994^\circ\text{N}, 80.180^\circ\text{E}$
  - `428090` (VECC / Kolkata Netaji Subhash Chandra Bose Intl): $22.654^\circ\text{N}, 88.447^\circ\text{E}$
- **Spatial Resolution:** Point observation stations across major Indian cities and airports.
- **Temporal Resolution:** 30-minute to 60-minute standard METAR/SYNOP reports; special SPECI reports during severe convective squalls.
- **Historical Coverage:** 1901 to present (continuous hourly records from 1973+ for major Indian hubs).
- **File / API Format:** CSV, fixed-width ASCII, JSON API.
- **Access Method:** NOAA NCEI Open HTTP (`https://www.ncei.noaa.gov/data/global-hourly/access/`) and AWS Open Data.
- **License / Restrictions:** Public Domain. Completely open, zero cost, no authentication required.
- **Whether Download is Currently Possible:** **YES — Fully open and immediately accessible**.
- **Whether Authentication is Required:** **NO**.
- **Suitability for Convective Nowcasting:** **HIGH**. Provides legitimate, ground-truth surface temperature, wind gust, pressure drop, and severe weather codes across Delhi, Mumbai, Chennai, and Kolkata to calibrate convective hazard heads.

---

## 3. Summary Matrix of Public Candidate Sources

| Candidate Source | Domain | Geographic Coverage | Spatio-Temporal | Access Method | Download Now? | Suitable for Nowcasting? |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **NOAA NEXRAD S3** | Radar | North America / US | $1\text{ km} / 5\text{ min}$ | AWS S3 Open Data | **YES** | Pre-training / Architecture Benchmarking |
| **MIT SEVIR** | Radar + Sat + Ltg | North America | $1–2\text{ km} / 5\text{ min}$ | AWS S3 Open Data | **YES** | Multi-modal Deep Learning Benchmarks |
| **EUMETSAT IODC** | Satellite | **Indian Subcontinent** | $3\text{ km} / 15\text{ min}$ | EUMETSAT Data Store | **YES** (Free Reg) | **Direct Indian Satellite Nowcasting** |
| **NASA GPM IMERG** | Precipitation | **Global (inc. India)** | $0.1^\circ / 30\text{ min}$ | NASA Earthdata | **YES** (Free Reg) | **Objective Rainfall Ground Truth** |
| **NOAA ISD / METAR** | Surface AWS | **Delhi, Mumbai, Chennai, Kolkata** | Point / $30–60\text{ min}$ | NOAA NCEI Open HTTP | **YES (No Auth)** | **Authentic Surface Validation** |

---

## 4. Architectural Integration Path for STORMNET

STORMNET establishes a clean, decoupled data bridge for public data:
1. Public datasets are placed into `data/external/public/{domain}/`.
2. Every imported public dataset is registered under provenance tag `PUBLIC_REAL_DATA`.
3. Datasets pass through existing validation, spatial normalization, and common-grid alignment.
4. Experiments consuming `PUBLIC_REAL_DATA` are gated and labeled explicitly as **"Public-Dataset Validation"**, strictly separated from `AUTHORIZED_IMD_DATA` and `SAMPLE_DATA`.
