# STORMNET — UI Architectural Specification
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr)  
**Document Status:** Approved Architectural Specification  
**Design Paradigm:** Matte Cream / Government Meteorological Intelligence (IMD / MoES Operational Standard)

---

## 1. Executive Architecture & Mission Context

### 1.1 Problem Statement Overview (SIH26084)
Convective phenomena—specifically severe thunderstorms, damaging hail, microbursts, and cloudbursts (>100 mm/hr precipitation)—develop rapidly on mesoscale and microscale levels (spatial scale 1–10 km, temporal lifecycles under 1–3 hours). Traditional Numerical Weather Prediction (NWP) models suffer from spin-up latency and parameterization limitations that render them inadequate for the critical 0–6 hour nowcasting window. 

**STORMNET** bridges this critical operational gap through high-resolution spatio-temporal deep learning models (assimilating Doppler Weather Radar [DWR], INSAT-3D/3DR satellite radiances, High-Density Automatic Weather Station [AWS] feeds, and Lightning Location Networks).

### 1.2 Target User Personas & Operational Environments
1. **IMD Severe Weather Forecaster & Radar Meteorologist:** Needs instant cell diagnostics (VIL, Echo Top, dBZ profiles), automated cell centroid extrapolation, and lead-time confidence degradation cues.
2. **Disaster Management Authorities (NDMA / SDMA / Relief Commissioners):** Needs clear, unambiguous hazard severity categorization (Green, Yellow, Orange, Red) and district/taluk-level impact warnings formatted for Common Alerting Protocol (CAP).
3. **Operational Environment:** Primary deployment on dual/triple display meteorological workstations in 24/7 command centers under ambient overhead fluorescent lighting. 

### 1.3 Core Visual Paradigm: Matte Light Cream / Meteorological Authority
- **Aesthetic DNA:** Clean, matte, restrained, authoritative. Warm cream/stone substrate resembling high-grade cartographic parchment and professional meteorological charts.
- **Strict Anti-Patterns:**
  - ❌ No dark sci-fi / cyberpunk neon styling.
  - ❌ No heavy glassmorphism, background blurs, or glow effects that reduce data legibility.
  - ❌ No cluttered dashboards with non-functional decorative widgets.
  - ❌ No bright uncalibrated primary colors; all status indicators adhere strictly to WMO/IMD meteorological warning standards.

---

## 2. Page Hierarchy & Master Layout Architecture

The platform employs a viewport-locked, high-density 3-pane operational layout (`100vh` non-scrolling workspace) optimized for situational awareness without cognitive fatigue.

```
+---------------------------------------------------------------------------------------------------------+
| [TOP NAVIGATION HEADER]                                                                                 |
| STORMNET Logo | Sector Selector | Observation Time | Data-Source Health Indicators | System Sync Status |
+----------------------------------------------------+----------------------------------------------------+
|                                                    | [RIGHT-SIDE STORM PANEL]                           |
|                                                    | (Width: 380px fixed, collapsible)                  |
|                                                    |                                                    |
| [INTERACTIVE GIS CONVECTIVE NOWCASTING MAP]        | 1. Active Cell Inspector (Cell ID, Stage, Speed)  |
| - DWR Reflectivity (dBZ) Raster Layer              | 2. Physical Telemetry (dBZ, VIL, Echo Top, Trend)  |
| - Identified Cell Envelopes & Vectors              | 3. Hazard Probability Matrix                       |
| - Cloudburst Alert Polygons                        |    - Severe Thunderstorm                           |
| - Floating Map Controls & dBZ Color Scale          |    - Large Hail Risk                               |
|                                                    |    - Cloudburst Risk                               |
|                                                    |    - Lightning Density                             |
|                                                    | 4. Impacted Administrative Jurisdictions           |
|                                                    | 5. CAP Warning / Advisory Dispatch                 |
+----------------------------------------------------+                                                    |
| [FORECAST TIMELINE & NOWCAST CONTROLS]             |                                                    |
| Observation T-0 | Nowcast Scrub 0 to +6 hr | Steps |                                                    |
+----------------------------------------------------+----------------------------------------------------+
```

