import React from "react";
import { Compass } from "lucide-react";

interface MapHUDCoordinatesProps {
  lat: number;
  lng: number;
  zoom: number;
}

export const MapHUDCoordinates: React.FC<MapHUDCoordinatesProps> = ({ lat, lng, zoom }) => {
  return (
    <div className="flex items-center gap-2 rounded-sm border border-border-default bg-surface-card/90 px-2 py-1 text-[11px] font-mono text-content-primary shadow-matte backdrop-blur-sm select-none">
      <Compass className="h-3 w-3 text-brand-800" />
      <span>{lat.toFixed(4)}°N</span>
      <span className="text-border-strong">|</span>
      <span>{lng.toFixed(4)}°E</span>
      <span className="text-border-strong">|</span>
      <span className="text-content-muted">Z: {zoom.toFixed(1)}</span>
    </div>
  );
};
