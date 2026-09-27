# Meteorological Radar Data Formats & Ingestion Specification
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr)  
**File Reference:** `docs/research/radar-data-format.md`  
**Status:** Approved Technical Research Document  

---

## 1. Executive Summary & Operational Context

In convective-scale nowcasting (0–6 hr), Doppler Weather Radar (DWR) provides the foundational volumetric spatial observations needed to resolve microscale convective initiation, updraft intensification, echo tops, and localized precipitation cores. 

Operational meteorological agencies worldwide (and in India, the India Meteorological Department [IMD]) operate multiple radar networks transmitting volumetric polar scans. To ensure STORMNET is vendor-agnostic and operationally deployable across IMD C-band and S-band radar networks, this document specifies:
1. Supported input file formats and structural schemas
2. Coordinate reference systems and georeferencing transformations
3. Physical meteorological variables, units, and quality control flags
4. Common 1–3 km grid generation methodology
5. Known format limitations and missing data handling protocols

---

## 2. Supported Radar Data Formats

### 2.1 WMO ODIM_H5 (OPERA Data Information Model in HDF5) — Primary Operational Format

The **ODIM_H5** specification (WMO Information System / EUMETNET OPERA) is the primary international standard for operational radar data exchange, utilized extensively by IMD for both indigenous (ISRO/BEL) and imported (Gematronik/Selex) Doppler Weather Radars.

- **Container:** Hierarchical Data Format 5 (HDF5)
- **Top-Level Attributes (`/what`, `/where`, `/how`):**
  - `/what`: Metadata indicating object type (`PVOL` for polar volume, `CVOL` for Cartesian volume, `SCAN` for single elevation sweep), source institution, date/time, and software version.
  - `/where`: Antenna geographic reference coordinates:
    - `lat`: Antenna latitude in decimal degrees WGS84 ($^{\circ}\text{N}$)
    - `lon`: Antenna longitude in decimal degrees WGS84 ($^{\circ}\text{E}$)
    - `height`: Antenna feed horn elevation above mean sea level ($m\text{ MSL}$)
  - `/how`: Operational radar hardware parameters (beamwidth, wavelength, PRF, pulse width, polarization).
- **Dataset Structure:**
  - `/dataset1`, `/dataset2`, ...: Distinct elevation sweeps within a volume scan.
  - `/dataset1/where`: Sweep-specific geometry:
    - `elangle`: Antenna elevation angle ($^{\circ}$)
    - `nbins`: Number of range bins along each radial ray
    - `rscale`: Range bin resolution ($m/\text{bin}$, typically $150\text{ m}$ to $500\text{ m}$)
    - `rstart`: Starting range ($km$, typically $0.0$)
    - `nrays`: Number of azimuth angles (typically $360$ rays for $1.0^{\circ}$ angular resolution)
  - `/dataset1/data1/data`: 2D polar matrix representing the physical quantity (azimuth $\times$ range).
  - `/dataset1/data1/what`: Variable metadata (`quantity`, `gain`, `offset`, `nodata`, `undetect`).

### 2.2 CfRadial (Climate and Forecast Convention NetCDF / CfRadial1 & CfRadial2)

Developed by the National Center for Atmospheric Research (NCAR) and adopted by the WMO, **CfRadial** encodes polar radar moments in self-describing NetCDF (Network Common Data Form) adhering to CF-1.6 conventions.

- **Container:** NetCDF-4 / HDF5
- **Coordinate Dimensions:** `time`, `range`, `sweep`.
- **Variables:**
  - `azimuth(time)`: Azimuth pointing angle in degrees clockwise from true north.
  - `elevation(time)`: Elevation pointing angle in degrees above local horizontal.
  - `range(range)`: Distance from antenna to bin center in meters.
  - `DBZH(time, range)`: Horizontal equivalent radar reflectivity factor.
  - `VRADH(time, range)`: Radial Doppler velocity.

### 2.3 Cloud-Optimized GeoTIFF (COG) & Gridded Cartesian Products

For web GIS assimilation and downstream raster nowcast models, 2D Cartesian products (such as Constant Altitude Plan Position Indicator [CAPPI] at 2.0 km and Column Maximum Composite Reflectivity [$Z_{\text{comp}}$]) are rendered as single-band georeferenced raster surfaces.

- **Container:** TIFF with GeoTIFF tags / Cloud-Optimized GeoTIFF (COG)
- **CRS:** `EPSG:4326` (WGS84 Geographic) or local UTM projection (`EPSG:32643` for NW India).
- **Pixel Encoding:** Float32 or UInt8 with linear gain/offset calibration:
  $$\text{Value}_{\text{dBZ}} = (\text{Pixel} \times \text{gain}) + \text{offset}$$

### 2.4 Vector / GeoJSON Gridded Representation (STORMNET Interchange Format)

For high-speed API transmission and web client rendering without tile-server overhead, gridded cells and vector reflectivity contour intervals are serialized into standard GeoJSON feature collections:

```json
{
  "type": "FeatureCollection",
  "metadata": {
    "radar_id": "DWR-DEL-SAF",
    "source": "DEVELOPMENT_SAMPLE",
    "timestamp": "2026-09-26T15:45:00Z",
    "product_type": "COMPOSITE_REFLECTIVITY",
    "source_resolution_km": 0.5,
    "target_grid_km": 3.0,
    "unit": "dBZ",
    "crs": "EPSG:4326"
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "grid_id": "DEL-3KM-X024-Y031",
        "reflectivity_dbz": 61.5,
        "quality_flag": "VALID",
        "sample_mode": true
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[77.20, 28.60], [77.23, 28.60], [77.23, 28.63], [77.20, 28.63], [77.20, 28.60]]]
      }
    }
  ]
}
```

