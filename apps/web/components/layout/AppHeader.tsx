"use client";

import React from "react";
import { CloudLightning, Clock } from "lucide-react";
import { SectorSelector } from "./SectorSelector";
import { DataSourceHealthBar } from "./DataSourceHealthBar";
import { Badge } from "@/components/common/Badge";

interface AppHeaderProps {
  selectedSectorId: string;
  onSelectSector: (sectorId: string) => void;
  observationTime?: string;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  selectedSectorId,
  onSelectSector,
  observationTime = "15:45 IST",
}) => {
  return (
    <header
      role="banner"
      className="flex h-[52px] w-full items-center justify-between border-b border-border-default bg-surface-card px-4 shadow-sm select-none"
    >
      {/* Left Region: Brand Identity & Operational Scope */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-brand-800 text-white shadow-sm">
          <CloudLightning className="h-5 w-5" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold tracking-tight text-brand-800">STORMNET</span>
            <Badge variant="brand" size="sm">
              SIH26084
            </Badge>
            <span className="rounded bg-amber-100 px-1.5 py-0.5 font-mono text-[9px] font-semibold text-amber-800 border border-amber-300">
              RESEARCH PROTOTYPE
            </span>
          </div>
          <span className="text-[10px] font-medium text-content-muted">
            Convective Scale Nowcasting (0–6 hr)
          </span>
        </div>

        {/* Sector Selector */}
        <div className="ml-4 pl-4 border-l border-border-subtle">
          <SectorSelector
            selectedSectorId={selectedSectorId}
            onSelectSector={onSelectSector}
          />
        </div>
      </div>

      {/* Center / Right Region: Observation Anchor & Sensor Health */}
      <div className="flex items-center gap-4">
        {/* Temporal Anchor */}
        <div className="flex items-center gap-1.5 rounded-sm border border-border-subtle bg-surface-subtle px-2.5 py-1 text-xs text-content-primary">
          <Clock className="h-3.5 w-3.5 text-brand-800" />
          <span className="font-medium text-content-muted">BASE T-0:</span>
          <span className="font-mono font-semibold">{observationTime}</span>
        </div>

        {/* Multi-Sensor Ingestion Status */}
        <DataSourceHealthBar />
      </div>
    </header>
  );
};
