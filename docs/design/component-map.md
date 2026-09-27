# STORMNET — Component Map & Hierarchy Specification
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting (0–6 hr)  
**File Reference:** `docs/design/component-map.md`  
**Architecture:** Atomic & Modular Meteorological UI Architecture

---

## 1. System Component Tree (Atomic Hierarchy)

```
STORMNET App Root
└── NowcastingWorkspaceLayout [Template]
    ├── AppHeaderBar [Organism]
    │   ├── BrandIdentity [Molecule]
    │   │   ├── EmblemPartnerInsignia [Atom]
    │   │   ├── PlatformLogoWordmark [Atom]
    │   │   └── SubDomainTag [Atom]
    │   ├── SectorSelector [Molecule]
    │   │   ├── SectorButtonDropdown [Atom]
    │   │   └── SectorMenuModal [Molecule]
    │   ├── TemporalAnchorDisplay [Molecule]
    │   │   ├── LivePulsingDot [Atom]
    │   │   └── UtcIstTimestamp [Atom]
    │   └── DataSourceHealthBar [Molecule]
    │       ├── DataSourceIndicator (DWR) [Molecule]
    │       ├── DataSourceIndicator (INSAT) [Molecule]
    │       ├── DataSourceIndicator (Lightning) [Molecule]
    │       └── DataSourceIndicator (AWS) [Molecule]
    │
    ├── GISMapViewportContainer [Organism]
    │   ├── GISMapCanvas [Organism / Engine Wrapper]
    │   │   ├── BaseCartographyLayer [Molecule]
    │   │   ├── RadarReflectivityRasterLayer [Molecule]
    │   │   ├── StormCellPolygonsLayer [Molecule]
    │   │   │   └── CellCentroidMarker [Atom]
    │   │   ├── MotionVectorsLayer [Molecule]
    │   │   ├── LightningDischargeLayer [Molecule]
    │   │   └── AdministrativeBoundaryOverlay [Molecule]
    │   ├── MapHUDCoordinates [Molecule]
    │   ├── MapLayerTogglesMenu [Molecule]
    │   ├── ReflectivityLegendBar [Molecule]
    │   │   ├── GradientLegendBar [Atom]
    │   │   └── NumericDbzTicks [Atom]
    │   └── MapScaleNorthArrow [Atom]
    │
    ├── ForecastTimelineScrubberBar [Organism]
    │   ├── TimelinePlayControls [Molecule]
    │   │   ├── PlayPauseButton [Atom]
    │   │   ├── StepBackButton [Atom]
    │   │   ├── StepForwardButton [Atom]
    │   │   └── SpeedRateToggle [Atom]
    │   ├── TimelineTrackContainer [Molecule]
    │   │   ├── HistoricalPastZone [Atom]
    │   │   ├── PresentObservationAnchor (T-0) [Atom]
    │   │   ├── NowcastForecastZone (0-6h) [Atom]
    │   │   ├── LeadTimeConfidenceBand [Atom]
    │   │   ├── DiscreteStepTickMarks [Atom]
    │   │   └── ActiveScrubberHandle [Atom]
    │   └── CurrentLeadTimeReadout [Molecule]
    │
    └── RightStormInspectionPanel [Organism]
        ├── PanelToggleTab [Atom]
        ├── CellHeaderCard [Molecule]
        │   ├── CellIdTitle [Atom]
        │   ├── SeverityWarningPill [Atom]
        │   └── KinematicVectorSummary [Atom]
        ├── CellDiagnosticsGrid [Molecule]
        │   ├── DiagnosticMetricCard (Max dBZ) [Molecule]
        │   ├── DiagnosticMetricCard (VIL) [Molecule]
        │   ├── DiagnosticMetricCard (Echo Top) [Molecule]
        │   └── DiagnosticMetricCard (Growth Trend) [Molecule]
        ├── HazardProbabilitySection [Organism]
        │   ├── HazardProbabilityCard (Cloudburst >100mm/hr) [Molecule]
        │   ├── HazardProbabilityCard (Damaging Hail) [Molecule]
        │   ├── HazardProbabilityCard (Severe Convective Wind) [Molecule]
        │   └── HazardProbabilityCard (Lightning Density) [Molecule]
        ├── ImpactedJurisdictionsList [Molecule]
        │   └── DistrictWarningRow [Molecule]
        └── CAPAlertDispatchAction [Molecule]
            ├── GenerateCapAlertButton [Atom]
            └── ExportGeoJsonButton [Atom]
```

---

## 2. Core Organism & Molecule Specifications

