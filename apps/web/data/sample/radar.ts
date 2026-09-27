import { LightningStrike } from "@/lib/types";

/**
 * DEVELOPMENT / SAMPLE RADAR REFLECTIVITY & LIGHTNING DATASET
 *
 * Provides vector polygons representing radar reflectivity dBZ bands
 * centered around convective cells in the Delhi-NCR sector.
 */

// Radar Reflectivity contours centered on Central Delhi and Gurugram storms
export const SAMPLE_RADAR_GEOJSON: GeoJSON.FeatureCollection = {
  type: "FeatureCollection",
  features: [
    // Outer envelope: 20-30 dBZ (Light rain)
    {
      type: "Feature",
      properties: {
        dbz: 25,
        color: "#457B9D",
        label: "20-30 dBZ (Light Rain)",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.05, 28.72],
            [77.20, 28.78],
            [77.40, 28.74],
            [77.48, 28.62],
            [77.40, 28.48],
            [77.20, 28.45],
            [77.02, 28.52],
            [76.95, 28.65],
            [77.05, 28.72],
          ],
        ],
      },
    },
    // Moderate envelope: 35-45 dBZ (Moderate rain / convective updraft)
    {
      type: "Feature",
      properties: {
        dbz: 40,
        color: "#2A9D8F",
        label: "35-45 dBZ (Moderate Rain)",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.12, 28.69],
            [77.26, 28.72],
            [77.36, 28.66],
            [77.34, 28.56],
            [77.22, 28.54],
            [77.10, 28.58],
            [77.12, 28.69],
          ],
        ],
      },
    },
    // Heavy core envelope: 45-55 dBZ (Heavy rain / hail initiation)
    {
      type: "Feature",
      properties: {
        dbz: 50,
        color: "#F4A261",
        label: "45-55 dBZ (Heavy Rain / Hail Initiation)",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.16, 28.66],
            [77.25, 28.68],
            [77.30, 28.64],
            [77.28, 28.60],
            [77.18, 28.59],
            [77.14, 28.62],
            [77.16, 28.66],
          ],
        ],
      },
    },
    // Severe hail core envelope: >55 dBZ (Severe hail core / Cloudburst risk)
    {
      type: "Feature",
      properties: {
        dbz: 60,
        color: "#D90429",
        label: "55-65 dBZ (Severe Hail Core / Cloudburst)",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.19, 28.645],
            [77.24, 28.655],
            [77.26, 28.630],
            [77.22, 28.615],
            [77.18, 28.625],
            [77.19, 28.645],
          ],
        ],
      },
    },
    // Gurugram Cell: 45 dBZ
    {
      type: "Feature",
      properties: {
        dbz: 48,
        color: "#E76F51",
        label: "45-52 dBZ (Convective Core)",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [76.99, 28.48],
            [77.06, 28.49],
            [77.08, 28.45],
            [77.03, 28.43],
            [76.98, 28.45],
            [76.99, 28.48],
          ],
        ],
      },
    },
  ],
};

// Sample lightning strike cluster around active cells
export const SAMPLE_LIGHTNING_STRIKES: LightningStrike[] = [
  { id: "lt-01", coordinates: [77.21, 28.64], type: "CG", peakCurrentKa: -48.5, ageSeconds: 14 },
  { id: "lt-02", coordinates: [77.23, 28.65], type: "CG", peakCurrentKa: -62.1, ageSeconds: 28 },
  { id: "lt-03", coordinates: [77.19, 28.62], type: "IC", peakCurrentKa: 24.3, ageSeconds: 45 },
  { id: "lt-04", coordinates: [77.25, 28.63], type: "CG", peakCurrentKa: -35.8, ageSeconds: 62 },
  { id: "lt-05", coordinates: [77.20, 28.66], type: "IC", peakCurrentKa: 18.9, ageSeconds: 85 },
  { id: "lt-06", coordinates: [77.04, 28.46], type: "CG", peakCurrentKa: -52.0, ageSeconds: 32 },
  { id: "lt-07", coordinates: [77.02, 28.44], type: "IC", peakCurrentKa: 31.4, ageSeconds: 74 },
  { id: "lt-08", coordinates: [77.06, 28.47], type: "CG", peakCurrentKa: -41.2, ageSeconds: 110 },
];
