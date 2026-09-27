# Phase 9 Status Audit: Open/Public Meteorological Data Acquisition & Integration

**Audit Date**: September 26, 2026  
**Scope**: Public/Open Meteorological Data Acquisition, Provenance Tracking, Ingestion Contract, Validation Gating, and Reproducibility Infrastructure.  
**Auditor**: Automated Verification & Integrity Agent  
**Operational Policy**: Absolute Scientific Honesty — Zero Fake Data, Zero Fabricated Metrics, Zero False Validation Claims.

---

## Data Sources

The following meteorological data sources have been audited for convective nowcasting suitability across the Indian subcontinent and global benchmarks:

1. **Weather Radar**:
   - *NOAA NEXRAD AWS Open Data*: Level II/III dual-pol radar data over CONUS.
   - *MIT SEVIR (Storm Event Imagery & Radar Dataset)*: Synchronized NEXRAD VIL and GOES satellite imagery for convective storm events.
   - *IMD Doppler Weather Radar (DWR)*: S-band and C-band operational radar network across India.
   - *OPERA European Radar Network*: Pan-European radar composites.

2. **Satellite Imagery**:
   - *EUMETSAT IODC (Indian Ocean Data Coverage)*: Meteosat-9/11 geostationary SEVIRI imagery positioned over the Indian Ocean (45.5° E / 0°).
   - *ISRO MOSDAC / INSAT-3D/3DR/3DS*: Imager and Sounder radiances (TIR, VIS, WV) over India.
   - *NASA NOAA GOES-16/18 ABI*: Geostationary advanced baseline imager over the Americas.

3. **Lightning Observations**:
   - *NASA ISS-LIS (Lightning Imaging Sensor)*: Tropical spaceborne optical lightning detection (flashes, groups, events).
   - *GOES Geostationary Lightning Mapper (GLM)*: Total lightning optical observations.
   - *IITM / MoES Damini Lightning Network*: Operational ground lightning sensor network in India.

4. **Rainfall / Precipitation**:
   - *NASA GPM IMERG (Integrated Multi-satellitE Retrievals for GPM)*: Early/Late/Final runs at 0.1° (~10 km) resolution every 30 minutes over India.
   - *IMD Automated Rain Gauge (ARG) Network*: Surface tipping bucket gauges.

5. **Surface Weather Observations**:
   - *NOAA Integrated Surface Database (ISD) METAR*: Automated airport weather observations (VIDP, VABB, VOMM, VECC, etc.).
   - *IMD AWS (Automatic Weather Stations)*: Mesonet surface stations across India.

---

## Actually Accessible Sources

The following sources are **genuinely accessible** via public APIs, open cloud storage, or automated HTTP download without requiring restricted governmental access agreements:

| Source | Domain | Coverage | Access Method | Cost / Auth | Nowcasting Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MIT SEVIR** | Radar (VIL) & Satellite | CONUS Events | AWS S3 (`s3://sevir`) | Free / None | **High** (Deep-learning architecture pre-training & baseline benchmarking) |
| **NOAA ISD METAR** | Surface Station Truth | Global (incl. India) | NCEI HTTP Archive | Free / None | **High** (Real surface temperature, dew point, wind gusts, pressure ground truth) |
| **NASA GPM IMERG** | Precipitation | Global (incl. India) | NASA GES DISC HTTP | Free (Earthdata login) | **Medium-High** (Sub-hourly regional precipitation verification) |
| **NASA ISS-LIS** | Lightning | Tropical / India | NASA GHRC DAAC HTTP | Free (Earthdata login) | **Medium** (Climatological and orbital lightning calibration) |
| **EUMETSAT IODC** | Satellite (IR/WV/VIS) | Indian Ocean & India | Data Store Open API | Free (Registration required) | **High** (Geostationary cloud-top temperature & convective monitoring) |

---

## Inaccessible Sources

The following datasets remain **inaccessible** without signed institutional agreements, specialized ministerial credentials, or commercial licenses:

| Dataset | Provider | Reason Inaccessible |
| :--- | :--- | :--- |
| **IMD Operational Doppler Radar Volumes** | India Meteorological Department | No open HTTP/S3 public endpoint exists. Distribution is restricted to authorized MoES/government agencies. |
| **MOSDAC High-Rate Real-Time Stream** | Space Applications Centre / ISRO | Open portal provides historical/delayed files via interactive captcha/login, but automated low-latency real-time API streaming is restricted. |
| **IITM Damini Operational Lightning Feed** | Indian Institute of Tropical Meteorology | Proprietary government network; raw sensor feeds not published via open API. |
| **IMD Real-Time Dense AWS/ARG Feeds** | IMD | Real-time dense 15-minute gauge records are not exposed as an open machine-readable bulk REST API. |

---

## Dataset Provenance

