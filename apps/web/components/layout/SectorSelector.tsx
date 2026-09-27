"use client";

import React, { useState } from "react";
import { ChevronDown, MapPin } from "lucide-react";
import { OPERATIONAL_SECTORS } from "@/lib/constants";

interface SectorSelectorProps {
  selectedSectorId: string;
  onSelectSector: (sectorId: string) => void;
}

export const SectorSelector: React.FC<SectorSelectorProps> = ({
  selectedSectorId,
  onSelectSector,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const currentSector =
    OPERATIONAL_SECTORS.find((s) => s.id === selectedSectorId) || OPERATIONAL_SECTORS[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-8 items-center gap-2 rounded-sm border border-border-default bg-surface-card px-2.5 text-xs font-medium text-content-primary shadow-sm hover:bg-surface-subtle"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <MapPin className="h-3.5 w-3.5 text-brand-800" />
        <span className="font-semibold">{currentSector?.name}</span>
        <ChevronDown className="h-3.5 w-3.5 text-content-muted" />
      </button>

      {isOpen && (
        <div className="absolute left-0 top-full z-50 mt-1 w-72 rounded-md border border-border-default bg-surface-card p-1 shadow-matte-lg">
          <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-content-muted">
            Monitored Radar Sectors (Research Domains)
          </div>
          {OPERATIONAL_SECTORS.map((sector) => (
            <button
              key={sector.id}
              onClick={() => {
                onSelectSector(sector.id);
                setIsOpen(false);
              }}
              className={`flex w-full items-center justify-between rounded-sm px-2.5 py-1.5 text-left text-xs transition-colors ${
                sector.id === selectedSectorId
                  ? "bg-brand-100 font-medium text-brand-800"
                  : "text-content-secondary hover:bg-surface-subtle"
              }`}
            >
              <span>{sector.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