### 2.1 `AppHeaderBar` (Top Navigation)
- **Role:** Persistent situational anchor for domain, observation time, and multi-sensor network health.
- **Visual Design:** Matte ivory background (`#FFFFFF`), 1px solid bottom border (`#E8E2D8`), height `52px`, horizontal padding `16px`.
- **Sub-Components:**
  1. `BrandIdentity`: Shows government / meteorological partner seal, `STORMNET` title in bold slate navy (`#1E3A5F`), and problem statement label `SIH26084`.
  2. `SectorSelector`: Select dropdown with keyboard navigation support. Allows quick switching between radar composite sectors (e.g. `Delhi-NCR DWR Composite`, `Mumbai-Konkan`, `Kolkata-Ganges Plain`).
  3. `DataSourceHealthBar`: Groups 4 `DataSourceIndicator` components:
     - Radar: `DWR Composite` (Latency: 2.1 min)
     - Satellite: `INSAT-3DR` (Rapid Scan IR: Online)
     - Lightning: `IITM / LLN` (Active: 34.2k strikes)
     - Surface: `IMD AWS Network` (98.2% healthy)
- **Accessibility:** Header landmarks `<header role="banner">`, ARIA labels for sensor status tooltips.

---

### 2.2 `GISMapCanvas` & Map Overlays
- **Role:** Primary visual workspace displaying multi-source nowcasting data layers.
- **Base Rendering:** Leaflet / MapLibre GL canvas with muted cartography, preventing visual clash with radar colormaps.
- **Dynamic Layers:**
  1. `RadarReflectivityRasterLayer`: Renders calibrated dBZ raster tiles or GeoTIFF overlays with opacity slider support (default 85% opacity).
  2. `StormCellPolygonsLayer`: Vector polygons tracing segmented convective cells.
     - **Normal State:** 1.5px solid border, subtle transparent fill.
     - **Hover State:** Highlighted stroke with tooltip showing `Cell ID` and `Max dBZ`.
     - **Selected State:** 2px high-contrast stroke with animated pulsing centroid ring.
  3. `MotionVectorsLayer`: Smooth projected trajectory arrow emanating from cell centroid. Arrow length is proportional to storm speed (km/h) with labeled 15m, 30m, 45m, and 60m future nodes.
  4. `ReflectivityLegendBar`: Compact matte HUD docked to bottom-left of map canvas. Displays 10-step dBZ scale from 15 to 70+ dBZ with physical descriptors (Drizzle → Hail / Cloudburst).

---

### 2.3 `ForecastTimelineScrubberBar` (0–6 Hour Lead Time)
- **Role:** Allows the forecaster to scrub through time from recent observations ($T-60m$ to $T-0$) to deep-learning convective predictions ($T+0$ to $T+6h$).
- **Visual Design:** Floating matte pill container (`#FAF8F5`), 1px border (`#D8D1C4`), subtle ambient shadow (`--shadow-md`), height `64px`, width `min(920px, calc(100% - 420px))`.
- **Sub-Components:**
  1. `TimelinePlayControls`:
     - `PlayPauseButton`: Toggles automated 10-minute looping playback.
     - `StepButtons`: Single-step backwards and forwards (-10 min / +10 min).
     - `SpeedSelector`: Speed chip toggle (1x, 2x, 4x).
  2. `TimelineTrack`:
     - **Past Band (-60m to 0m):** Slate grey track indicating historical observations.
     - **Anchor Node (0m / Now):** Prominent circular pin with orange ring and text `LIVE T-0`.
     - **Forecast Band (0m to +6h):** Divided into two segments:
       - *0 to +2 Hours (High Confidence):* Solid track line with 10-minute discrete ticks.
       - *+2 to +6 Hours (Convective Evolution):* Graduated hatched background indicating increasing model divergence and uncertainty.
  3. `LeadTimeDisplay`: High-contrast numeric readout: `LEAD TIME: +40 MIN` | `VALID: 16:30 IST`.

---

