/**
 * TypeScript Type Definitions for STORMNET Frontend.
 * Production-grade contracts aligned with backend schemas & UI specs.
 */

export type SeverityLevel = "GREEN" | "YELLOW" | "ORANGE" | "RED";

export type StormStatus =
  | "ACTIVE"
  | "INTENSIFYING"
  | "SEVERE"
  | "MATURE"
  | "DISSIPATING"
  | "MERGED";

export interface StormTrackPoint {
  leadTimeMinutes: number; // -60, -30, 0, 15, 30, 45, 60, ..., 360
  timestamp: string;
  coordinates: [number, number]; // [lng, lat]
  maxReflectivityDbz: number;
  uncertaintyRadiusKm: number; // Radius of error circle in km
  status: "PAST" | "CURRENT" | "PREDICTED";
}

export interface HazardPrediction {
  hazardType: "CLOUDBURST" | "HAIL" | "SQUALL" | "LIGHTNING";
  title: string;
  probability: number; // 0.0 to 1.0
  warningLevel: SeverityLevel;
  metricValue: number;
  metricUnit: string;
  thresholdAlert: string;
  timeToImpactMinutes: number;
}

export type HazardCard = HazardPrediction;

export interface StormCell {
  id: string;
  cellCode: string;
  name: string;
  status: StormStatus;
  severityLevel: SeverityLevel;
  centroidCoordinates: [number, number]; // [lng, lat]
  maxReflectivityDbz: number;
  verticallyIntegratedLiquid: number; // kg/m^2
  echoTopHeightKm: number; // km MSL
  cellSpeedKmh: number;
  cellBearingDeg: number;
  directionLabel: string; // e.g. "East-North-East"
  firstDetectedAt: string;
  lastUpdatedAt: string;
  etaCriticalMinutes: number;
  confidenceScore: number; // e.g. 0.88 (Sample value)
  boundaryCoordinates: [number, number][]; // Polygon ring
  tracks: StormTrackPoint[];
  uncertaintyConeCoordinates?: [number, number][]; // Polygon for prediction cone
  hazards: HazardPrediction[];
  affectedJurisdictions: string[];
}

export interface ForecastFrame {
  id: string;
  sectorId: string;
  leadTimeMinutes: number;
  label: string; // e.g. "NOW", "+1 HR", "+2 HR"
  timestamp: string;
  domainMaxDbz: number;
  confidenceIndex: number; // 1.0 at T-0 down to 0.40 at T+360
  convectiveInitiationPotential: "LOW" | "MODERATE" | "HIGH" | "EXTREME";
}

export interface ForecastTimeline {
  sectorId: string;
  baseTime: string;
  frames: ForecastFrame[];
  totalSteps: number;
  cadenceMinutes: number;
}

export interface RadarReflectivityContour {
  dbzLevel: number;
  color: string;
  coordinates: [number, number][][]; // GeoJSON MultiPolygon or Polygon rings
}

export interface RadarFrame {
  leadTimeMinutes: number;
  timestamp: string;
  contours: RadarReflectivityContour[];
}

export interface LightningStrike {
  id: string;
  coordinates: [number, number];
  type: "CG" | "IC"; // Cloud-to-Ground or Intra-Cloud
  peakCurrentKa: number;
  ageSeconds: number;
}

export interface StrategicLocation {
  id: string;
  name: string;
  locationType: "RADAR_SITE" | "AIRPORT" | "AWS_STATION" | "DISTRICT";
  state: string;
  district?: string;
  elevationM?: number;
  coordinates: [number, number];
}

export interface Alert {
  id: string;
  stormId?: string;
  alertIdentifier: string;
  status: string;
  msgType: string;
  severity: SeverityLevel;
  urgency: string;
  headline: string;
  description: string;
  instruction?: string;
  affectedJurisdictions?: string[];
  effectiveFrom: string;
  expiresAt: string;
  createdAt: string;
}

