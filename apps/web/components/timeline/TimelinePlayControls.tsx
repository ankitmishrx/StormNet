import React from "react";
import { Play, Pause, SkipBack, SkipForward } from "lucide-react";

interface TimelinePlayControlsProps {
  isPlaying: boolean;
  onTogglePlay: () => void;
  onStepBack: () => void;
  onStepForward: () => void;
  speed: number;
  onCycleSpeed: () => void;
}

export const TimelinePlayControls: React.FC<TimelinePlayControlsProps> = ({
  isPlaying,
  onTogglePlay,
  onStepBack,
  onStepForward,
  speed,
  onCycleSpeed,
}) => {
  return (
    <div className="flex items-center gap-1">
      {/* Step Back (-15m) */}
      <button
        onClick={onStepBack}
        className="flex h-7 w-7 items-center justify-center rounded-sm border border-border-default bg-surface-card text-content-primary hover:bg-surface-subtle"
        title="Step Backward (15 min)"
      >
        <SkipBack className="h-3.5 w-3.5" />
      </button>

      {/* Play / Pause Toggle */}
      <button
        onClick={onTogglePlay}
        className="flex h-8 w-8 items-center justify-center rounded-sm bg-brand-800 text-white shadow-sm hover:bg-brand-900"
        title={isPlaying ? "Pause Timeline Loop" : "Play Timeline Loop"}
      >
        {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 fill-current ml-0.5" />}
      </button>

      {/* Step Forward (+15m) */}
      <button
        onClick={onStepForward}
        className="flex h-7 w-7 items-center justify-center rounded-sm border border-border-default bg-surface-card text-content-primary hover:bg-surface-subtle"
        title="Step Forward (15 min)"
      >
        <SkipForward className="h-3.5 w-3.5" />
      </button>

      {/* Speed Multiplier Chip */}
      <button
        onClick={onCycleSpeed}
        className="ml-1 flex h-6 items-center rounded-xs border border-border-subtle bg-surface-subtle px-1.5 font-mono text-[10px] font-semibold text-content-secondary hover:bg-surface-muted"
        title="Cycle Playback Speed"
      >
        {speed}x
      </button>
    </div>
  );
};
