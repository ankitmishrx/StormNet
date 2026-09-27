# Dataset Card: NOAA ISD Hourly Surface Meteorological Observations (Indira Gandhi International Airport, Delhi)

## Dataset
- **Name**: NOAA Integrated Surface Database (ISD) Hourly / Sub-hourly Surface Weather Observations — Indira Gandhi International Airport (VIDP), New Delhi, India.
- **Identifier**: `pub_noaa_isd_vidp_delhi_2024`
- **Station ID**: `42181099999` (WMO: `421810`, ICAO: `VIDP`)
- **Local Dropzone File**: `data/external/public/station/noaa_isd_vidp_delhi_2024.csv`
- **Manifest Location**: `data/manifests/pub_noaa_isd_vidp_delhi_2024.json`
- **Quality Report**: `data/processed/quality_reports/pub_noaa_isd_vidp_delhi_2024.json`

---

## Provider
- **Agency**: National Oceanic and Atmospheric Administration (NOAA) / National Centers for Environmental Information (NCEI).
- **Originating Reporting Authority**: Airports Authority of India (AAI) / India Meteorological Department (IMD) Aviation Meteorological Office at IGI Airport, transmitted globally via WMO GTS / ICAO AFTN.

---

## Product
- **Product Title**: Integrated Surface Database (ISD) Global Hourly and Special Surface Weather Observations.
- **Source URL**: `https://www.ncei.noaa.gov/data/global-hourly/access/2024/42181099999.csv`
- **Access Protocol**: Direct open HTTPS GET (No API token, authentication, or registration required).

---

## Geographic Coverage
- **Station Coordinates**: Latitude $28.5665^\circ\text{ N}$, Longitude $77.103088^\circ\text{ E}$.
- **Station Elevation**: $236.82\text{ m}$ above mean sea level.
- **Meteorological Sub-domain**: Delhi National Capital Region (NCR), Indo-Gangetic Plains, India.
- **Coordinate Reference System**: EPSG:4326 (WGS 84).

---

## Temporal Coverage
- **Start Timestamp**: `2024-01-01T00:00:00Z`
- **End Timestamp**: `2024-12-31T23:30:00Z`
- **Duration**: Full leap year 2024 (366 days, 8,784 continuous hours).
- **Total Records Ingested**: 19,511 discrete observation entries (routine METAR hourly + SPECI sub-hourly convective storm reports).

---

## Spatial Resolution
- **Native Resolution**: In-situ single-site point surface observation ($0\text{ km}$ footprint at sensor location).
- **Target Ingestion Grid**: Mapped into the STORMNET $3.0\text{ km}$ common grid cell ($28.0^\circ\text{ N}-29.2^\circ\text{ N}, 76.5^\circ\text{ E}-77.8^\circ\text{ E}$, grid cell $[i=21, j=20]$).

---

## Temporal Resolution
- **Nominal Cadence**: 30 minutes (routine half-hourly METAR transmissions).
- **Convective Event Cadence**: 5–15 minutes (irregular SPECI transmissions triggered by sudden gusts, wind shifts, visibility drops, or thunderstorm initiation).

---

## Variables
The dataset supplies high-quality, calibrated surface thermodynamic and kinematic variables:
1. `air_temperature_celsius` (`TMP`): Dry-bulb temperature at $2\text{ m}$ ($0.1^\circ\text{C}$ resolution).
2. `dewpoint_celsius` (`DEW`): Dewpoint temperature ($0.1^\circ\text{C}$ resolution).
3. `relative_humidity_pct`: Thermodynamic moisture content calculated via standard Magnus-Tetens vapor pressure formulation.
4. `sea_level_pressure_hpa` (`SLP`): Atmospheric pressure reduced to mean sea level ($0.1\text{ hPa}$ resolution).
5. `wind_direction_deg` (`WND`): True wind direction ($1^\circ$ resolution, $0^\circ-360^\circ$).
6. `wind_speed_kmh` (`WND`): Sustained horizontal wind speed at $10\text{ m}$ ($0.1\text{ m/s} \to\text{km/h}$).
7. `liquid_precipitation_mm` (`AA1`): Measured liquid accumulation depth over preceding observation intervals.