export type DataFreshnessTier =
  | "LIVE"
  | "HISTORICAL"
  | "REPLAY"
  | "SAMPLE"
  | "STALE"
  | "UNAVAILABLE"
  | "PUBLIC_REAL_DATA"
  | "AUTHORIZED_IMD_DATA"
  | "AUTHORIZED_MOSDAC_DATA"
  | "REAL_AUTHORIZED_DATA"
  | "HISTORICAL_DATA"
  | "SAMPLE_DATA"
  | "SYNTHETIC_DATA"
  | "REPLAY_DATA";

export interface RadarContourLevel {
  dbz_level: number;
  color: string;
  geometry: {
    type: string;
    coordinates: any;
  };
}

export interface RadarFrameDetail {
  id: string;
  radar_id: string;
  source: string;
  timestamp: string;
  product_type: string;
  resolution_km: number;
  source_resolution_km: number;
  crs: string;
  bounding_box: [number, number, number, number];
  status: string;
  total_cells_processed: number;
  max_dbz: number;
  data_freshness: DataFreshnessTier;
  station_name: string;
  contours: RadarContourLevel[];
  metadata_payload?: Record<string, any>;
}

export interface RadarFrameSummary {
  id: string;
  radar_id: string;
  source: string;
  timestamp: string;
  product_type: string;
  resolution_km: number;
  source_resolution_km: number;
  crs: string;
  bounding_box: [number, number, number, number];
  status: string;
  total_cells_processed: number;
  max_dbz: number;
  data_freshness: DataFreshnessTier;
}

export interface RadarStatusResponse {
  radar_id: string;
  station_name: string;
  status: string;
  latency_seconds: number;
  last_observation_time: string;
  active_sector: string;
  resolution_km: number;
  frequency_band: string;
  is_live: boolean;
  disclaimer: string;
}

export interface MapLayerState {
  radar: boolean;
  radarOpacity?: number; // 0.0 to 1.0 (default 0.50)
  storms: boolean;
  trajectory: boolean;
  lightning: boolean;
  rangeRings: boolean;
}

export interface DashboardState {
  selectedStormId: string;
  leadTimeMinutes: number;
  isPlaying: boolean;
  playbackSpeed: 1 | 2 | 4;
  layers: MapLayerState;
  activeSectorId: string;
}

export interface DataSourceStatusDTO {
  source_type: "RADAR" | "SATELLITE" | "LIGHTNING" | "AWS";
  provider_name: string;
  status: "ONLINE" | "DEGRADED" | "OFFLINE" | "SAMPLE";
  latency_seconds?: number;
  last_received_at?: string;
  is_available: boolean;
  data_freshness: DataFreshnessTier;
  metadata_payload?: Record<string, any>;
}

export interface FusionNetworkStatusResponse {
  sector_id: string;
  active_sources_count: number;
  total_sources_count: number;
  network_completeness_ratio: number;
  data_freshness: DataFreshnessTier;
  last_fusion_timestamp?: string;
  sources: DataSourceStatusDTO[];
  disclaimer: string;
}

export interface NowcastPredictRequest {
  sector_id?: string;
  lead_times_minutes?: number[];
  anchor_timestamp?: string;
  model_version?: string;
}

export interface NowcastFrameDTO {
  lead_time_minutes: number;
  forecast_timestamp: string;
  domain_max_dbz: number;
  confidence_score: number;
  validated_horizon: boolean;
  sample_grid_predictions?: Array<{
    node: string;
    lat: number;
    lon: number;
    pred_dbz: number;
  }>;
}

export interface NowcastResponse {
  run_id: string;
  model_name: string;
  model_version: string;
  dataset_version: string;
  feature_version: string;
  grid_version: string;
  sector_id: string;
  anchor_timestamp: string;
  inference_duration_ms: number;
  data_source_status: Record<string, any>;
  validated_horizon_minutes: number;
  frames: NowcastFrameDTO[];
  disclaimer: string;
}

