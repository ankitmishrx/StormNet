# STORMNET Public Meteorological Data Reproducibility Guide

## 1. Overview & Scientific Guarantees

This document provides complete, transparent, and reproducible instructions for acquiring, registering, and ingesting publicly accessible meteorological datasets into the STORMNET convective nowcasting pipeline.

### Scientific Principles & Gating
1. **Absolute Honesty**: Public datasets must never be mislabeled as IMD, NCMRWF, or MOSDAC data.
2. **Zero Fabrication**: No synthetic data or unverified observations are passed into scientific validation.
3. **Provenance Integrity**: Every file ingested into STORMNET is stamped with a machine-readable manifest declaring `provenance="PUBLIC_REAL_DATA"`.
4. **Validation Separation**: Models evaluated on public datasets are certified under `PUBLIC_DATASET_VALIDATION`. They are strictly disqualified from claiming `AUTHORIZED_REAL_WORLD_VALIDATION` (which requires signed MoES/IMD data authorization).

---

## 2. Ingestion Architecture Contract

All public datasets must pass through the unified Phase 8/9 ingestion bridge without parallel or bypass architectures:

```text
Public Source Download
       │
       ▼
data/external/public/{radar,satellite,lightning,rainfall,station}/
       │
       ▼
Manifest Generation (ml/data/manifest.py -> DatasetManifest)
       │
       ▼
Data Quality & Integrity Validation (ml/data/quality.py & ml/data/validate.py)
       │
       ▼
Normalization & Unit Standardization (ml/data/normalizer.py)
       │
       ▼
Spatial-Temporal Gridding (1-3 km target grid, 5-15 min alignment)
       │
       ▼
Feature Fusion Engine (ml/fusion/)
       │
       ▼
Gated Research Benchmark Evaluation (ml/data/gating.py)
```

---

## 3. Step-by-Step Acquisition & Ingestion Procedures

### Source A: MIT SEVIR (Storm Event Imagery & Radar Dataset)
- **Primary Use**: Radar (VIL) and geostationary satellite (IR, WV, VIS) convective nowcasting architecture benchmark.
- **Provider**: MIT Lincoln Laboratory / AWS Open Data (`s3://sevir`).
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Authentication**: None required (public AWS S3 bucket).

#### Reproduction Steps:
1. **Download SEVIR event sample or full partition**:
   ```bash
   # Using AWS CLI without credentials
   aws s3 cp --no-sign-request s3://sevir/data/vil/2019/SEVIR_VIL_STORMEVENTS_2019_0501_0630.h5 data/external/public/radar/
   ```
2. **Register Dataset in Manifest**:
   ```python
   from ml.data.manifest import DatasetManifest, DatasetProvenance, ValidationStatus
   import hashlib, os

   filepath = "data/external/public/radar/SEVIR_VIL_STORMEVENTS_2019_0501_0630.h5"
   file_size = os.path.getsize(filepath)
   with open(filepath, "rb") as f:
       chk = hashlib.sha256(f.read()).hexdigest()

   manifest = DatasetManifest(
       dataset_id="pub-radar-sevir-vil-2019",
       provider="MIT Lincoln Laboratory / AWS Open Data",
       product="SEVIR VIL",
       source_url="s3://sevir/data/vil/2019/",
       access_method="s3_anonymous",
       license="CC BY 4.0",
       provenance=DatasetProvenance.PUBLIC_REAL_DATA,
       variables=["vertically_integrated_liquid"],
       spatial_resolution="1 km",
       temporal_resolution="5 min",
       start_time="2019-05-01T00:00:00Z",
       end_time="2019-06-30T23:55:00Z",
       geographic_coverage="CONUS",
       file_count=1,
       total_size=file_size,
       checksum=chk,
       validation_status=ValidationStatus.PENDING
   )
   manifest.save("data/external/public/radar/manifest.json")
   ```
3. **Execute Ingestion & Quality Validation**:
   ```bash
   python -m ml.data.validate --manifest data/external/public/radar/manifest.json
   ```

---

### Source B: NOAA Integrated Surface Database (ISD) METAR
- **Primary Use**: Real surface weather ground truth (temperature, dew point, wind speed, gusts, pressure, present weather) for Indian airports.
- **Provider**: NOAA National Centers for Environmental Information (NCEI).
- **Coverage**: Delhi Palam (VIDP - 421810), Mumbai Santacruz (VABB - 430030), Chennai (VOMM - 432790), Kolkata (VECC - 428090).
- **License**: Public Domain (US Government Open Data).
- **Authentication**: None required.

#### Reproduction Steps:
1. **Download ISD METAR annual archives via open HTTPS**:
   ```bash
   # Download Delhi Indira Gandhi International Airport (VIDP, WBAN: 421810) for 2024
   curl -o data/external/public/station/VIDP_2024.csv "https://www.ncei.noaa.gov/data/global-hourly/access/2024/42181099999.csv"
   ```
