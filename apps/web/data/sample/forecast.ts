import { ForecastFrame, StormCell, HazardPrediction, StormTrackPoint } from "@/lib/types";

/**
 * DEVELOPMENT / SAMPLE FORECAST TIMELINE DATASET (0–6 Hours)
 *
 * NOTE: These are deterministic development fixtures for testing and UI demonstration.
 */

export const FORECAST_FRAMES: ForecastFrame[] = [
  { id: "f-000", sectorId: "delhi-ncr", leadTimeMinutes: 0, label: "NOW", timestamp: "15:45 IST", domainMaxDbz: 61.5, confidenceIndex: 1.0, convectiveInitiationPotential: "HIGH" },
  { id: "f-015", sectorId: "delhi-ncr", leadTimeMinutes: 15, label: "+15m", timestamp: "16:00 IST", domainMaxDbz: 62.0, confidenceIndex: 0.95, convectiveInitiationPotential: "EXTREME" },
  { id: "f-030", sectorId: "delhi-ncr", leadTimeMinutes: 30, label: "+30m", timestamp: "16:15 IST", domainMaxDbz: 60.5, confidenceIndex: 0.92, convectiveInitiationPotential: "EXTREME" },
  { id: "f-045", sectorId: "delhi-ncr", leadTimeMinutes: 45, label: "+45m", timestamp: "16:30 IST", domainMaxDbz: 59.0, confidenceIndex: 0.88, convectiveInitiationPotential: "HIGH" },
  { id: "f-060", sectorId: "delhi-ncr", leadTimeMinutes: 60, label: "+1 HR", timestamp: "16:45 IST", domainMaxDbz: 58.5, confidenceIndex: 0.85, convectiveInitiationPotential: "HIGH" },
  { id: "f-090", sectorId: "delhi-ncr", leadTimeMinutes: 90, label: "+1.5H", timestamp: "17:15 IST", domainMaxDbz: 56.5, confidenceIndex: 0.80, convectiveInitiationPotential: "HIGH" },
  { id: "f-120", sectorId: "delhi-ncr", leadTimeMinutes: 120, label: "+2 HR", timestamp: "17:45 IST", domainMaxDbz: 54.0, confidenceIndex: 0.75, convectiveInitiationPotential: "MODERATE" },
  { id: "f-150", sectorId: "delhi-ncr", leadTimeMinutes: 150, label: "+2.5H", timestamp: "18:15 IST", domainMaxDbz: 52.5, confidenceIndex: 0.70, convectiveInitiationPotential: "MODERATE" },
  { id: "f-180", sectorId: "delhi-ncr", leadTimeMinutes: 180, label: "+3 HR", timestamp: "18:45 IST", domainMaxDbz: 50.5, confidenceIndex: 0.65, convectiveInitiationPotential: "MODERATE" },
  { id: "f-240", sectorId: "delhi-ncr", leadTimeMinutes: 240, label: "+4 HR", timestamp: "19:45 IST", domainMaxDbz: 47.0, confidenceIndex: 0.55, convectiveInitiationPotential: "MODERATE" },
  { id: "f-300", sectorId: "delhi-ncr", leadTimeMinutes: 300, label: "+5 HR", timestamp: "20:45 IST", domainMaxDbz: 43.0, confidenceIndex: 0.48, convectiveInitiationPotential: "LOW" },
  { id: "f-360", sectorId: "delhi-ncr", leadTimeMinutes: 360, label: "+6 HR", timestamp: "21:45 IST", domainMaxDbz: 39.0, confidenceIndex: 0.40, convectiveInitiationPotential: "LOW" },
];

/**
 * Deterministically computes the storm's spatial location and hazard state at a chosen lead time.
 * Interpolates between nearest track nodes without generating random numbers.
 */
export function getStormStateAtLeadTime(storm: StormCell, leadTimeMinutes: number): {
  centroid: [number, number];
  maxDbz: number;
  vil: number;
  echoTop: number;
  hazards: HazardPrediction[];
  statusText: StormCell["status"];
} {
  const tracks = storm.tracks;
  if (!tracks || tracks.length === 0) {
    return {
      centroid: storm.centroidCoordinates,
      maxDbz: storm.maxReflectivityDbz,
      vil: storm.verticallyIntegratedLiquid,
      echoTop: storm.echoTopHeightKm,
      hazards: storm.hazards,
      statusText: storm.status,
    };
  }

  // Find surrounding track points
  let prev: StormTrackPoint = tracks[0]!;
  let next: StormTrackPoint = tracks[tracks.length - 1]!;

  for (let i = 0; i < tracks.length - 1; i++) {
    const currentPoint = tracks[i]!;
    const nextPoint = tracks[i + 1]!;
    if (currentPoint.leadTimeMinutes <= leadTimeMinutes && nextPoint.leadTimeMinutes >= leadTimeMinutes) {
      prev = currentPoint;
      next = nextPoint;
      break;
    }
  }

  // Linear interpolation factor
  const range = next.leadTimeMinutes - prev.leadTimeMinutes;
  const factor = range > 0 ? (leadTimeMinutes - prev.leadTimeMinutes) / range : 0;

  const lng = prev.coordinates[0] + (next.coordinates[0] - prev.coordinates[0]) * factor;
  const lat = prev.coordinates[1] + (next.coordinates[1] - prev.coordinates[1]) * factor;
  const dbz = prev.maxReflectivityDbz + (next.maxReflectivityDbz - prev.maxReflectivityDbz) * factor;

  // Scale VIL and Echo Top proportionately to reflectivity
  const dbzRatio = dbz / (storm.maxReflectivityDbz || 1);
  const vil = Number((storm.verticallyIntegratedLiquid * dbzRatio).toFixed(1));
  const echoTop = Number((storm.echoTopHeightKm * Math.sqrt(Math.max(0.1, dbzRatio))).toFixed(1));

  // Scale hazard probabilities deterministically with decay past peak
  const decayFactor = Math.max(0.2, 1.0 - (leadTimeMinutes / 360) * 0.6);
  const updatedHazards: HazardPrediction[] = storm.hazards.map((h) => {
    const adjustedProb = Number(Math.min(0.99, Math.max(0.05, h.probability * decayFactor)).toFixed(2));
    let level = h.warningLevel;
    if (adjustedProb >= 0.75) level = "RED";
    else if (adjustedProb >= 0.50) level = "ORANGE";
    else if (adjustedProb >= 0.25) level = "YELLOW";
    else level = "GREEN";

    const adjustedValue = Number((h.metricValue * decayFactor).toFixed(1));
    const timeToImpact = Math.max(0, h.timeToImpactMinutes - leadTimeMinutes);

    return {
      ...h,
      probability: adjustedProb,
      warningLevel: level,
      metricValue: adjustedValue,
      timeToImpactMinutes: timeToImpact,
    };
  });

  let statusText: StormCell["status"] = storm.status;
  if (leadTimeMinutes > 180) {
    statusText = "DISSIPATING";
  } else if (leadTimeMinutes > 60) {
    statusText = "MATURE";
  }

  return {
    centroid: [Number(lng.toFixed(4)), Number(lat.toFixed(4))],
    maxDbz: Number(dbz.toFixed(1)),
    vil,
    echoTop,
    hazards: updatedHazards,
    statusText,
  };
}
