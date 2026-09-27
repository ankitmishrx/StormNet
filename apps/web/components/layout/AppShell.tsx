"use client";

import React, { useState } from "react";
import { AppHeader } from "./AppHeader";
import { GISViewportShell } from "@/components/map/GISViewportShell";
import { ForecastTimelineShell } from "@/components/timeline/ForecastTimelineShell";
import { StormPanelShell } from "@/components/storm/StormPanelShell";
import { StormCell, MapLayerState } from "@/lib/types";
import { SAMPLE_STORMS } from "@/data/sample/storms";

interface AppShellProps {
  initialStorms?: StormCell[];
}

export const AppShell: React.FC<AppShellProps> = ({ initialStorms }) => {
  const storms = initialStorms && initialStorms.length > 0 ? initialStorms : SAMPLE_STORMS;

  // 1. Centralized Dashboard State
  const [selectedSectorId, setSelectedSectorId] = useState("delhi-ncr");
  const [selectedStormId, setSelectedStormId] = useState<string>(storms[0]?.id || "ST-001");
  const [leadTimeMinutes, setLeadTimeMinutes] = useState<number>(0); // 0 = NOW / T-0
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<1 | 2 | 4>(1);

  const [layers, setLayers] = useState<MapLayerState>({
    radar: true,
    storms: true,
    trajectory: true,
    lightning: true,
    rangeRings: true,
  });

  const selectedStorm: StormCell =
    storms.find((s) => s.id === selectedStormId) || storms[0] || SAMPLE_STORMS[0]!;

  const handleSelectStorm = React.useCallback((stormId: string) => {
    setSelectedStormId(stormId);
  }, []);

  const handleToggleLayer = (key: keyof MapLayerState) => {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleCycleSpeed = () => {
    setPlaybackSpeed((prev) => (prev === 1 ? 2 : prev === 2 ? 4 : 1));
  };

  const handleGenerateCapAlert = () => {
    alert(
      `[COMMON ALERTING PROTOCOL — CAP DISPATCH]\n` +
      `Alert ID: CAP-IN-DL-2026-084-001\n` +
      `Target Cell: ${selectedStorm.cellCode} (${selectedStorm.name})\n` +
      `Severity: ${selectedStorm.severityLevel} WARNING\n` +
      `Urgency: IMMEDIATE\n` +
      `Dispatched to: National Disaster Management Authority (NDMA) & Delhi SDMA\n` +
      `Areas in path: ${selectedStorm.affectedJurisdictions.join(", ")}`
    );
  };

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-surface-canvas font-sans text-content-primary">
      {/* 1. Top Navigation Bar (Fixed 52px) */}
      <AppHeader
        selectedSectorId={selectedSectorId}
        onSelectSector={setSelectedSectorId}
        observationTime="15:45 IST"
      />

      {/* 2. Main Working Workspace (Viewport Height - 52px) */}
      <main className="flex flex-1 overflow-hidden relative">
        {/* Left: GIS Map Viewport & Overlays */}
        <div className="relative flex-1 h-full overflow-hidden">
          <GISViewportShell
            sectorId={selectedSectorId}
            storms={storms}
            selectedStormId={selectedStormId}
            leadTimeMinutes={leadTimeMinutes}
            layers={layers}
            onSelectStorm={handleSelectStorm}
            onToggleLayer={handleToggleLayer}
          />

          {/* Floating Docked Timeline Scrubber */}
          <div className="absolute bottom-4 left-0 right-0 z-30 flex justify-center px-6 pointer-events-none">
            <div className="pointer-events-auto w-full max-w-4xl">
              <ForecastTimelineShell
                currentLeadTimeMinutes={leadTimeMinutes}
                onSelectLeadTime={setLeadTimeMinutes}
                isPlaying={isPlaying}
                onTogglePlay={() => setIsPlaying(!isPlaying)}
                playbackSpeed={playbackSpeed}
                onCycleSpeed={handleCycleSpeed}
              />
            </div>
          </div>
        </div>

        {/* Right: Convective Storm Intelligence Panel (Fixed 380px, collapsible) */}
        <StormPanelShell
          selectedStorm={selectedStorm}
          allStorms={storms}
          leadTimeMinutes={leadTimeMinutes}
          onSelectStorm={setSelectedStormId}
          onGenerateCapAlert={handleGenerateCapAlert}
        />
      </main>
    </div>
  );
};