### 2.1 Workspace Dimensions & Proportions
- **Header Bar:** Height `52px` fixed. Full width.
- **Main Working Canvas:** Calculated `calc(100vh - 52px)`.
  - **GIS Map Viewport:** Flexible (`flex-1`), occupying 100% of remaining width minus the right panel.
  - **Forecast Timeline Scrubber Bar:** Floating/docked bottom container: `64px` height, anchored `16px` above the bottom edge of the map canvas, spanning the central map zone with `24px` horizontal margins.
  - **Right Storm Intelligence Panel:** `380px` fixed width on desktop displays (`≥1440px`), `340px` on `1024px–1439px`, collapsible into a slide-over drawer on tablet/mobile screens.

---

## 3. Detailed Layout Specifications

### 3.1 Top Navigation Header Bar
- **Purpose:** Persistent branding, domain identity, spatial sector selection, and multi-sensor network health monitoring.
- **Left Region:**
  - National Emblems / IMD MoES partner insignia (subtle monochrome badge).
  - Platform Wordmark: `STORMNET` (Uppercase, 15px, Bold, Tracking +0.05em, Deep Slate Navy `#1E3A5F`).
  - Sub-label: `AI Convective Nowcasting (0–6h)`.
- **Center Region:**
  - **Sector Selector Dropdown:** Default: `Northwest India (Delhi-NCR DWR Composite)`. Options: `Western Ghats`, `Central India`, `North-East Region`, `Southern Peninsula`.
  - **Temporal Anchor:** Active base observation time: `UTC +05:30 (IST)` and ISO UTC timestamp.
- **Right Region:**
  - **Data-Source Health Matrix:** Four discrete inline sensor pills:
    1. `DWR Composite` (Live / 2.4 min latency)
    2. `INSAT-3D/3DR` (Rapid Scan Active)
    3. `Lightning LLN` (Connected / 42.1k strikes/hr)
    4. `AWS Network` (98.4% Reporting)
  - **Forecaster Mode Switcher / Settings Trigger.**

### 3.2 Main Interactive GIS Convective Map
- **Cartographic Base Layer:** Subtle warm-tinted light cartography (Matte Carto Positron or custom MapLibre style). Administrative boundaries (State, District, Taluk) rendered in subtle taupe `#C4BCB1` with low visual weight so radar echoes pop without optical noise.
- **Meteorological Dynamic Overlays:**
  1. **Doppler Radar Reflectivity ($Z$ in dBZ):** High-resolution raster heatmap (15 dBZ to 70+ dBZ). Colormap follows standard meteorological calibration adapted for light backgrounds (avoiding washed out yellows).
  2. **Convective Cell Contours & Polygons:** Algorithmically segmented convective storm cells (TITAN/SCIT-derived + AI deep-cell masks) bordered with thin 1.5px high-contrast strokes.
  3. **Extrapolated Storm Motion Vectors:** Dashed directional line with 15, 30, 45, and 60-minute forecast centroid positions.
  4. **Cloudburst Threshold Zones (>100 mm/hr):** Hatched diagonal highlight polygons representing localized flash flood danger.
  5. **Lightning Flash Clusters:** Discrete transient icon markers indicating cloud-to-ground (CG) and intra-cloud (IC) discharges.
- **On-Map Overlaid HUD Elements:**
  - **Top-Left HUD:** Active Viewport Center Coordinates (Lat/Long, Elevation), Zoom Level.
  - **Top-Right HUD:** Map Layer Visibility Toggle (Reflectivity, Velocity, VIL, Storm Vectors, Lightning, Admin Boundaries).
  - **Bottom-Left HUD:** Calibrated Reflectivity dBZ Legend (horizontal segmented scale from 15 to 70+ dBZ with numeric tick marks).
  - **Bottom-Right HUD:** Scale Bar (km) and North Arrow.

### 3.3 Forecast Timeline & Temporal Scrubber
- **Operational Cadence:** Convective nowcasting spans 0 to 6 hours with differential temporal resolution:
  - **High-Resolution Nowcast (0–2 Hours):** 10-minute discrete time steps (DWR optical flow + AI convLSTM/U-Net prediction).
  - **Extended Nowcast (2–6 Hours):** 30-minute discrete time steps (Blended AI + High-Resolution Rapid Refresh NWP).