### 2.4 `RightStormInspectionPanel` (Cell Telemetry & Hazard Cards)
- **Role:** Deep physical diagnostics for selected storm cells, probability scoring, and jurisdiction impact warning.
- **Dimensions:** Width `380px`, vertical scroll container with custom slim scrollbar.
- **Sub-Components:**
  1. `CellHeaderCard`:
     - Cell identifier (e.g. `CELL #NCR-084-ALPHA`).
     - Real-time status pill (e.g. `RAPID INTENSIFICATION`, `MATURE SUPERCELL`).
     - Vector speed & bearing (`42 km/h @ 78° ENE`).
  2. `CellDiagnosticsGrid`:
     - 4-quadrant high-density telemetry:
       - **Max Reflectivity:** Numeric readout `62 dBZ` with peak elevation tag `(4.2 km AGL)`.
       - **VIL:** `52 kg/m²` (Vertically Integrated Liquid).
       - **Echo Top:** `15.4 km MSL` (Severe tropopause penetration).
       - **Updraft Surge:** `+7.4 dBZ / 15 min`.
  3. `HazardProbabilityCard` System:
     Four structured cards for key SIH26084 convective hazards:
     - **Cloudburst Potential (>100 mm/hr):**
       - Probability: `88%` (IMD Red Warning Level).
       - Metric: Estimated precipitation rate `115 mm/hr` in focal basin.
       - Timeline to impact: `25–40 minutes`.
     - **Severe Hail Risk (>2.5 cm):**
       - Probability: `74%` (IMD Orange Alert Level).
       - Metric: Maximum hailstone diameter `3.2 cm`.
     - **Damaging Squalls / Microbursts:**
       - Probability: `92%` (IMD Red Warning Level).
       - Metric: Estimated surface wind gusts `80–95 km/h`.
     - **Lightning Flash Density:**
       - Density: `Extreme (480 flashes/10 min)`.
  4. `ImpactedJurisdictionsList`:
     - Tabular list of administrative districts, sub-divisions, and tehsils in the projected 0–2h envelope.
     - Status badges: Red (Immediate alert), Orange (Prepare).
  5. `CAPAlertDispatchAction`:
     - One-click trigger to format and export WMO / IMD CAP XML and GeoJSON alert polygons for State Emergency Operation Centers (SEOC).

---

## 3. Global State Model & Data Architecture

```typescript
// Core Reactive State Model for STORMNET
interface StormnetAppState {
  // Temporal State
  timeline: {
    currentTimestampUtc: string; // ISO 8601
    observationAnchorUtc: string; // T-0 reference
    leadTimeOffsetMinutes: number; // 0 to 360 (+6 hr)
    playback: {
      isPlaying: boolean;
      speedMultiplier: 1 | 2 | 4;
      loopIntervalMs: number;
    };
    uncertaintyIndex: number; // 0.0 (high confidence) to 1.0 (divergence)
  };

  // Geographic & Radar Domain
  domain: {
    activeSectorId: 'delhi-ncr' | 'mumbai-konkan' | 'kolkata-ganges' | 'custom';
    viewport: {
      center: [number, number]; // [lat, lng]
      zoom: number;
      bearing: number;
    };
    activeLayers: {
      radarReflectivity: boolean;
      stormCellOutlines: boolean;
      motionVectors: boolean;
      lightningFeed: boolean;
      cloudburstZones: boolean;
      adminBoundaries: boolean;
    };
    radarOpacity: number; // 0.0 to 1.0
  };

  // Convective Cells & Telemetry
  cells: {
    activeCellId: string | null;
    identifiedCells: Array<ConvectiveCellSummary>;
    selectedCellDetail: ConvectiveCellDetail | null;
  };

  // Multi-Sensor Ingestion Status
  sensorHealth: {
    dwrRadar: { status: 'online' | 'degraded' | 'offline'; latencySec: number };
    insatSatellite: { status: 'online' | 'degraded'; rapidScan: boolean };
    lightningNetwork: { status: 'online'; strikesLastHour: number };
    awsSurfaceStations: { reportingPercentage: number; totalStations: number };
  };
}
```

---

## 4. Interaction Patterns & Forecaster Workflow

1. **Sector Ingestion & Scan:** On startup, the system locks to the regional composite (e.g. Delhi-NCR). Sensor pills confirm live data feed latency.
2. **Cell Detection & Highlighting:** The AI segmentation model automatically isolates convective cells with $Z \ge 40\text{ dBZ}$. Top severe cells are marked with red/orange centroid pins.
3. **Forecaster Cell Selection:** Forecaster clicks any cell polygon on the map:
   - Map smoothly centers and highlights the cell's 60-minute extrapolation cone.
   - Right Storm Panel automatically opens, populating VIL, Echo Top, and Cloudburst/Hail probabilities.
4. **Time Scrubbing (Nowcasting Verification):** Forecaster drags the bottom timeline scrubber forward to $T+30m$, $T+1h$, $T+2h$:
   - Radar reflectivity heatmap transitions seamlessly to predicted AI nowcast frames.
   - Motion vector endpoints shift to future predicted coordinates.
   - Hazard probabilities dynamically recalculate for each lead-time increment.
5. **Warning Generation:** Forecaster clicks `Generate CAP Advisory` to review pre-populated warning text for local emergency authorities.
