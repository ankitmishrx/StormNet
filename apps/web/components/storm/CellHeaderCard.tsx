import React from "react";
import { Navigation, Compass } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { StormCell } from "@/lib/types";

interface CellHeaderCardProps {
  cell: StormCell;
}

export const CellHeaderCard: React.FC<CellHeaderCardProps> = ({ cell }) => {
  return (
    <div className="flex flex-col gap-2 rounded-sm border border-border-default bg-surface-card p-3 shadow-sm select-none">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-content-primary">
            {cell.cellCode}
          </span>
          <Badge severity={cell.severityLevel} size="sm">
            {cell.severityLevel} ALERT
          </Badge>
        </div>
        <span className="font-mono text-[10px] text-content-muted">
          STATUS: {cell.status}
        </span>
      </div>

      {/* Vector Kinematics Summary */}
      <div className="flex items-center justify-between border-t border-border-subtle pt-2 text-xs text-content-secondary">
        <div className="flex items-center gap-1.5 font-mono text-[11px]">
          <Compass className="h-3.5 w-3.5 text-brand-800" />
          <span>
            {cell.centroidCoordinates[1].toFixed(2)}°N, {cell.centroidCoordinates[0].toFixed(2)}°E
          </span>
        </div>

        <div className="flex items-center gap-1.5 font-mono text-[11px]">
          <Navigation
            className="h-3.5 w-3.5 text-brand-800"
            style={{ transform: `rotate(${cell.cellBearingDeg || 0}deg)` }}
          />
          <span className="font-semibold">{cell.cellSpeedKmh ?? 38} km/h</span>
          <span className="text-content-muted">@ {cell.cellBearingDeg ?? 75}°</span>
        </div>
      </div>
    </div>
  );
};
