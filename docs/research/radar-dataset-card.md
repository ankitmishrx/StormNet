# Candidate Radar Dataset Card: IMD Doppler Weather Radar (Delhi Safdarjung / Palam)

> [!IMPORTANT]
> **Data Access Status**: `ACCESS REQUIRES AUTHORIZATION`  
> **Physical Data Presence**: `NOT AVAILABLE`  
> This dataset card documents the target specifications, licensing requirements, and ingestion expectations for legitimate Indian operational Doppler Weather Radar data. No unverified or unauthorized radar volume files have been fabricated or ingested.

---

## 1. Provider & Operating Agency
- **Provider**: India Meteorological Department (IMD) / Ministry of Earth Sciences (MoES), Government of India.
- **Operating Centre**: Regional Meteorological Centre (RMC), New Delhi.
- **Station Location**:
  - *Station 1*: Safdarjung Airport DWR, New Delhi ($28.5847^\circ\text{ N}, 77.2069^\circ\text{ E}$, Elevation $230\text{ m}$)
  - *Station 2*: Indira Gandhi International Airport (Palam) C-Band DWR ($28.5665^\circ\text{ N}, 77.1031^\circ\text{ E}$, Elevation $237\text{ m}$)
- **Hardware Architecture**: S-Band ($2.7\text{--}2.9\text{ GHz}$) / C-Band ($5.6\text{ GHz}$) Dual-Polarization Doppler Weather Radar.

---

## 2. Product Specifications & Target Variables

### Primary Variables (Mandatory for Convective Nowcasting)
1. **Radar Reflectivity Factor ($Z$ / dBZ)**:
   - *Physical Meaning*: Backscattered power from precipitation hydrometeors (raindrops, graupel, hail).
   - *Required Dynamic Range*: $-30.0\text{ dBZ to }+75.0\text{ dBZ}$.
   - *Role in Model*: Primary target and input feature for tracking storm cell intensity, precipitation cores, and convective boundaries.

### Secondary Variables (Severe Hazard Heads & Dynamics)
2. **Radial Doppler Velocity ($V_r$ / m/s)**:
   - *Physical Meaning*: Component of hydrometeor motion towards or away from the radar antenna.
   - *Required Dynamic Range*: $-60.0\text{ m/s to }+60.0\text{ m/s}$ (Nyquist velocity interval).
   - *Role in Model*: Detection of low-level convergence, gust fronts, microburst divergence, and mesocyclonic shear.
3. **Spectrum Width ($\sigma_v$ / m/s)**:
   - *Physical Meaning*: Standard deviation of the Doppler velocity spectrum within a pulse volume.
   - *Role in Model*: Indicator of turbulence, shear zones, and non-meteorological clutter discrimination.
4. **Differential Reflectivity ($Z_{DR}$ / dB)**:
   - *Physical Meaning*: Ratio of horizontally to vertically polarized radar backscatter.
   - *Role in Model*: Hail identification (large hail shows high $Z$ with near-zero or negative $Z_{DR}$).
5. **Specific Differential Phase ($K_{DP}$ / deg/km)**:
   - *Physical Meaning*: Range derivative of differential phase shift along propagation path.
   - *Role in Model*: Quantitative precipitation estimation (QPE) unaffected by radar calibration drift or beam attenuation.

---

## 3. Spatial & Temporal Characteristics
- **Native Spatial Resolution**:
  - Radial Range Gate Spacing: $250\text{ m}$ (short pulse) or $500\text{ m}$ (long pulse).
  - Azimuthal Resolution: $1.0^\circ$ beamwidth.
  - Maximum Unambiguous Range: $250\text{ km}$ (reflectivity mode) / $120\text{ km}$ (Doppler mode).
- **Target Ingestion Grid**: $1.0\text{ to }3.0\text{ km}$ Cartesian CAPPI / Column Maximum composite binned onto the STORMNET $45 \times 43$ grid ($28.0^\circ\text{--}29.2^\circ\text{ N}, 76.5^\circ\text{--}77.8^\circ\text{ E}$).
- **Temporal Cadence**: $10\text{ minutes}$ (standard volume coverage pattern / VCP) or $5\text{ minutes}$ (convective rapid-scan mode).
- **Historical Period Required**: Minimum 2 full convective seasons (Pre-monsoon and Monsoon 2023–2024, approximately $50\text{--}100$ severe convective storm days).

---

## 4. File Formats & Scientific Schema
- **Operational Source Formats**:
  - HDF5 / ODIM_H5 (WMO international radar exchange standard, `/dataset1/data1/data`)
  - NetCDF4 / Cf-Radial (Climate and Forecast conventions for radar data)
  - Raw Sigmet/Rainbow/Enterprise polar sweep files
- **Target Ingestion Format in STORMNET**: Standardized Cartesian GeoJSON / JSON / NetCDF grids mapped via [`ml.preprocessing.radar.ingest`](file:///e:/project/SIH%20project%202%20Stormnet/ml/preprocessing/radar/ingest.py).

---

## 5. Access Conditions & Institutional Protocols
- **Data Policy**: MoES National Data Sharing and Accessibility Policy (NDSAP).
- **Access Status for Third Parties**: **RESTRICTED / ACCESS REQUIRES AUTHORIZATION**.
- **Prerequisites for Procurement**:
  1. Formal research data request to the Director General of Meteorology (DGM), IMD New Delhi.
  2. Signed Memorandum of Understanding (MoU) / Non-Disclosure Agreement (NDA).
  3. Institutional project credentials from an accredited academic institution or Ministry of Jal Shakti / Disaster Management Authority.
  4. Payment of nominal data retrieval fees or academic fee waiver.

---

## 6. Quality Control Requirements for Raw Ingestion
1. **Ground Clutter Suppression**: Removal of static ground echoes (buildings, Aravalli hills, communication towers) via Doppler zero-velocity notch filtering and clutter map subtraction.
2. **Speckle & Second-Trip Echo Removal**: Isolation filtering of disconnected single-gate echo spikes.
3. **Attenuation Correction**: C-band specific path attenuation correction using $K_{DP}$ algorithms during intense monsoon squall lines.
4. **Beam Blockage Masking**: Geometric masking of partial or complete beam obstruction by high-rise urban structures near central Delhi.

---

## 7. Known Limitations
- Current access is strictly blocked pending institutional authorization.
- Operational radar files cannot be downloaded via open anonymous web endpoints.
- Scraping public web graphics (PNG/GIF) is prohibited due to lack of calibrated quantitative dBZ arrays and legal terms of service.
