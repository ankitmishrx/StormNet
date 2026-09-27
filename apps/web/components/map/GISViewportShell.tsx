"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import maplibregl, { Map as MapLibreMap, Marker } from "maplibre-gl";
import { Plus, Minus, Compass, LocateFixed, AlertTriangle } from "lucide-react";
import { StormCell, MapLayerState, RadarFrameDetail } from "@/lib/types";
import { stormnetApi } from "@/lib/api";
import { DataFreshnessBadge } from "@/components/common/DataFreshnessBadge";
import { MapHUDCoordinates } from "./MapHUDCoordinates";
import { ReflectivityLegend } from "./ReflectivityLegend";
import { LayerToggleMenu } from "./LayerToggleMenu";
import { SAMPLE_RADAR_GEOJSON, SAMPLE_LIGHTNING_STRIKES } from "@/data/sample/radar";
import { SAMPLE_LOCATIONS, generateRangeRingCoordinates } from "@/data/sample/locations";
import { getStormStateAtLeadTime } from "@/data/sample/forecast";

interface GISViewportShellProps {
  sectorId: string;
  storms: StormCell[];
  selectedStormId: string;
  leadTimeMinutes: number;
  layers: MapLayerState;
  onSelectStorm: (stormId: string) => void;
  onToggleLayer: (layerKey: keyof MapLayerState) => void;
}

