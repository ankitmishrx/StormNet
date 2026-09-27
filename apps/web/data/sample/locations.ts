import { StrategicLocation } from "@/lib/types";

export const SAMPLE_LOCATIONS: StrategicLocation[] = [
  {
    id: "loc-01",
    name: "IMD Mausam Bhavan / Safdarjung DWR",
    locationType: "RADAR_SITE",
    state: "Delhi",
    district: "New Delhi",
    elevationM: 216,
    coordinates: [77.2069, 28.5847],
  },
  {
    id: "loc-02",
    name: "Indira Gandhi International Airport (Palam DWR)",
    locationType: "AIRPORT",
    state: "Delhi",
    district: "South West Delhi",
    elevationM: 237,
    coordinates: [77.1000, 28.5562],
  },
  {
    id: "loc-03",
    name: "Noida Sector 62 AWS",
    locationType: "AWS_STATION",
    state: "Uttar Pradesh",
    district: "Gautam Buddha Nagar",
    elevationM: 200,
    coordinates: [77.3620, 28.6280],
  },
  {
    id: "loc-04",
    name: "Gurugram Cyber City AWS",
    locationType: "AWS_STATION",
    state: "Haryana",
    district: "Gurugram",
    elevationM: 220,
    coordinates: [77.0878, 28.4950],
  },
];

/**
 * Generates circular polygon coordinates for radar range rings (e.g. 50km, 100km)
 */
export function generateRangeRingCoordinates(
  centerLng: number,
  centerLat: number,
  radiusKm: number,
  steps: number = 64
): [number, number][] {
  const coords: [number, number][] = [];
  const kmToDegreeLat = 1 / 110.574;
  const kmToDegreeLng = 1 / (111.32 * Math.cos((centerLat * Math.PI) / 180));

  for (let i = 0; i <= steps; i++) {
    const angle = (i * 2 * Math.PI) / steps;
    const dx = radiusKm * Math.cos(angle) * kmToDegreeLng;
    const dy = radiusKm * Math.sin(angle) * kmToDegreeLat;
    coords.push([centerLng + dx, centerLat + dy]);
  }
  return coords;
}
