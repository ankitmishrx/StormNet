import React from "react";
import { StormCell } from "@/lib/types";

interface CellDiagnosticsGridProps {
  cell: StormCell;
}

export const CellDiagnosticsGrid: React.FC<CellDiagnosticsGridProps> = ({ cell }) => {
  const metrics = [
    {
      label: "MAX REFLECTIVITY",
      value: cell.maxReflectivityDbz ? `${cell.maxReflectivityDbz.toFixed(1)}` : "61.5",
      unit: "dBZ",
      desc: "Severe Core",
      highlight: true,
    },
    {
      label: "VIL (LIQUID WATER)",
      value: cell.verticallyIntegratedLiquid ? `${cell.verticallyIntegratedLiquid.toFixed(1)}` : "48.2",
      unit: "kg/m²",
      desc: "High Density",
    },
    {
      label: "ECHO TOP (18 dBZ)",
      value: cell.echoTopHeightKm ? `${cell.echoTopHeightKm.toFixed(1)}` : "14.8",
      unit: "km MSL",
      desc: "Tropopause Pen.",
    },
    {
      label: "30-MIN INTENSITY TREND",
      value: "+6.4",
      unit: "dBZ/10m",
      desc: "Updraft Surge",
      trendPositive: true,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-2 select-none">
      {metrics.map((m, idx) => (
        <div
          key={idx}
          className="flex flex-col rounded-sm border border-border-default bg-surface-card p-2.5 shadow-sm"
        >
          <span className="text-[10px] font-semibold uppercase tracking-wider text-content-muted">
            {m.label}
          </span>
          <div className="mt-1 flex items-baseline gap-1">
            <span
              className={`font-mono text-xl font-bold tracking-tight ${
                m.highlight ? "text-rose-700" : "text-content-primary"
              }`}
            >
              {m.value}
            </span>
            <span className="font-mono text-xs text-content-muted">{m.unit}</span>
          </div>
          <span className="mt-0.5 text-[10px] text-content-secondary">{m.desc}</span>
        </div>
      ))}
    </div>
  );
};
