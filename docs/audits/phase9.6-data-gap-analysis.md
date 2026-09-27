# Phase 9.6 Audit: Scientific Dataset Suitability & Modality Gap Analysis

**Audit Date**: September 27, 2026  
**Scope**: Scientific Dataset Suitability, Modality Completeness, Public Data Alternatives, Access Barriers, Minimum Viable Scientific Stack, and Validation Readiness.  
**Auditor**: Automated Verification & Integrity Agent  
**Scientific Policy**: Strict Truth in Meteorological AI — No False Claims, No Mislabeled Data, No Model Training in Gap Analysis.

---

## 1. What We Actually Have

STORMNET currently has physically downloaded, verified, and integrated the following legitimate public real-world meteorological dataset:

- **Dataset Identifier**: `pub_noaa_isd_vidp_delhi_2024`
- **Provider**: NOAA National Centers for Environmental Information (NCEI)
- **Local Location**: `data/external/public/station/noaa_isd_vidp_delhi_2024.csv`
- **File Size**: $7,891,387\text{ bytes}$ ($7.53\text{ MB}$)
- **Records**: 19,511 individual observations covering all 366 days of 2024.
- **Location**: Indira Gandhi International Airport (VIDP), New Delhi, India ($28.5665^\circ\text{ N}, 77.103088^\circ\text{ E}$).
- **Status in STORMNET**: Successfully registered in catalog, validated by automated quality checks, normalized via `AtmosphericAdapter`, mapped onto the $3.0\text{ km}$ target grid mesh, and exposed via versioned FastAPI endpoints under `PUBLIC_REAL_DATA` provenance.

---

## 2. What NOAA ISD Provides

The NOAA ISD dataset provides verified, high-precision in-situ surface meteorological measurements:
1. **Thermodynamic Boundary-Layer Ground Truth**: Continuous dry-bulb temperature ($99.98\%$ complete) and dew point ($99.71\%$ complete) to monitor surface heating and moisture surges.
2. **Kinematic Ground Truth**: Sustained 10-meter horizontal wind speed ($99.97\%$ complete) and direction to detect surface wind shifts and squall gust fronts.
3. **Barometric Measurements**: Sea-level pressure records during major synoptic observation windows.
4. **Surface Weather Occurrences**: 19,129 present weather reports capturing fog, haze, dust storms, rain, and thunderstorm activity at the airport.
5. **Point Precipitation Depth**: 537 active precipitation accumulation measurements.
6. **Cloud Base Ceilings**: 14,083 cloud base ceiling observations.

---

## 3. What NOAA ISD Does Not Provide

NOAA ISD is **strictly a single-site surface station dataset**. It does not provide:
1. **NO Doppler Weather Radar**: No volumetric reflectivity ($Z$), differential reflectivity ($Z_{DR}$), or radial Doppler velocity ($V_r$).
2. **NO Geostationary Satellite Imagery**: No thermal infrared ($10.8\text{ µm}$) brightness temperatures, no water vapor channels, and no cloud-top cooling rates.
3. **NO Lightning Detection**: No total lightning flash counts, locations, or strike rates.
4. **NO Spatial 2D/3D Continuity**: It represents a point observation ($0\text{ km}$ footprint); it cannot resolve storm cell geometry, storm speed, storm tracks, or spatial precipitation gradients across the Delhi NCR domain.

---

## 4. Required Data Modalities

For true convective-scale nowcasting (0–6 hours at 1–3 km grid resolution) as required by SIH26084, the following four complementary data modalities are required:

| Modality | Primary Function | Minimum Required Spec |
| :--- | :--- | :--- |
| **Doppler Weather Radar** | Direct tracking of convective storm cores, updrafts, and severe hazard signatures | $1\text{--}3\text{ km}$, $5\text{--}10\text{ min}$, Column Max-Z & Radial Velocity |
| **Geostationary Satellite** | Detection of rapid cumulus ascent and cloud-top cooling before radar echoes form | $3\text{--}4\text{ km}$, $15\text{ min}$, TIR 10.8 µm & Water Vapor bands |
| **Lightning Location** | Proxy for convective updraft strength and severe hazard head triggers | $1\text{--}3\text{ km}$, $5\text{ min}$, Flash count & density |
| **Surface Observations** | Thermodynamic boundary layer constraints and ground-truth validation | Point mesonet, $15\text{--}30\text{ min}$, $T, T_d, P$, Wind, Precip |

