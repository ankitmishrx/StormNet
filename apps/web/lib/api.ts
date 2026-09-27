/**
 * Type-Safe API Client for STORMNET Backend.
 */

import {
  StormCell,
  ForecastTimeline,
  HazardCard,
  Alert,
  StrategicLocation,
  RadarFrameDetail,
  RadarFrameSummary,
  RadarStatusResponse,
  DataSourceStatusDTO,
  FusionNetworkStatusResponse,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

async function fetchJson<T>(endpoint: string, fallbackData: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      next: { revalidate: 15 },
    });
    if (!res.ok) {
      console.warn(`[STORMNET API] ${endpoint} returned ${res.status}. Falling back to default.`);
      return fallbackData;
    }
    return (await res.json()) as T;
  } catch (err) {
    console.warn(`[STORMNET API] Failed to reach ${endpoint}:`, err);
    return fallbackData;
  }
}

export const stormnetApi = {
  getStorms: async (): Promise<StormCell[]> => {
    return fetchJson<StormCell[]>("/storms", []);
  },

  getStormById: async (id: string): Promise<StormCell | null> => {
    return fetchJson<StormCell | null>(`/storms/${id}`, null);
  },

  getForecastTimeline: async (sectorId = "delhi-ncr"): Promise<ForecastTimeline> => {
    return fetchJson<ForecastTimeline>(`/forecasts?sector_id=${sectorId}`, {
      sectorId,
      baseTime: new Date().toISOString(),
      frames: [],
      totalSteps: 0,
      cadenceMinutes: 15,
    });
  },

  getHazards: async (stormId?: string): Promise<HazardCard[]> => {
    const query = stormId ? `?storm_id=${stormId}` : "";
    return fetchJson<HazardCard[]>(`/hazards${query}`, []);
  },

  getAlerts: async (): Promise<Alert[]> => {
    return fetchJson<Alert[]>("/alerts", []);
  },

  getLocations: async (): Promise<StrategicLocation[]> => {
    return fetchJson<StrategicLocation[]>("/locations", []);
  },

  getLatestRadarFrame: async (sectorId = "delhi-ncr"): Promise<RadarFrameDetail | null> => {
    return fetchJson<RadarFrameDetail | null>(`/radar/latest?sector_id=${sectorId}`, null);
  },

  getRadarFrames: async (limit = 10, offset = 0): Promise<RadarFrameSummary[]> => {
    return fetchJson<RadarFrameSummary[]>(`/radar/frames?limit=${limit}&offset=${offset}`, []);
  },

  getRadarFrameById: async (frameId: string): Promise<RadarFrameDetail | null> => {
    return fetchJson<RadarFrameDetail | null>(`/radar/${frameId}`, null);
  },

  getRadarStatus: async (radarId = "DWR-DEL-SAF"): Promise<RadarStatusResponse | null> => {
    return fetchJson<RadarStatusResponse | null>(`/radar/status?radar_id=${radarId}`, null);
  },

  getFusionStatus: async (sectorId = "delhi-ncr"): Promise<FusionNetworkStatusResponse | null> => {
    return fetchJson<FusionNetworkStatusResponse | null>(`/fusion/status?sector_id=${sectorId}`, null);
  },

  getFusionSources: async (): Promise<DataSourceStatusDTO[]> => {
    return fetchJson<DataSourceStatusDTO[]>("/fusion/sources", []);
  },

  getLatestNowcast: async (sectorId = "delhi-ncr"): Promise<import("./types").NowcastResponse | null> => {
    return fetchJson<import("./types").NowcastResponse | null>(`/nowcast/latest?sector_id=${sectorId}`, null);
  },

  getNowcastByRunId: async (runId: string): Promise<import("./types").NowcastResponse | null> => {
    return fetchJson<import("./types").NowcastResponse | null>(`/nowcast/${runId}`, null);
  },

  predictNowcast: async (payload: import("./types").NowcastPredictRequest): Promise<import("./types").NowcastResponse | null> => {
    try {
      const res = await fetch(`${API_BASE_URL}/nowcast/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) return null;
      return (await res.json()) as import("./types").NowcastResponse;
    } catch {
      return null;
    }
  },
};


