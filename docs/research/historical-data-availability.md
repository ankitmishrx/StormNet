# STORMNET — Historical Radar Data Availability Audit (2021–2025)
**Document ID:** `AUDIT-HIST-DATA-001`  
**Phase:** Phase 7 Multi-Year Historical Archive & Multi-Station Validation  
**Problem Statement:** SIH26084 (Convective Nowcasting for Thunderstorms, Hail & Cloudbursts, 0–6 hr)  
**Audit Date:** 2026-09-26  
**Auditor:** Lead System Architect  
**Classification:** Scientific Data Provenance & Compliance Audit  

---

## 1. Executive Summary

As required by Phase 7 guidelines, an exhaustive environment and repository inspection was performed to determine whether multi-year ($2021–2025$) Doppler Weather Radar (DWR) archives are locally present or accessible for target stations: **Delhi**, **Mumbai**, **Chennai**, and **Kolkata**.

### Key Audit Finding:
- **No official raw IMD historical radar archive files ($2021–2025$) are present in the local repository or runtime environment.**
- Local data is strictly limited to calibrated single-scan development samples (`data/samples/radar/dwr_delhi_20260926_1545.json`) and controlled synthetic mesoscale convective sequences generated for algorithmic testing.
- In strict adherence to SIH26084 scientific integrity rules:
  1. No unauthorized data scraping was performed.
  2. No authentication systems were bypassed.
  3. No fabricated historical archives were substituted.
  4. All four target stations are classified as **NOT AVAILABLE** for historical 2021–2025 evaluation until official institutional credentials / disk transfer from IMD/MoES are provisioned.

---

## 2. Station-by-Station Audit Findings

### 2.1 Station 1: Delhi-NCR (DWR-DEL-SAF / DWR-DEL-PAL)
- **Target Station ID:** `DWR-DEL-SAF` (Safdarjung) / `DWR-DEL-PAL` (Palam)
- **Verified Coordinates:** Lat $28.589^\circ\text{N}$, Lon $77.217^\circ\text{E}$, Altitude $216\text{ m MSL}$
- **Operational Agency:** India Meteorological Department (IMD) / MoES
- **Radar Hardware:** S-band ($2.8\text{ GHz}$ Doppler, BEL Indigenous) & C-band ($5.6\text{ GHz}$, EEC)
- **Actual Historical Data Available:** **NOT AVAILABLE** (0 archive files found in `data/raw/` or workspace)
- **Sample Ingested:** Single calibrated frame (`dwr_delhi_20260926_1545.json`, 15:45 IST)
- **Target Date Range:** 2021-01-01 to 2025-12-31 (Monsoon pre-convective & active seasons)
- **Target Temporal Resolution:** 5-minute to 10-minute volume scans
- **Target Spatial Resolution:** Polar range bins $250\text{ m}$ to $500\text{ m}$, azimuth $1.0^\circ$; Cartesian projection $1.0\text{ km}–3.0\text{ km}$
- **Target Variables:** Total Reflectivity ($Z$), Radial Doppler Velocity ($V$), Spectral Width ($W$), Differential Reflectivity ($Z_{DR}$)
- **Target File Formats:** WMO ODIM_H5, IRIS RAW (Vaisala/Sigmet), NetCDF4 (CF-Radial)
- **Licensing & Access Restrictions:** Government of India / IMD Data Sharing Policy. Access requires formal MoU / academic credentialing via IMD Pune National Data Centre (NDC).

---

### 2.2 Station 2: Mumbai (DWR-MUM-VER)
- **Target Station ID:** `DWR-MUM-VER` (Veravali, Andheri East / Colaba)
- **Verified Coordinates:** Lat $19.124^\circ\text{N}$, Lon $72.866^\circ\text{E}$, Altitude $85\text{ m MSL}$
- **Operational Agency:** India Meteorological Department (IMD)
- **Radar Hardware:** S-band ($2.8\text{ GHz}$, BEL indigenous)
- **Actual Historical Data Available:** **NOT AVAILABLE** (0 archive files)
- **Target Date Range:** 2021-06-01 to 2025-09-30 (Southwest Monsoon coastal convection)
- **Target Temporal Resolution:** 10-minute volume scan cycle
- **Target Spatial Resolution:** $500\text{ m}$ range gate, $1.0^\circ$ beamwidth; $3.0\text{ km}$ Cartesian resampled grid
- **Target Variables:** $Z$ (reflectivity), $V$ (radial velocity), $W$ (spectrum width)
- **Target File Formats:** WMO ODIM_H5, NetCDF4
- **Licensing & Access Restrictions:** Restricted meteorological data under MoES National Data Policy.