---

## 5. Public Alternatives

| Candidate Source | Provider | Resolution | India Coverage | Feasibility / Access |
| :--- | :--- | :--- | :--- | :--- |
| **EUMETSAT IODC (Meteosat-9/11)** | EUMETSAT | $3\text{--}4\text{ km}, 15\text{ min}$ | **YES** ($45.5^\circ\text{ E}$ orbit covers India) | **High**: Free registration, open data store API |
| **NASA GPM IMERG** | NASA GES DISC | $0.1^\circ (\approx 10\text{ km}), 30\text{ min}$ | **YES** (Global / India) | **Medium-High**: Free Earthdata authentication |
| **ECMWF ERA5** | ECMWF / Copernicus | $0.25^\circ (\approx 28\text{ km}), 1\text{ hr}$ | **YES** (Global / India) | **High**: Free Copernicus CDS API (Coarse) |
| **MIT SEVIR** | MIT / AWS Open Data | $1\text{ km} \text{ (VIL)}, 5\text{ min}$ | **NO** (CONUS only) | **High**: Public S3 bucket (ML pre-training only) |
| **NASA ISS-LIS** | NASA GHRC DAAC | $\approx 4\text{ km}, \text{orbital}$ | **YES** (Overpasses only) | **Medium**: Climatological calibration only |

---

## 6. Access Barriers

1. **IMD Doppler Weather Radar Raw Volumes**:
   - Barrier: Non-public governmental distribution network. No open HTTP/S3 public access without institutional MoES data sharing agreement.
2. **ISRO MOSDAC INSAT-3D/3DR Real-Time Automated Stream**:
   - Barrier: Web portal employs CAPTCHA and delayed interactive file retrieval; automated programmatic REST endpoints require formal authorization.
3. **IITM Damini Operational Ground Lightning Network**:
   - Barrier: Proprietary institutional telemetry; raw sensor coordinates are not published via public APIs.
4. **NOAA NEXRAD AWS Open Data**:
   - Barrier: Direct anonymous S3 access returned `403 Forbidden` (requires AWS account signature / requester-pays token).
5. **NASA Earthdata (GPM IMERG & ISS-LIS)**:
   - Barrier: Automated anonymous download returned `401 Unauthorized`; requires credentialed `~/.netrc` setup.

---

## 7. Minimum Viable Scientific Dataset (MVSD)

The minimum viable combination that allows defensible machine-learning nowcasting experiments consists of:
1. **Spatial Backbone**: EUMETSAT IODC ($3\text{ km}, 15\text{ min}$ geostationary satellite imagery over India) OR IMD Doppler Weather Radar (Delhi DWR Max-Z composite).
2. **Ground Truth & Surface Constraint**: NOAA ISD surface station observations (Delhi VIDP 2024, currently available).
3. **Precipitation Calibrator**: NASA GPM IMERG ($10\text{ km}, 30\text{ min}$, downscaled to $3\text{ km}$).

---

## 8. Current Validation Capability

- **Data Ingestion Pipeline**: **PASS & READY**. The system can successfully consume, validate, normalize, and common-grid legitimate meteorological datasets.
- **Surface Thermodynamic Validation**: **CAPABLE**. The system can validate surface temperature drops, pressure jumps, and wind shifts during historical Delhi storm episodes.
- **Convective Nowcast Model Validation**: **NOT READY**. Validating 0–6 hour spatial nowcasting models (CSI, POD, FAR, F1) cannot be performed without 2D spatial radar reflectivity or geostationary satellite frames.

---

## 9. Exact Next Dataset To Acquire

To progress towards scientific nowcasting without requiring restricted ministerial clearances:
1. **Acquire EUMETSAT IODC Meteosat-9/11 geostationary imagery** over Northern India (free registration) to supply the required continuous 2D convective cloud-top imagery.
2. **Establish NASA Earthdata authentication** to ingest calibrated GPM IMERG sub-hourly precipitation fields over India.
3. **Pursue formal MoES/IMD data authorization** for Delhi Doppler Weather Radar volume files.