---

## Format
- **Format**: Structured Comma-Separated Values (`.csv`).
- **Encoding**: UTF-8.
- **File Size**: $7,891,387\text{ bytes}$ ($7.53\text{ MB}$).
- **SHA-256 Checksum**: `3982a30f3827492c85804beee4a4afd146b68808fd0c0e070dea56a371668205`.

---

## License / Access
- **License**: US Government Open Data / Public Domain (equivalent to CC0 1.0 Universal).
- **Access Restrictions**: None. Unrestricted for academic, research, commercial, and operational benchmarking.
- **Attribution**: "Dataset courtesy of NOAA National Centers for Environmental Information (NCEI), Global Hourly Integrated Surface Database (ISD)."

---

## Provenance
- **STORMNET Tier**: `PUBLIC_REAL_DATA`
- **Validation Gate Certification**: Eligible strictly for `PUBLIC_DATASET_VALIDATION`.
- **Integrity Status**: Physically downloaded, un-fabricated, immutable raw file preserved in `data/external/public/station/`.

---

## Known Limitations
1. **Single-Site Point Measurement**: Observations represent a single geographic location (VIDP airport). They do not represent a spatially contiguous volumetric 2D field.
2. **Missing Precipitation Depth Records**: Certain routine METARs record precipitation present weather codes without quantitative `AA1` accumulation depth.
3. **No Volumetric Doppler Radar**: This dataset contains surface station telemetry; it does not provide 3D radar reflectivity ($Z$), differential reflectivity ($Z_{DR}$), or radial velocity ($V_r$).
4. **Historical Delay**: This is an archived historical dataset and cannot be utilized as a real-time streaming feed.

---

## Resampling
- **SOURCE_RESOLUTION**: `Point Station Observation (Single Site)`
- **TARGET_RESOLUTION**: `3.0 km (45 x 43 Common Grid Mesh)`
- **RESAMPLING_METHOD**: `Inverse Distance Weighting (IDW) / Nearest Grid Cell Mapping`
- **Scientific Disclosure**: Spatial interpolation does not synthesize unobserved atmospheric features across unmonitored sectors of Delhi NCR. Target grid cells distant from the VIDP station maintain explicitly quarantined missing data flags (`QualityFlag.MISSING`).

---

## Quality Control
Automated validation checks executed via [`ml/data/validate.py`](file:///e:/project/SIH%20project%202%20Stormnet/ml/data/validate.py):
- **File Integrity**: Verified non-zero byte, valid CSV headers, intact EOF.
- **Geographic Bounds**: Validated within Indian bounding box ($28.5665^\circ\text{ N}, 77.1031^\circ\text{ E}$).
- **Coordinate Reference System**: EPSG:4326.
- **Timestamp Integrity**: All 19,511 records parsed as valid ISO 8601 timestamps without backward clock jumps.
- **Physical Plausibility**: Validated $-40^\circ\text{C} \le T \le +60^\circ\text{C}$, $700\text{ hPa} \le P \le 1100\text{ hPa}$, $0\text{ km/h} \le V_{wind} \le 200\text{ km/h}$. Sentinel values (`9999`) filtered out.

---

## Intended Use
- Ground-truth meteorological validation for historical convective storm and squall episodes in Delhi NCR.
- Cross-calibration of surface temperature drops, pressure surges, and wind gusts associated with convective downdrafts and gust fronts.
- Reproducible pipeline testing of multi-source fusion without synthetic approximations.

---

## Prohibited Claims
1. **NO Operational Live Claim**: Must never be represented in user interfaces or papers as a live real-time operational feed.
2. **NO Direct IMD Bulk Authorization Claim**: Must never be described as "Authorized IMD Radar Data" or "Official MoES Direct Bulk Feed."
3. **NO Spatial Radar Volumetric Claim**: Must never be misrepresented as radar reflectivity volume data.
4. **NO Real-World Operational Model Validation Claim**: Must never be cited as operational real-world validation of the complete STORMNET nowcasting system.
