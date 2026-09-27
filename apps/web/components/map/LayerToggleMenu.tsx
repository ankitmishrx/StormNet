"use client";

import React, { useState } from "react";
import { Layers, Check, Eye } from "lucide-react";
import { MapLayerState } from "@/lib/types";

interface LayerToggleMenuProps {
  layers: MapLayerState;
  onToggleLayer: (key: keyof MapLayerState) => void;
  onSetRadarOpacity?: (opacity: number) => void;
}

export const LayerToggleMenu: React.FC<LayerToggleMenuProps> = ({
  layers,
  onToggleLayer,
  onSetRadarOpacity,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const radarOpacity = layers.radarOpacity !== undefined ? layers.radarOpacity : 0.5;

  const layerOptions: { key: keyof MapLayerState; label: string; desc: string }[] = [
    { key: "radar", label: "Radar Reflectivity", desc: "Doppler dBZ composite contours" },
    { key: "storms", label: "Storm Cells", desc: "Centroid markers & cell boundaries" },
    { key: "trajectory", label: "Trajectory & Uncertainty", desc: "Past track & forecast uncertainty cone" },
    { key: "lightning", label: "Lightning Strikes", desc: "CG & IC discharge observations" },
    { key: "rangeRings", label: "DWR Range Rings", desc: "50km / 100km / 150km Doppler rings" },
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Map Layer Settings"
        aria-expanded={isOpen}
        className={`flex h-8 w-8 items-center justify-center rounded-sm border transition-colors shadow-matte ${
          isOpen
            ? "border-brand-800 bg-brand-800 text-white"
            : "border-border-default bg-surface-card text-content-secondary hover:bg-surface-subtle"
        }`}
        title="Toggle Map Layers"
      >
        <Layers className="h-4 w-4" />
      </button>

      {isOpen && (
        <div
          role="region"
          aria-label="Layer Controls"
          className="absolute right-0 top-10 z-50 w-72 rounded-sm border border-border-default bg-surface-card p-3 shadow-matte-lg"
        >
          <div className="flex items-center justify-between border-b border-border-subtle pb-2 mb-2">
            <span className="text-[12px] font-semibold text-content-primary">
              Map Overlays
            </span>
            <span className="text-[10px] font-mono text-content-muted">
              METEOROLOGY
            </span>
          </div>

          <div className="flex flex-col gap-1.5">
            {layerOptions.map((opt) => {
              const active = Boolean(layers[opt.key]);
              return (
                <div key={opt.key} className="flex flex-col">
                  <button
                    onClick={() => onToggleLayer(opt.key)}
                    className={`flex items-start justify-between rounded-xs px-2 py-1.5 text-left text-[11px] transition-colors ${
                      active
                        ? "bg-brand-100 text-brand-900 font-medium"
                        : "text-content-secondary hover:bg-surface-subtle"
                    }`}
                  >
                    <div className="flex flex-col">
                      <span>{opt.label}</span>
                      <span className="text-[9px] text-content-muted">{opt.desc}</span>
                    </div>
                    <div
                      className={`mt-0.5 flex h-4 w-4 items-center justify-center rounded-xs border ${
                        active
                          ? "border-brand-800 bg-brand-800 text-white"
                          : "border-border-default bg-surface-card"
                      }`}
                    >
                      {active && <Check className="h-3 w-3 stroke-[2.5]" />}
                    </div>
                  </button>

                  {/* Nested Radar Opacity Control */}
                  {opt.key === "radar" && active && onSetRadarOpacity && (
                    <div className="mt-1 mb-1.5 flex flex-col gap-1 rounded bg-surface-subtle/80 px-2 py-1.5 border border-border-subtle">
                      <div className="flex justify-between text-[10px] font-medium text-content-secondary">
                        <span>Radar Fill Opacity</span>
                        <span className="font-mono">{Math.round(radarOpacity * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0.1"
                        max="1.0"
                        step="0.05"
                        value={radarOpacity}
                        onChange={(e) => onSetRadarOpacity(parseFloat(e.target.value))}
                        className="h-1.5 w-full cursor-pointer accent-brand-800 bg-border-default rounded-lg"
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

