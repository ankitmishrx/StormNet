# STORMNET — Meteorological Data Dropzone & Directory Guide

This directory manages the storage, staging, and provenance tracking of all meteorological observations and model features used by STORMNET.

## 1. Directory Structure

```text
data/
├── external/               <-- LOCAL DROPZONE FOR AUTHORIZED REAL DATA (Git ignored)
│   ├── imd_radar/          <-- Place raw IMD DWR volume scans (WMO ODIM_H5 / NetCDF4 / IRIS)
│   │   ├── DWR-DEL-SAF/    <-- Station subdirectories (e.g. New Delhi Safdarjung)
│   │   ├── DWR-MUM-VER/    <-- Mumbai Veravali
│   │   ├── DWR-CHE-PRT/    <-- Chennai Port Trust
│   │   └── DWR-KOL-SUB/    <-- Kolkata NSCB Airport
│   ├── insat/              <-- Place MOSDAC INSAT-3D / INSAT-3DR HDF5 product files
│   ├── lightning/          <-- Place IITM / Earth Networks lightning strike CSV / NetCDF
│   └── rain_gauge/         <-- Place IMD AWS / ARG rainfall accumulation CSV files
│
├── manifests/              <-- Dataset registration manifests (*.json)
├── raw/                    <-- Working staging directory for verified raw observations
├── processed/              <-- Gridded and fused feature sets (Parquet partitions)
│   └── fused/              <-- Date/sector partitioned fused tensors
└── samples/                <-- DEVELOPMENT SAMPLES ONLY (committed for CI/test suites)
    ├── radar/              <-- Single-frame radar development sample
    ├── satellite/          <-- Single-frame INSAT development sample
    ├── lightning/          <-- Single-frame lightning development sample
    └── aws/                <-- Single-frame AWS surface observation sample
```

---

## 2. Ingesting Authorized Real Datasets

When legitimate meteorological datasets are received via official IMD/MoES/ISRO credentials:

### Step 1: Copy Files into Dropzone
Place files in the appropriate subdirectory under `data/external/`.
*Note: Large raw volume files are ignored by git to protect data sovereignty and repository size limits.*

### Step 2: Register Dataset
Run the STORMNET registration CLI:
```bash
python -m ml.data.register \
  --path data/external/imd_radar/DWR-DEL-SAF/ \
  --dataset-id imd_delhi_2024_monsoon \
  --provider IMD \
  --product DWR_VOLUME_SCAN \
  --provenance REAL_AUTHORIZED_DATA \
  --license "IMD Academic MoU"
```
This inspects the directory, computes SHA-256 checksums, extracts temporal/spatial bounds, and generates an immutable manifest at `data/manifests/imd_delhi_2024_monsoon.json`.

### Step 3: Validate Dataset
Execute automated quality and integrity verification:
```bash
python -m ml.data.validate --dataset imd_delhi_2024_monsoon
```
Validation inspects:
- Header and file format integrity
- Coordinate Reference System (CRS) conformity (EPSG:4326)
- Geodetic bounding within Indian airspace ($6.0^\circ\text{N}–38.0^\circ\text{N}, 68.0^\circ\text{E}–98.0^\circ\text{E}$)
- Value ranges (e.g. Reflectivity $-30.0$ to $+80.0\text{ dBZ}$)
- Duplicate timestamps and temporal gaps ($>20\text{ minutes}$)

A formal validation report is produced in `reports/data-validation/imd_delhi_2024_monsoon.json`.

---

## 3. Data Classification Standards

Every dataset registered in STORMNET receives one of the following classification tags:

1. `REAL_AUTHORIZED_DATA`: Authenticated observations from IMD, ISRO MOSDAC, or authorized networks.
2. `HISTORICAL_DATA`: Official historical archives supplied under institutional data agreements.
3. `SAMPLE_DATA`: Small developmental sample files used for CI testing and unit tests.
4. `SYNTHETIC_DATA`: Mathematically generated test fixtures (e.g. 2D Gaussian kinematic cores).
5. `REPLAY_DATA`: Recorded or replayed live operational streams.

> [!CAUTION]
> Scientific validation experiments (`--mode SCIENTIFIC_VALIDATION`) will refuse to run on `SAMPLE_DATA` or `SYNTHETIC_DATA`. Only `REAL_AUTHORIZED_DATA` or `HISTORICAL_DATA` may be used for scientific claims.