2. **Generate Station Manifest**:
   ```python
   from ml.data.manifest import DatasetManifest, DatasetProvenance, ValidationStatus
   import hashlib, os

   filepath = "data/external/public/station/VIDP_2024.csv"
   file_size = os.path.getsize(filepath)
   with open(filepath, "rb") as f:
       chk = hashlib.sha256(f.read()).hexdigest()

   manifest = DatasetManifest(
       dataset_id="pub-surface-noaa-isd-vidp-2024",
       provider="NOAA NCEI",
       product="Integrated Surface Database (ISD) Hourly",
       source_url="https://www.ncei.noaa.gov/data/global-hourly/access/2024/42181099999.csv",
       access_method="https_open",
       license="Public Domain / CC0",
       provenance=DatasetProvenance.PUBLIC_REAL_DATA,
       variables=["TMP", "DEW", "WND", "SLP", "AA1"],
       spatial_resolution="Point Station (28.566° N, 77.103° E)",
       temporal_resolution="Hourly / Special METAR",
       start_time="2024-01-01T00:00:00Z",
       end_time="2024-12-31T23:59:00Z",
       geographic_coverage="Delhi NCR (VIDP)",
       file_count=1,
       total_size=file_size,
       checksum=chk,
       validation_status=ValidationStatus.PENDING
   )
   manifest.save("data/external/public/station/manifest.json")
   ```
3. **Parse and Grid to Common Spatial Grid**:
   Execute station point-to-grid interpolation using PostGIS or scipy nearest/IDW interpolation into the 1–3 km grid.

---

### Source C: NASA GPM IMERG Precipitation (Global Precipitation Measurement)
- **Primary Use**: Half-hourly calibrated precipitation estimates over the Indian subcontinent.
- **Provider**: NASA Goddard Earth Sciences Data and Information Services Center (GES DISC).
- **Product**: GPM IMERG Early/Late Run (0.1° × 0.1°, 30 min).
- **License**: Open NASA Data Policy.
- **Authentication**: Free Earthdata Login required (via `~/.netrc`).

#### Reproduction Steps:
1. **Set up Earthdata credentials**:
   ```bash
   echo "machine urs.earthdata.nasa.gov login <USER> password <PASS>" >> ~/.netrc
   chmod 600 ~/.netrc
   ```
2. **Fetch Sub-daily IMERG NetCDF4/HDF5**:
   ```bash
   curl -b ~/.netrc -c ~/.netrc -L -O \
     "https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.07/2024/200/3B-HHR-E.MS.MRG.3IMERG.20240718-S000000-E002959.0000.V07B.HDF5" \
     -o data/external/public/rainfall/3B-HHR-E.20240718.HDF5
   ```
3. **Spatial Resampling**:
   Bilinear interpolation from 0.1° (~10 km) to STORMNET 1–3 km target grid.

---

### Source D: NASA ISS-LIS (Lightning Imaging Sensor on the ISS)
- **Primary Use**: Optical lightning flash, group, and event observations over tropical latitudes including India.
- **Provider**: NASA Global Hydrology Resource Center (GHRC) DAAC.
- **License**: Open Data.
- **Authentication**: Free Earthdata Login required.

#### Reproduction Steps:
1. **Download HDF4/HDF5 orbital passes**:
   ```bash
   curl -b ~/.netrc -c ~/.netrc -L -O \
     "https://ghrc.nsstc.nasa.gov/pub/lis/iss/data/science/nrt/2024/ISS_LIS_SC_V1.0_20240718_010000.hdf" \
     -o data/external/public/lightning/ISS_LIS_20240718.hdf
   ```
2. **Grid lightning flash counts into 1–3 km, 15-min intervals**.

---

## 4. Automated Quality Control Checks

Every public dataset file is verified against the automated quality engine:

| Check | Failure Condition | Action Taken |
| :--- | :--- | :--- |
| **Missing Values / NaNs** | Rate > 20% in active area | Flagged in QC report, masked out |
| **Timestamp Validity** | Non-ISO8601 or out of range | File rejected |
| **Duplicate Observations** | Identical timestamp + coordinates | Deduplicated automatically |
| **Geographic Bounds** | Data outside declared bounding box | Clipped or rejected |
| **Corrupted Files** | Checksum mismatch or unreadable headers | Ingestion halted |
| **Temporal Gaps** | Gap > 3x temporal resolution | Flagged; sequence split into chunks |
| **Coordinate Reference System** | Missing CRS or non-standard projection | Reprojected to EPSG:4326 |
| **Unit Consistency** | Discrepancy (e.g. dBZ vs mm/hr vs mm) | Normalized via `ml.data.normalizer` |

Quality reports are generated as structured JSON alongside the manifest.

---

## 5. Scientific Validation Gate Protocol

The module [`ml.data.gating.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/gating.py) acts as a strict firewall:

```python
from ml.data.gating import enforce_provenance_gating, EvaluationContext
from ml.data.manifest import DatasetManifest

# Enforces that PUBLIC_REAL_DATA is allowed for reproducible research
# but categorically prohibited from claiming AUTHORIZED_REAL_WORLD_VALIDATION
result = enforce_provenance_gating(
    manifest=manifest,
    requested_context=EvaluationContext.SCIENTIFIC_VALIDATION
)

# Output:
# result.allowed == True
# result.certified_tier == "PUBLIC_DATASET_VALIDATION"
# result.operational_claim_allowed == False
```

If an evaluation attempts to claim operational real-world validation without `AUTHORIZED_IMD_DATA` or `AUTHORIZED_MOSDAC_DATA`, the pipeline raises `ProvenanceViolationError` and halts immediately.

---

## 6. End-to-End Reproduction Checklist for New Researchers

To reproduce the benchmark pipeline from scratch:
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download public dataset into `data/external/public/<category>/`
- [ ] Verify SHA256 checksum and generate `manifest.json`
- [ ] Run `python -m ml.data.validate --manifest data/external/public/<category>/manifest.json`
- [ ] Run test suite: `pytest tests/ -v`
- [ ] Inspect UI under `PUBLIC DATA` mode (with live operational watermarks disabled)
