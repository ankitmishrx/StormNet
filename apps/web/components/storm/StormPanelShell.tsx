"use client";

import React, { useState } from "react";
import { Send, MapPin, ChevronRight, ChevronLeft, AlertTriangle, ShieldAlert } from "lucide-react";
import { CellHeaderCard } from "./CellHeaderCard";
import { CellDiagnosticsGrid } from "./CellDiagnosticsGrid";
import { HazardProbabilityCard } from "./HazardProbabilityCard";
import { Button } from "@/components/common/Button";
import { StormCell } from "@/lib/types";
import { getStormStateAtLeadTime } from "@/data/sample/forecast";

interface StormPanelShellProps {
  selectedStorm: StormCell;
  allStorms: StormCell[];
  leadTimeMinutes: number;
  onSelectStorm: (stormId: string) => void;
  onGenerateCapAlert?: () => void;
}

export const StormPanelShell: React.FC<StormPanelShellProps> = ({
  selectedStorm,
  allStorms,
  leadTimeMinutes,
  onSelectStorm,
  onGenerateCapAlert,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Compute dynamic deterministic state at current lead time
  const dynamicState = getStormStateAtLeadTime(selectedStorm, leadTimeMinutes);

  // Clone storm with dynamically interpolated attributes
  const activeStorm: StormCell = {
    ...selectedStorm,
    status: dynamicState.statusText as any,
    maxReflectivityDbz: dynamicState.maxDbz,
    verticallyIntegratedLiquid: dynamicState.vil,
    echoTopHeightKm: dynamicState.echoTop,
    centroidCoordinates: dynamicState.centroid,
    hazards: dynamicState.hazards,
  };

  if (isCollapsed) {
    return (
      <div className="relative flex h-full">
        <button
          onClick={() => setIsCollapsed(false)}
          className="flex h-12 w-6 items-center justify-center rounded-l-sm border-y border-l border-border-default bg-surface-card text-content-secondary shadow-matte hover:bg-surface-subtle self-center"
          title="Expand Storm Intelligence Panel"
          aria-label="Expand Storm Panel"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <aside
      className="relative flex h-full w-[380px] shrink-0 flex-col border-l border-border-default bg-surface-canvas overflow-y-auto select-none transition-all"
      aria-label="Convective Storm Intelligence Panel"
    >
      {/* Panel Top Title Header */}
      <div className="sticky top-0 z-10 flex h-[46px] items-center justify-between border-b border-border-subtle bg-surface-card px-4 shadow-xs">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-brand-800" />
          <span className="text-xs font-bold uppercase tracking-wider text-content-primary">
            Convective Cell Intelligence
          </span>
        </div>

        <button
          onClick={() => setIsCollapsed(true)}
          className="flex h-7 w-7 items-center justify-center rounded-xs text-content-muted hover:bg-surface-subtle hover:text-content-primary"
          title="Collapse Panel"
          aria-label="Collapse Panel"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      <div className="flex flex-col gap-3 p-3">
        {/* Cell Selector Switcher (Quick select between monitored cells) */}
        <div className="flex items-center gap-1.5 rounded-sm border border-border-default bg-surface-card p-1.5 shadow-xs">
          <span className="text-[10px] font-semibold text-content-muted uppercase px-1">
            Active Cells:
          </span>
          <div className="flex flex-1 gap-1">
            {allStorms.map((storm) => {
              const isSelected = storm.id === selectedStorm.id;
              const badgeColor =
                storm.severityLevel === "RED"
                  ? "bg-red-100 text-red-900 border-red-300"
                  : storm.severityLevel === "ORANGE"
                  ? "bg-orange-100 text-orange-900 border-orange-300"
                  : "bg-yellow-100 text-yellow-900 border-yellow-300";

              return (
                <button
                  key={storm.id}
                  onClick={() => onSelectStorm(storm.id)}
                  className={`flex-1 rounded-xs border px-1.5 py-1 text-center font-mono text-[10px] font-bold transition-all ${
                    isSelected
                      ? "border-brand-800 bg-brand-800 text-white shadow-xs"
                      : `${badgeColor} hover:opacity-90`
                  }`}
                >
                  {storm.id}
                </button>
              );
            })}
          </div>
        </div>

        {/* Data Status Indicator */}
        <div className="flex items-center justify-between rounded-sm border border-amber-300 bg-amber-50 px-2.5 py-1.5 text-[11px] text-amber-900">
          <div className="flex items-center gap-1.5 font-medium">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-700 shrink-0" />
            <span>Data Status: DEMO / SAMPLE DATA</span>
          </div>
          <span className="font-mono text-[10px] text-amber-800 font-semibold">
            SIH26084
          </span>
        </div>

        {/* Cell Code & Kinematics Header */}
        <CellHeaderCard cell={activeStorm} />

        {/* Physical Radar Diagnostics Grid */}
        <CellDiagnosticsGrid cell={activeStorm} />

        {/* Metadata Telemetry Row */}
        <div className="grid grid-cols-3 gap-1.5 rounded-sm border border-border-default bg-surface-card p-2 text-center text-[10px] shadow-xs">
          <div className="flex flex-col">
            <span className="text-content-muted">DETECTION TIME</span>
            <span className="font-mono font-bold text-content-primary">
              {activeStorm.firstDetectedAt}
            </span>
          </div>
          <div className="flex flex-col border-x border-border-subtle">
            <span className="text-content-muted">EST. ETA</span>
            <span className="font-mono font-bold text-rose-700">
              {Math.max(0, activeStorm.etaCriticalMinutes - leadTimeMinutes)} min
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-content-muted">CONFIDENCE</span>
            <span className="font-mono font-bold text-brand-800">
              {Math.round(
                activeStorm.confidenceScore *
                  (leadTimeMinutes <= 0
                    ? 1.0
                    : Math.max(0.4, 1.0 - (leadTimeMinutes / 360) * 0.6)) *
                  100
              )}
              %
            </span>
          </div>
        </div>

        {/* Hazard Probability Cards Section */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-content-muted">
            <span>Hazard Matrix (Research Prototype)</span>
            <span className="font-mono text-content-primary">
              {leadTimeMinutes === 0 ? "T-0 (NOW)" : `+${leadTimeMinutes} min`}
            </span>
          </div>
          {activeStorm.hazards.map((h, idx) => (
            <HazardProbabilityCard
              key={`${h.hazardType}-${idx}`}
              card={{
                hazardType: h.hazardType,
                title: h.title,
                probability: h.probability,
                warningLevel: h.warningLevel,
                metricValue: h.metricValue,
                metricUnit: h.metricUnit,
                thresholdAlert: h.thresholdAlert,
                timeToImpactMinutes: h.timeToImpactMinutes,
              }}
            />
          ))}
        </div>

        {/* Impacted Jurisdictions & Critical Nodes */}
        <div className="flex flex-col gap-1.5 rounded-sm border border-border-default bg-surface-card p-3 shadow-sm">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-content-primary">
            <MapPin className="h-3.5 w-3.5 text-brand-800" />
            <span>Impacted Jurisdictions (0–2h Path)</span>
          </div>
          <div className="flex flex-wrap gap-1 pt-1 font-mono text-[11px]">
            {activeStorm.affectedJurisdictions.map((loc, i) => (
              <span
                key={i}
                className="rounded-xs border border-border-subtle bg-surface-subtle px-1.5 py-0.5 text-content-secondary"
              >
                {loc}
              </span>
            ))}
          </div>
        </div>

        {/* CAP Advisory Generation Action */}
        <div className="pt-1 pb-3">
          <Button
            variant="primary"
            size="md"
            className="w-full"
            icon={<Send className="h-3.5 w-3.5" />}
            onClick={onGenerateCapAlert}
          >
            Dispatch CAP Warning Bulletin
          </Button>
        </div>
      </div>
    </aside>
  );
};