export const GISViewportShell: React.FC<GISViewportShellProps> = ({
  sectorId,
  storms,
  selectedStormId,
  leadTimeMinutes,
  layers,
  onSelectStorm,
  onToggleLayer,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Map<string, Marker>>(new Map());
  const lightningMarkersRef = useRef<Marker[]>([]);

  const [coords, setCoords] = useState<{ lat: number; lng: number; zoom: number }>({
    lat: 28.6139,
    lng: 77.209,
    zoom: 8.6,
  });

  const [radarFrame, setRadarFrame] = useState<RadarFrameDetail | null>(null);
  const [radarOpacity, setRadarOpacity] = useState<number>(layers.radarOpacity ?? 0.5);

  const selectedStorm = storms.find((s) => s.id === selectedStormId) || storms[0];

  const onSelectStormRef = useRef(onSelectStorm);
  useEffect(() => {
    onSelectStormRef.current = onSelectStorm;
  }, [onSelectStorm]);

  // Initialize MapLibre GL
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Self-contained light cream / matte cartographic style (OpenStreetMap base with matte palette)
    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        name: "STORMNET Matte Cream Cartography",
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors | IMD MoES Standards",
          },
        },
        layers: [
          {
            id: "background",
            type: "background",
            paint: {
              "background-color": "#FAF8F5",
            },
          },
          {
            id: "osm-raster",
            type: "raster",
            source: "osm",
            minzoom: 0,
            maxzoom: 19,
            paint: {
              "raster-saturation": -0.85,
              "raster-contrast": -0.15,
              "raster-opacity": 0.5,
            },
          },
        ],
      },
      center: [77.209, 28.6139],
      zoom: 8.6,
      attributionControl: false,
    });

    map.on("move", () => {
      const center = map.getCenter();
      setCoords({
        lat: Number(center.lat.toFixed(4)),
        lng: Number(center.lng.toFixed(4)),
        zoom: Number(map.getZoom().toFixed(1)),
      });
    });

    map.on("load", () => {
      // 1. DWR Range Rings Source (50km, 100km)
      const safdarjungLng = 77.2069;
      const safdarjungLat = 28.5847;
      const ring50 = generateRangeRingCoordinates(safdarjungLng, safdarjungLat, 50);
      const ring100 = generateRangeRingCoordinates(safdarjungLng, safdarjungLat, 100);

      map.addSource("range-rings", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: [
            {
              type: "Feature",
              properties: { label: "50 km DWR Range" },
              geometry: { type: "Polygon", coordinates: [ring50] },
            },
            {
              type: "Feature",
              properties: { label: "100 km DWR Range" },
              geometry: { type: "Polygon", coordinates: [ring100] },
            },
          ],
        },
      });

      map.addLayer({
        id: "range-rings-line",
        type: "line",
        source: "range-rings",
        paint: {
          "line-color": "#B8AE9D",
          "line-width": 1,
          "line-dasharray": [4, 4],
          "line-opacity": 0.6,
        },
      });

      // 2. Radar Reflectivity Contours Source
      map.addSource("radar-reflectivity", {
        type: "geojson",
        data: SAMPLE_RADAR_GEOJSON,
      });

      map.addLayer({
        id: "radar-reflectivity-fill",
        type: "fill",
        source: "radar-reflectivity",
        paint: {
          "fill-color": ["get", "color"],
          "fill-opacity": 0.45,
        },
      });

      map.addLayer({
        id: "radar-reflectivity-stroke",
        type: "line",
        source: "radar-reflectivity",
        paint: {
          "line-color": ["get", "color"],
          "line-width": 1.2,
          "line-opacity": 0.8,
        },
      });

      // 3. Storm Cell Boundaries Source
      const stormPolygons: GeoJSON.FeatureCollection = {
        type: "FeatureCollection",
        features: storms.map((s) => ({
          type: "Feature",
          properties: {
            id: s.id,
            cellCode: s.cellCode,
            severity: s.severityLevel,
            color: s.severityLevel === "RED" ? "#CF1322" : s.severityLevel === "ORANGE" ? "#D4380D" : "#D48806",
          },
          geometry: {
            type: "Polygon",
            coordinates: [s.boundaryCoordinates],
          },
        })),
      };

      map.addSource("storm-cells", {
        type: "geojson",
        data: stormPolygons,
      });

      map.addLayer({
        id: "storm-cells-fill",
        type: "fill",
        source: "storm-cells",
        paint: {
          "fill-color": ["get", "color"],
          "fill-opacity": 0.15,
        },
      });

      map.addLayer({
        id: "storm-cells-stroke",
        type: "line",
        source: "storm-cells",
        paint: {
          "line-color": ["get", "color"],
          "line-width": 1.8,
          "line-dasharray": [3, 1],
        },
      });

      // 4. Trajectory and Uncertainty Cone Sources
      map.addSource("storm-trajectory-cone", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: [],
        },
      });

      map.addLayer({
        id: "trajectory-cone-fill",
        type: "fill",
        source: "storm-trajectory-cone",
        paint: {
          "fill-color": "#1E3A5F",
          "fill-opacity": 0.1,
        },
      });

      map.addLayer({
        id: "trajectory-cone-stroke",
        type: "line",
        source: "storm-trajectory-cone",
        paint: {
          "line-color": "#1E3A5F",
          "line-width": 1,
          "line-dasharray": [3, 2],
          "line-opacity": 0.5,
        },
      });

      map.addSource("storm-trajectory-lines", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: [],
        },
      });

      map.addLayer({
        id: "trajectory-past-line",
        type: "line",
        source: "storm-trajectory-lines",
        filter: ["==", "type", "PAST"],
        paint: {
          "line-color": "#78716C",
          "line-width": 2,
        },
      });

      map.addLayer({
        id: "trajectory-predicted-line",
        type: "line",
        source: "storm-trajectory-lines",
        filter: ["==", "type", "PREDICTED"],
        paint: {
          "line-color": "#1E3A5F",
          "line-width": 2.5,
          "line-dasharray": [4, 2],
        },
      });

      // Click event on cell boundaries
      map.on("click", "storm-cells-fill", (e) => {
        const clickedId = e.features?.[0]?.properties?.id;
        if (clickedId) {
          onSelectStormRef.current(clickedId);
        }
      });

      map.on("mouseenter", "storm-cells-fill", () => {
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", "storm-cells-fill", () => {
        map.getCanvas().style.cursor = "";
      });
    });

    mapRef.current = map;
    const markers = markersRef.current;
    const lightning = lightningMarkersRef.current;

    return () => {
      // Clean up markers
      markers.forEach((m) => m.remove());
      markers.clear();
      lightning.forEach((m) => m.remove());
      lightningMarkersRef.current = [];

      map.remove();
      mapRef.current = null;
    };
  }, [storms]);

  // Fetch latest radar observation and update radar-reflectivity source
  useEffect(() => {
    let isMounted = true;
    stormnetApi
      .getLatestRadarFrame(sectorId)
      .then((frame) => {
        if (!isMounted || !frame) return;
        setRadarFrame(frame);
        const map = mapRef.current;
        if (map && map.isStyleLoaded() && frame.contours && frame.contours.length > 0) {
          const source = map.getSource("radar-reflectivity") as maplibregl.GeoJSONSource;
          if (source) {
            source.setData({
              type: "FeatureCollection",
              features: frame.contours.map((c) => ({
                type: "Feature",
                properties: {
                  dbz: c.dbz_level,
                  color: c.color,
                },
                geometry: c.geometry as any,
              })),
            });
          }
        }
      })
      .catch((err) => {
        console.warn("[STORMNET Radar] Non-blocking radar fetch notice:", err);
      });

    return () => {
      isMounted = false;
    };
  }, [sectorId]);

  // Sync radar fill opacity dynamically
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;
    if (map.getLayer("radar-reflectivity-fill")) {
      map.setPaintProperty("radar-reflectivity-fill", "fill-opacity", radarOpacity);
    }
  }, [radarOpacity]);

  // Sync Trajectory & Uncertainty Cone when selected storm changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded() || !selectedStorm) return;

    // 1. Update Trajectory Cone
    const coneSource = map.getSource("storm-trajectory-cone") as maplibregl.GeoJSONSource;
    if (coneSource && selectedStorm.uncertaintyConeCoordinates) {
      coneSource.setData({
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            properties: { id: selectedStorm.id },
            geometry: {
              type: "Polygon",
              coordinates: [selectedStorm.uncertaintyConeCoordinates],
            },
          },
        ],
      });
    }

    // 2. Update Past & Predicted Trajectory Lines
    const linesSource = map.getSource("storm-trajectory-lines") as maplibregl.GeoJSONSource;
    if (linesSource && selectedStorm.tracks) {
      const pastCoords = selectedStorm.tracks
        .filter((t) => t.status === "PAST" || t.status === "CURRENT")
        .map((t) => t.coordinates);

      const predictedCoords = selectedStorm.tracks
        .filter((t) => t.status === "CURRENT" || t.status === "PREDICTED")
        .map((t) => t.coordinates);

      const features: GeoJSON.Feature[] = [];
      if (pastCoords.length >= 2) {
        features.push({
          type: "Feature",
          properties: { type: "PAST" },
          geometry: { type: "LineString", coordinates: pastCoords },
        });
      }
      if (predictedCoords.length >= 2) {
        features.push({
          type: "Feature",
          properties: { type: "PREDICTED" },
          geometry: { type: "LineString", coordinates: predictedCoords },
        });
      }

      linesSource.setData({
        type: "FeatureCollection",
        features,
      });
    }
  }, [selectedStormId, selectedStorm]);

  // Sync Layer Visibility when layer toggles change
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    const setVis = (layerId: string, visible: boolean) => {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, "visibility", visible ? "visible" : "none");
      }
    };

    setVis("radar-reflectivity-fill", layers.radar);
    setVis("radar-reflectivity-stroke", layers.radar);
    setVis("storm-cells-fill", layers.storms);
    setVis("storm-cells-stroke", layers.storms);
    setVis("trajectory-cone-fill", layers.trajectory);
    setVis("trajectory-cone-stroke", layers.trajectory);
    setVis("trajectory-past-line", layers.trajectory);
    setVis("trajectory-predicted-line", layers.trajectory);
    setVis("range-rings-line", layers.rangeRings);

    // Toggle lightning markers
    lightningMarkersRef.current.forEach((m) => {
      const el = m.getElement();
      if (el) el.style.display = layers.lightning ? "flex" : "none";
    });

    // Toggle storm centroid markers
    markersRef.current.forEach((m) => {
      const el = m.getElement();
      if (el) el.style.display = layers.storms ? "flex" : "none";
    });
  }, [layers]);

  // Update Storm Centroids & Markers based on selected lead time
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    storms.forEach((storm) => {
      const dynamicState = getStormStateAtLeadTime(storm, leadTimeMinutes);
      const isSelected = storm.id === selectedStormId;

      let marker = markersRef.current.get(storm.id);

      if (!marker) {
        // Create custom HTML marker element
        const el = document.createElement("div");
        el.className = "storm-marker-root cursor-pointer select-none transition-transform hover:scale-105";
        el.setAttribute("role", "button");
        el.setAttribute("tabindex", "0");
        el.setAttribute("aria-label", `Storm ${storm.cellCode}, Severity: ${storm.severityLevel}`);

        el.addEventListener("click", () => {
          onSelectStorm(storm.id);
        });

        el.addEventListener("keydown", (evt) => {
          if (evt.key === "Enter" || evt.key === " ") {
            evt.preventDefault();
            onSelectStorm(storm.id);
          }
        });

        marker = new maplibregl.Marker({ element: el })
          .setLngLat(dynamicState.centroid)
          .addTo(map);

        markersRef.current.set(storm.id, marker);
      } else {
        marker.setLngLat(dynamicState.centroid);
      }

      // Update marker DOM content
      const el = marker.getElement();
      const severityColor =
        storm.severityLevel === "RED"
          ? "bg-red-600 text-white border-red-800"
          : storm.severityLevel === "ORANGE"
          ? "bg-amber-600 text-white border-amber-800"
          : "bg-yellow-500 text-stone-900 border-yellow-700";

      const ringClass = isSelected
        ? "ring-2 ring-brand-800 ring-offset-2 ring-offset-surface-canvas shadow-matte-lg"
        : "shadow-matte";

      el.innerHTML = `
        <div class="flex items-center gap-1.5 rounded-sm border px-2 py-1 font-mono text-[11px] font-bold ${severityColor} ${ringClass}">
          <span class="inline-block h-2 w-2 rounded-full ${isSelected ? "animate-pulse bg-white" : "bg-white/80"}"></span>
          <span>${storm.cellCode}</span>
          <span class="rounded bg-black/25 px-1 text-[10px]">${dynamicState.maxDbz} dBZ</span>
        </div>
      `;
    });
  }, [storms, selectedStormId, leadTimeMinutes, onSelectStorm]);

  // Add Lightning Strike Markers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    if (lightningMarkersRef.current.length === 0) {
      SAMPLE_LIGHTNING_STRIKES.forEach((strike) => {
        const el = document.createElement("div");
        el.className = "lightning-marker select-none pointer-events-none";
        el.innerHTML = `
          <div class="flex items-center justify-center h-4 w-4 rounded-full bg-amber-400/90 text-[10px] text-stone-900 font-bold border border-amber-600 shadow-sm animate-pulse" title="${strike.type} Lightning: ${strike.peakCurrentKa} kA">
            ⚡
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(strike.coordinates)
          .addTo(map);

        lightningMarkersRef.current.push(marker);
      });
    }
  }, []);

  // Zoom handlers
  const handleZoomIn = useCallback(() => {
    mapRef.current?.zoomIn();
  }, []);

  const handleZoomOut = useCallback(() => {
    mapRef.current?.zoomOut();
  }, []);

  const handleResetNorth = useCallback(() => {
    mapRef.current?.resetNorth();
  }, []);

  const handleRecenter = useCallback(() => {
    if (selectedStorm) {
      const dynamicState = getStormStateAtLeadTime(selectedStorm, leadTimeMinutes);
      mapRef.current?.flyTo({ center: dynamicState.centroid, zoom: 9 });
    }
  }, [selectedStorm, leadTimeMinutes]);

  return (
    <div className="relative h-full w-full overflow-hidden bg-[#FAF8F5] select-none">
      {/* MapLibre WebGL Canvas Container */}
      <div ref={mapContainerRef} className="absolute inset-0 h-full w-full" />

      {/* Floating Top-Left HUD: Coordinates, Radar Status & Freshness */}
      <div className="absolute left-4 top-4 z-20 flex flex-col gap-1.5 pointer-events-auto">
        <MapHUDCoordinates lat={coords.lat} lng={coords.lng} zoom={coords.zoom} />

        {/* Radar Telemetry & Freshness Status Box */}
        <div className="flex flex-col gap-1 rounded-sm border border-border-default bg-surface-card/95 p-2 shadow-matte backdrop-blur-sm">
          <div className="flex items-center justify-between gap-3">
            <DataFreshnessBadge
              status={radarFrame?.data_freshness || "SAMPLE"}
              radarId={radarFrame?.radar_id || "DWR-DEL-SAF"}
              size="sm"
            />
            <span className="font-mono text-[10px] text-content-muted">
              {radarFrame?.timestamp
                ? new Date(radarFrame.timestamp).toLocaleTimeString("en-IN", {
                    hour: "2-digit",
                    minute: "2-digit",
                    timeZone: "Asia/Kolkata",
                  }) + " IST"
                : "15:45 IST"}
            </span>
          </div>
          <div className="flex items-center justify-between border-t border-border-subtle pt-1 text-[9px] font-mono text-content-secondary">
            <span>
              Grid: <strong className="text-brand-800">{radarFrame?.resolution_km ?? 3} km</strong> (Src {radarFrame?.source_resolution_km ?? 0.5} km)
            </span>
            <span>
              Max: <strong className="text-red-700">{radarFrame?.max_dbz ?? 61.5} dBZ</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Floating Top-Right HUD: Map Layer & Zoom Controls */}
      <div className="absolute right-4 top-4 z-20 flex flex-col gap-2 pointer-events-auto">
        {/* Layer Toggle Menu with Opacity Control */}
        <LayerToggleMenu
          layers={{ ...layers, radarOpacity }}
          onToggleLayer={onToggleLayer}
          onSetRadarOpacity={setRadarOpacity}
        />

        {/* Zoom Controls */}
        <div className="flex flex-col rounded-sm border border-border-default bg-surface-card shadow-matte overflow-hidden">
          <button
            onClick={handleZoomIn}
            className="flex h-8 w-8 items-center justify-center border-b border-border-subtle hover:bg-surface-subtle text-content-primary"
            title="Zoom In"
            aria-label="Zoom In"
          >
            <Plus className="h-4 w-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="flex h-8 w-8 items-center justify-center hover:bg-surface-subtle text-content-primary"
            title="Zoom Out"
            aria-label="Zoom Out"
          >
            <Minus className="h-4 w-4" />
          </button>
        </div>

        {/* Orientation / Reset North */}
        <button
          onClick={handleResetNorth}
          className="flex h-8 w-8 items-center justify-center rounded-sm border border-border-default bg-surface-card text-content-secondary shadow-matte hover:bg-surface-subtle"
          title="Reset North Orientation"
          aria-label="Reset North"
        >
          <Compass className="h-4 w-4 text-brand-800" />
        </button>

        {/* Recenter on Selected Storm */}
        <button
          onClick={handleRecenter}
          className="flex h-8 w-8 items-center justify-center rounded-sm border border-border-default bg-surface-card text-content-secondary shadow-matte hover:bg-surface-subtle"
          title="Center on Selected Cell"
          aria-label="Center on Selected Cell"
        >
          <LocateFixed className="h-4 w-4 text-brand-800" />
        </button>
      </div>

      {/* Floating Bottom-Left HUD: Calibrated dBZ Scale */}
      <div className="absolute bottom-24 left-4 z-20 pointer-events-auto">
        <ReflectivityLegend />
      </div>
    </div>
  );
};