---

## 3. Physical Meteorological Variables & Units

| Variable Code | Standard Name | Physical Description | Operational Range | Standard Units | Missing / No-Data Sentinel |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DBZH` / `TH` | Equivalent Reflectivity Factor | Horizontal reflectivity power proportional to $\sum D^6$ | $-30.0$ to $+75.0$ | $\text{dBZ}$ | $-9999.0$ / `NaN` |
| `VRADH` / `VR` | Radial Doppler Velocity | Mean particle motion toward/away from antenna | $-60.0$ to $+60.0$ | $m/s$ | $-9999.0$ / `NaN` |
| `WRADH` / `WR` | Spectrum Width | Doppler velocity variance / turbulence indicator | $0.0$ to $+15.0$ | $m/s$ | $-9999.0$ / `NaN` |
| `ZDR` | Differential Reflectivity | Oblateness indicator (hail vs raindrop discrimination) | $-2.0$ to $+8.0$ | $\text{dB}$ | $-9999.0$ / `NaN` |
| `RHOHV` | Correlation Coefficient | Uniformity of hydrometeor shapes (rain vs hail vs non-met) | $0.20$ to $1.02$ | Dimensionless | $-9999.0$ / `NaN` |
| `KDP` | Specific Differential Phase | Liquid water accumulation rate (cloudburst tracer) | $-2.0$ to $+12.0$ | $^{\circ}/km$ | $-9999.0$ / `NaN` |

---

## 4. Coordinate Reference Systems & Georeferencing

### 4.1 Radar Polar Coordinate Model $(r, \theta, \phi)$
A radar bin is identified by:
1. Slant range $r$ (meters from antenna)
2. Azimuth angle $\theta$ (degrees clockwise from True North)
3. Elevation angle $\phi$ (degrees above local tangent plane)

### 4.2 Curved Earth Atmospheric Refraction Model
To compute Cartesian horizontal ground range $s$ and height $h$ above mean sea level, STORMNET utilizes the standard **4/3 Effective Earth Radius Model**:

$$R' = \frac{4}{3} R_E \approx \frac{4}{3} \times 6371\text{ km} \approx 8495\text{ km}$$

$$\text{Height above antenna: } h = \sqrt{r^2 + (R')^2 + 2r R' \sin\phi} - R'$$

$$\text{Ground range: } s = R' \arcsin\left(\frac{r \cos\phi}{R' + h}\right)$$

### 4.3 Transformation to Geographic Coordinates (`EPSG:4326`)
Given antenna latitude $\phi_0$ and longitude $\lambda_0$:

$$\text{Latitude: } \phi_b = \arcsin\left(\sin\phi_0 \cos(s/R_E) + \cos\phi_0 \sin(s/R_E) \cos\theta\right)$$

$$\text{Longitude: } \lambda_b = \lambda_0 + \arctan2\left(\sin\theta \sin(s/R_E) \cos\phi_0, \cos(s/R_E) - \sin\phi_0 \sin\phi_b\right)$$

---

## 5. Target Common Grid Specification (1–3 km)

Per problem statement SIH26084, convective phenomena develop at microscale thresholds (1–10 km). STORMNET establishes a common tessellated grid over designated forecast sectors:

- **Supported Resolutions:**
  - `1 km` ($\approx 0.009^{\circ}$) — High-resolution microburst and cloudburst catchment analysis
  - `2 km` ($\approx 0.018^{\circ}$) — Intermediate convective envelope
  - `3 km` ($\approx 0.027^{\circ}$) — **Default operational resolution** for 0–6 hour nowcasting
- **Sector Coverage (e.g. Delhi-NCR Composite Domain):**
  - Minimum Longitude: $76.50^{\circ}\text{E}$
  - Minimum Latitude: $28.00^{\circ}\text{N}$
  - Maximum Longitude: $77.80^{\circ}\text{E}$
  - Maximum Latitude: $29.20^{\circ}\text{N}$
- **Cell Aggregation Metric:**
  When multiple raw radar bins fall within a target grid cell, composite reflectivity is calculated as:
  $$Z_{\text{cell}} = 10 \log_{10} \left( \frac{1}{N} \sum_{i=1}^N 10^{Z_i / 10} \right)$$
  (Logarithmic averaging of linear radar reflectivity factor $z_i = 10^{Z_i/10}$).

---

## 6. Data Quality, Validation & Limitations

### 6.1 Validation Rules
1. **Timestamp Check:** Must be valid ISO 8601; must not be more than 10 minutes in the future or older than 30 days for live mode.
2. **Geographic Check:** Antenna coordinates must be within the territorial bounds of India ($6.0^{\circ}\text{N} \le \text{lat} \le 38.0^{\circ}\text{N}$, $68.0^{\circ}\text{E} \le \text{lon} \le 98.0^{\circ}\text{E}$).
3. **Reflectivity Quality Flagging:**
   - Values $< 10\text{ dBZ}$: Marked as `NON_PRECIPITATING / CLEAR_AIR`
   - Values $\ge 55\text{ dBZ}$: Marked as `SEVERE_CONVECTIVE_HAIL_HAZARD`
   - Spurious speckle noise (isolated single bins): Filtered via 2D median kernel.

### 6.2 Data Limitations & Disclaimers
1. **Development/Sample Data Rule:** In Phase 4 development, sample datasets are clearly tagged with `"source": "DEVELOPMENT_SAMPLE"` and marked as `SAMPLE DATA` in all API responses.
2. **Beam Blockage & Cone of Silence:** Real DWR observations experience ground clutter within 5 km and beam elevation gaps directly overhead ("cone of silence"). The architecture accounts for multi-radar compositing to fill these physical blind spots.
