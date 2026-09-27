# NOAA ISD Dataset Card: Surface Observations (Indira Gandhi International Airport, Delhi)

## 1. Station Identification & Location
- **Station ID**: `42181099999` (WMO Station Identifier: `421810`, ICAO Airport Code: `VIDP`, WBAN: `99999`)
- **Station Name**: `INDIRA GANDHI INTERNATIONAL, IN`
- **Latitude**: $28.5665^\circ\text{ N}$
- **Longitude**: $77.103088^\circ\text{ E}$
- **Elevation**: $236.82\text{ m}$ above mean sea level
- **Country**: India
- **Local Dropzone File**: `data/external/public/station/noaa_isd_vidp_delhi_2024.csv`
- **File Size**: $7,891,387\text{ bytes}$ ($7.53\text{ MB}$)
- **SHA-256 Checksum**: `3982a30f3827492c85804beee4a4afd146b68808fd0c0e070dea56a371668205`

---

## 2. Temporal Characteristics
- **Observation Period**: `2024-01-01T00:00:00Z` to `2024-12-31T23:30:00Z` (Full leap year 2024, 366 days).
- **Total Ingested Observations**: $19,511$ discrete records.
- **Nominal Sampling Cadence**: 30 minutes (routine half-hourly METAR broadcasts at $hh:00$ and $hh:30\text{ UTC}$).
- **Event-Driven Cadence**: Irregular 5–15 minute intervals for special observations (SPECI) triggered by sudden weather shifts, gust fronts, squalls, or rapid visibility deterioration.

---

## 3. Meteorological Variables & Completeness

The dataset was directly inspected across all 19,511 rows:

| Variable | Raw Field | Description | Unit | Range in 2024 | Missing Rate | Completeness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Air Temperature** | `TMP` | Dry bulb temperature at 2 m | $^\circ\text{C}$ | $5.0^\circ\text{C}$ to $46.4^\circ\text{C}$ (mean $25.5^\circ\text{C}$) | $3$ records ($0.02\%$) | **$99.98\%$** |
| **Dew Point** | `DEW` | Dewpoint temperature at 2 m | $^\circ\text{C}$ | $-8.0^\circ\text{C}$ to $30.0^\circ\text{C}$ | $56$ records ($0.29\%$) | **$99.71\%$** |
| **Wind Speed** | `WND` (pos 4) | Sustained horizontal wind speed | $\text{m/s}$ | $0.0\text{ m/s}$ to $10.3\text{ m/s}$ (up to $37.1\text{ km/h}$) | $5$ records ($0.03\%$) | **$99.97\%$** |
| **Wind Direction** | `WND` (pos 1) | Direction from which wind is blowing | Degrees ($^\circ$) | $0^\circ$ to $360^\circ$ (variable winds coded as 999) | $5$ records ($0.03\%$) | **$99.97\%$** |
| **Horizontal Visibility** | `VIS` | Prevailing visibility distance | Meters ($\text{m}$) | $50\text{ m}$ (fog) to $10,000\text{ m}$ (clear) | $0$ records ($0.00\%$) | **$100.00\%$** |
| **Atmospheric Pressure** | `SLP` | Sea-level pressure | $\text{hPa}$ | $989.6\text{ hPa}$ to $1024.6\text{ hPa}$ | $16,753$ records ($85.86\%$) | **$14.14\%$** (synoptic hours only) |
| **Liquid Precipitation** | `AA1` | Measured accumulation depth | $\text{mm}$ | $0.0\text{ mm}$ to $110.0\text{ mm}$ (cumulative) | $18,974$ unlogged ($97.25\%$) | **$2.75\%$** ($537$ active rain events) |
| **Cloud Ceiling Base** | `CIG` | Height of cloud base ceiling | $\text{m}$ | $30\text{ m}$ to $22,000\text{ m}$ | $5,428$ clear/missing ($27.82\%$) | **$72.18\%$** ($14,083$ reports) |
| **Cloud Layer Coverage** | `GA1`–`GA4` | Sky cover fraction & layer base | Oktas / m | Stratified 1 to 4 cloud layers | Present in $10,934$ records | **$56.04\%$** |
| **Present Weather** | `MW1`–`MW2` / `AY1` | WMO Manual 306 present weather | Code | Thunderstorm, squall, dust, rain, fog | Present in $19,129$ records | **$98.04\%$** |

---

## 4. Key Findings & Data Modality Classification

1. **NOAA ISD is Surface In-Situ Data Only**:
   - It records ground boundary layer thermodynamics (temperature, dew point, pressure) and 10-meter kinematics (wind speed, wind direction).
   - It captures point ground-level weather manifestations (visibility drop, surface rain accumulation, surface wind gusts).

2. **What NOAA ISD Does NOT Provide**:
   - **NO Doppler Weather Radar**: Zero volumetric reflectivity ($Z$), differential reflectivity ($Z_{DR}$), or radial Doppler velocity ($V_r$).
   - **NO Satellite Radiance Imagery**: Zero top-of-atmosphere infrared brightness temperatures, water vapor channels, or visible cloud reflectances.
   - **NO Optical Lightning Location**: Zero cloud-to-ground or intra-cloud lightning flash coordinates, peak currents, or pulse rates.
   - **NO 2D Continuous Spatial Field**: Observations are localized to a single geographic coordinate ($28.5665^\circ\text{ N}, 77.1031^\circ\text{ E}$).

3. **Scientific Limitation Warning**:
   - Surface station telemetry alone **CANNOT** drive or validate 0–6 hour convective-scale nowcasting models.
   - Convective nowcasting inherently requires spatial tracking of deep convective cores, updrafts, and precipitation structures via radar and geostationary satellite data.