- **Component Layout:**
  - **Playback Controls (Left):** Play/Pause button, Step Back (10 min), Step Forward (10 min), Speed toggle (1x, 2x, 4x).
  - **Timeline Track (Center):** 
    - Historical radar replay zone (Past -60m to T-0) in subtle warm slate.
    - Present Observation marker (`T-0` — Bold indicator dot with pulse animation).
    - Forecast Extrapolation zone (`+10m` to `+6h`) with graduated shaded uncertainty band (visual cue that confidence degrades gracefully over lead time).
  - **Time Display (Right):** Large, crisp, monospaced timestamp (e.g., `FORECAST T+40 min | 16:20 IST`).

### 3.4 Right-Side Storm Panel (Active Cell Intelligence)
- **State Behavior:**
  - **Default (No Cell Selected):** Displays regional storm synopsis (Total active convective cells in domain, severe warning count, domain max dBZ, highest rainfall rate).
  - **Active Selection (Cell Clicked on Map or List):** Detailed deep-cell telemetry card.
- **Panel Sections (Top to Bottom):**
  1. **Cell Header Card:**
     - Cell Identifier: `CELL #CNV-26084-A2`
     - Status Badge: `RAPIDLY INTENSIFYING` (Orange) or `SEVERE HAIL CORE` (Red)
     - Centroid: `28.6139° N, 77.2090° E` | Speed: `38 km/h ENE`
  2. **Core Radar & Kinematic Diagnostics:**
     - 4-metric grid:
       - **Max Reflectivity:** `61.5 dBZ` (Severe)
       - **Vertically Integrated Liquid (VIL):** `48 kg/m²`
       - **Echo Top Height (18 dBZ):** `14.8 km`
       - **30-Min Intensity Trend:** `+6.2 dBZ/10m` (Updraft surge)
  3. **Hazard Probability Cards:**
     - Structured cards with probability gauge, confidence score, and threshold alerts:
       - **Cloudburst Risk (>100mm/hr):** `84%` — Alert: Extreme precipitation potential in 35 min.
       - **Severe Hail Risk (>2.5cm):** `72%` — Max expected hailstone diameter: 3.5 cm.
       - **Damaging Convective Gusts:** `91%` — Peak squall speed: 75–85 km/h.
       - **Lightning Density:** `High (Severe CG hazard)` — 340 strikes/10 min.
  4. **Impacted Jurisdictions & Critical Infrastructure:**
     - District & Sub-District / Taluk breakdown.
     - Critical nodes in path: Airport runways, highway corridors, low-lying drainage basins.
  5. **CAP-Compliant Warning Generation:**
     - Pre-formatted warning bulletin for immediate dispatch to NDMA/State EOC.

---

## 4. Meteorological Warning Standards Alignment (IMD / MoES)

The UI adheres strictly to the official 4-stage color-coded warning system established by the India Meteorological Department:

| Severity Level | IMD Nomenclature | UI Token | Action / Meaning |
| :--- | :--- | :--- | :--- |
| **Level 1** | **Green (No Warning)** | `--hazard-green-*` | No severe convective activity expected. Normal operations. |
| **Level 2** | **Yellow (Watch)** | `--hazard-yellow-*` | Convective clouds developing. Forecasters/authorities should be updated. |
| **Level 3** | **Orange (Alert)** | `--hazard-orange-*` | High probability of severe thunderstorm/hail. Authorities be prepared. |
| **Level 4** | **Red (Warning)** | `--hazard-red-*` | Imminent cloudburst, severe damaging hail, extreme squall. Take action immediately. |

---

## 5. Responsive Behavior & Operational Breakpoints

1. **Large Command Center Displays (`≥1920px`):**
   - Full 3-pane operational view.
   - Right storm panel expanded to `380px`.
   - Complete multi-sensor telemetry badges visible in header without collapsing.
2. **Standard Forecaster Laptops (`1366px` to `1919px`):**
   - Right storm panel adjusted to `340px`.
   - Timeline track remains full width across map area.
   - Header indicators condense into icon + status dot format.
3. **Field Tablets & Rapid Response Devices (`768px` to `1023px`):**
   - Right storm panel transforms into a bottom sliding drawer (swipeable).
   - Timeline controls docked persistently to bottom.
   - Map controls condense into a single floating speed-dial button.
4. **Mobile Devices (`<768px`):**
   - Simplified map view with floating bottom card showing top warning.
   - Drawer opens to full screen when a cell or alert is tapped.