---

### 2.3 Station 3: Chennai (DWR-CHE-PRT)
- **Target Station ID:** `DWR-CHE-PRT` (Chennai Port Trust, Cyclone Detection Radar)
- **Verified Coordinates:** Lat $13.084^\circ\text{N}$, Lon $80.298^\circ\text{E}$, Altitude $16\text{ m MSL}$
- **Operational Agency:** India Meteorological Department (IMD)
- **Radar Hardware:** S-band ($2.8\text{ GHz}$, ISRO/BEL indigenous)
- **Actual Historical Data Available:** **NOT AVAILABLE** (0 archive files)
- **Target Date Range:** 2021-10-01 to 2025-12-31 (Northeast Monsoon cyclonic / convective bursts)
- **Target Temporal Resolution:** 10-minute standard scan
- **Target Spatial Resolution:** $500\text{ m}$ radial resolution, $250\text{ km}$ surveillance radius
- **Target Variables:** Reflectivity, Doppler Velocity, VIL, Echo Tops
- **Target File Formats:** WMO ODIM_H5, BUFR
- **Licensing & Access Restrictions:** Defense / coastal maritime security restrictions apply; authenticated MoES access required.

---

### 2.4 Station 4: Kolkata (DWR-KOL-SUB)
- **Target Station ID:** `DWR-KOL-SUB` (Netaji Subhash Chandra Bose Intl Airport)
- **Verified Coordinates:** Lat $22.654^\circ\text{N}$, Lon $88.447^\circ\text{E}$, Altitude $10\text{ m MSL}$
- **Operational Agency:** India Meteorological Department (IMD)
- **Radar Hardware:** S-band ($2.8\text{ GHz}$, BEL)
- **Actual Historical Data Available:** **NOT AVAILABLE** (0 archive files)
- **Target Date Range:** 2021-03-01 to 2025-06-30 (Pre-monsoon Nor'wester / Kalbaisakhi squall lines)
- **Target Temporal Resolution:** 10-minute volume scans
- **Target Spatial Resolution:** $500\text{ m}$ range gate, $1.0^\circ$ azimuth
- **Target Variables:** $Z$, $V$, $W$
- **Target File Formats:** WMO ODIM_H5, IRIS RAW
- **Licensing & Access Restrictions:** Aviation and severe weather restricted dissemination.

---

## 3. Comparative Data Availability Matrix

| Target Station | Operational Radar ID | Lat / Lon | 2021–2025 Data Present? | Source File Format | Status | Access Mechanism |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Delhi-NCR** | `DWR-DEL-SAF` | $28.589^\circ\text{N}, 77.217^\circ\text{E}$ | **NO** | WMO ODIM_H5 / IRIS | **NOT AVAILABLE** | IMD NDC Pune Request |
| **Mumbai** | `DWR-MUM-VER` | $19.124^\circ\text{N}, 72.866^\circ\text{E}$ | **NO** | WMO ODIM_H5 | **NOT AVAILABLE** | MoES Academic Portal |
| **Chennai** | `DWR-CHE-PRT` | $13.084^\circ\text{N}, 80.298^\circ\text{E}$ | **NO** | WMO ODIM_H5 | **NOT AVAILABLE** | IMD Coastal Radar Data Agreement |
| **Kolkata** | `DWR-KOL-SUB` | $22.654^\circ\text{N}, 88.447^\circ\text{E}$ | **NO** | WMO ODIM_H5 | **NOT AVAILABLE** | Regional Meteorological Centre (RMC) Kolkata |

---

## 4. Architectural Mitigation for Phase 7

Because historical raw telemetry is not currently mounted in the workspace, Phase 7 implementation must:
1. **Provide a Production-Grade Historical Archive Adapter:** Build the indexing, cataloging, and ingestion engine capable of processing multi-station WMO ODIM_H5 / NetCDF4 / JSON formats as soon as directories are mounted.
2. **Provide Multi-Station Quality Control (QC):** Enforce strict checks for duplicate timestamps, spatial clipping, corrupted headers, and beam blockage.
3. **Formalize Event Extraction & Station Split Infrastructure:** Support leave-one-station-out cross-validation without assuming all stations share identical calibration or geographic characteristics.
4. **Honest Reporting:** Refuse to fabricate performance metrics for unmounted historical periods.