STORMNET implements a strict, backward-compatible 6-tier provenance system in [`ml/data/manifest.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/manifest.py):

1. `PUBLIC_REAL_DATA`: Real-world meteorological observations acquired from publicly accessible scientific repositories (SEVIR, NOAA ISD, NASA GPM, EUMETSAT).
2. `AUTHORIZED_IMD_DATA`: Official radar or AWS data delivered under signed MoES/IMD data sharing agreement.
3. `AUTHORIZED_MOSDAC_DATA`: Official INSAT-3D/3DR/3DS imagery delivered under authorized ISRO/MOSDAC agreement.
4. `SAMPLE_DATA`: Static historical reference samples bundled for development and unit testing.
5. `SYNTHETIC_DATA`: Dynamically or procedurally generated meteorological tensors for simulation and stress testing.
6. `REPLAY_DATA`: Recorded or replayed scenarios intended strictly for UI demonstrations.

Backward compatibility with legacy `REAL_AUTHORIZED_DATA` and `HISTORICAL_DATA` has been verified.

---

## Pipeline Integration

Public datasets reuse the identical Phase 8 ingestion bridge without parallel ingestion pathways:

$$\text{Dropzone} \longrightarrow \text{Manifest} \longrightarrow \text{Validation} \longrightarrow \text{Normalization} \longrightarrow \text{Temporal Alignment} \longrightarrow \text{Target Grid (1–3 km)} \longrightarrow \text{Feature Fusion}$$

- **Public Dropzone Locations**:
  - `data/external/public/radar/`
  - `data/external/public/satellite/`
  - `data/external/public/lightning/`
  - `data/external/public/rainfall/`
  - `data/external/public/station/`
- **Common Grid Standard**: Target spatial grid remains fixed at 1–3 km ($256 \times 256$ cells). Sources with coarser resolution (e.g. GPM IMERG at 0.1° / ~10 km) undergo explicit spatial resampling (bilinear/bicubic interpolation) documented in the metadata. Coarse inputs are never falsely claimed to possess native 1 km resolution.

---

## Quality Control

The automated quality control engine ([`ml/data/quality.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/quality.py) and [`ml/data/validate.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/validate.py)) enforces 10 strict physical and structural tests:
1. Missing value rates (NaN thresholds $\le 20\%$).
2. Timestamp validity and ISO 8601 formatting.
3. Duplicate observation detection and removal.
4. Geographic coordinate bounding box checks.
5. File corruption and SHA-256 checksum verification.
6. Temporal gap detection ($\le 3\times$ sampling interval).
7. Spatial grid resolution and projection consistency (EPSG:4326).
8. Physical unit standardization (dBZ, mm/hr, K, m/s).
9. Source metadata completeness.
10. Machine-readable quality report generation (`quality_report.json`).

---

## Reproducibility

Reproducibility protocols are completely documented in [`docs/research/public-data-reproducibility.md`](file:///e:/project/SIH%20project%202%20Stormnet/docs/research/public-data-reproducibility.md). Any external researcher can download open datasets (such as NOAA ISD METAR for Indian airports or SEVIR radar samples from AWS S3), generate a valid manifest, pass quality validation, and fuse features using standard command-line scripts without proprietary tooling.

---

## Scientific Validation Eligibility

Enforced by [`ml/data/gating.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/gating.py):

| Provenance Tier | Development / Testing | UI Demonstration | Scientific Validation Certification | Operational Verification Claim |
| :--- | :--- | :--- | :--- | :--- |
| **SYNTHETIC_DATA** | Allowed | Allowed (with watermark) | **PROHIBITED** | **PROHIBITED** |
| **SAMPLE_DATA** | Allowed | Allowed (with watermark) | **PROHIBITED** | **PROHIBITED** |
| **REPLAY_DATA** | Allowed | Allowed (with watermark) | **PROHIBITED** | **PROHIBITED** |
| **PUBLIC_REAL_DATA** | Allowed | Allowed (`PUBLIC DATA` badge) | **Allowed (`PUBLIC_DATASET_VALIDATION`)** | **PROHIBITED** |
| **AUTHORIZED_IMD_DATA** | Allowed | Allowed (`IMD AUTHORIZED` badge) | **Allowed (`AUTHORIZED_REAL_WORLD_VALIDATION`)** | Allowed |
| **AUTHORIZED_MOSDAC_DATA**| Allowed | Allowed (`MOSDAC AUTHORIZED` badge)| **Allowed (`AUTHORIZED_REAL_WORLD_VALIDATION`)** | Allowed |

Under no circumstances can public datasets or synthetic data be used to claim that STORMNET is validated on real operational IMD radar data.

---

## Remaining Blockers

1. **Institutional Data Access**: Official MoES/IMD data sharing agreement is required to ingest high-frequency, volumetric S/C-band Doppler radar raw files (.h5 / .nc) from Delhi, Mumbai, Chennai, and Kolkata radars.
2. **Real-Time Operational Push**: Low-latency direct socket/FTP feeds from operational Indian radar and lightning networks are required before live operational nowcasting can be deployed in production.

---

## Exact Next Step

1. Execute test suite to confirm end-to-end integrity of public manifests, demo isolation, and provenance gating.
2. Await formal institutional data authorization or evaluate pre-training on public real datasets (e.g. SEVIR / NOAA ISD) under strict `PUBLIC_DATASET_VALIDATION` labeling.
