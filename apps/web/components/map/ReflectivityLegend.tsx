import React from "react";
import { DBZ_SCALE } from "@/lib/constants";

export const ReflectivityLegend: React.FC = () => {
  return (
    <div className="flex flex-col gap-1 rounded-sm border border-border-default bg-surface-card/95 p-2 shadow-matte backdrop-blur-sm select-none">
      <div className="flex items-center justify-between text-[10px] font-semibold uppercase tracking-wider text-content-muted">
        <span>Reflectivity (dBZ)</span>
        <span className="font-mono text-content-primary">15 – 70+</span>
      </div>

      {/* Segmented Color Bar */}
      <div className="flex h-3 w-64 overflow-hidden rounded-xs border border-border-subtle">
        {DBZ_SCALE.map((step) => (
          <div
            key={step.value}
            style={{ backgroundColor: step.color }}
            className="flex-1"
            title={`${step.label} dBZ - ${step.desc}`}
          />
        ))}
      </div>

      {/* Numerical Labels */}
      <div className="flex justify-between font-mono text-[9px] text-content-muted">
        <span>15</span>
        <span>35</span>
        <span>45</span>
        <span>55</span>
        <span>65+</span>
      </div>
    </div>
  );
};
