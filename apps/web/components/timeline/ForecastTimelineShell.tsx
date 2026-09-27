"use client";

import React, { useEffect, useCallback } from "react";
import { TimelinePlayControls } from "./TimelinePlayControls";

interface ForecastTimelineShellProps {
  currentLeadTimeMinutes: number;
  onSelectLeadTime: (leadTime: number) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  playbackSpeed: 1 | 2 | 4;
  onCycleSpeed: () => void;
}

export const TIMELINE_STEPS = [
  { label: "-45m", val: -45, type: "past", isValidated: true },
  { label: "-30m", val: -30, type: "past", isValidated: true },
  { label: "-15m", val: -15, type: "past", isValidated: true },
  { label: "NOW", val: 0, type: "now", isValidated: true },
  { label: "+15m", val: 15, type: "forecast", isValidated: true },
  { label: "+30m", val: 30, type: "forecast", isValidated: true },
  { label: "+45m", val: 45, type: "forecast", isValidated: false },
  { label: "+1 HR", val: 60, type: "forecast", isValidated: false },
  { label: "+1.5H", val: 90, type: "forecast", isValidated: false },
  { label: "+2 HR", val: 120, type: "forecast", isValidated: false },
  { label: "+3 HR", val: 180, type: "forecast", isValidated: false },
  { label: "+4 HR", val: 240, type: "forecast", isValidated: false },
  { label: "+5 HR", val: 300, type: "forecast", isValidated: false },
  { label: "+6 HR", val: 360, type: "forecast", isValidated: false },
];

export const ForecastTimelineShell: React.FC<ForecastTimelineShellProps> = ({
  currentLeadTimeMinutes,
  onSelectLeadTime,
  isPlaying,
  onTogglePlay,
  playbackSpeed,
  onCycleSpeed,
}) => {
  // Step backward handler
  const handleStepBack = useCallback(() => {
    const idx = TIMELINE_STEPS.findIndex((s) => s.val === currentLeadTimeMinutes);
    if (idx > 0) {
      const prevStep = TIMELINE_STEPS[idx - 1];
      if (prevStep) onSelectLeadTime(prevStep.val);
    }
  }, [currentLeadTimeMinutes, onSelectLeadTime]);

  // Step forward handler
  const handleStepForward = useCallback(() => {
    const idx = TIMELINE_STEPS.findIndex((s) => s.val === currentLeadTimeMinutes);
    if (idx < TIMELINE_STEPS.length - 1) {
      const nextStep = TIMELINE_STEPS[idx + 1];
      if (nextStep) onSelectLeadTime(nextStep.val);
    } else if (TIMELINE_STEPS[0]) {
      // Loop to beginning
      onSelectLeadTime(TIMELINE_STEPS[0].val);
    }
  }, [currentLeadTimeMinutes, onSelectLeadTime]);

  // Playback timer loop with proper cleanup to prevent memory leaks
  useEffect(() => {
    if (!isPlaying) return;

    const intervalDuration = Math.round(1500 / playbackSpeed);

    const timer = setInterval(() => {
      handleStepForward();
    }, intervalDuration);

    return () => clearInterval(timer);
  }, [isPlaying, playbackSpeed, handleStepForward]);

  // Keyboard navigation shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.code === "Space") {
        e.preventDefault();
        onTogglePlay();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        handleStepBack();
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        handleStepForward();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onTogglePlay, handleStepBack, handleStepForward]);

  // Confidence index computation (1.0 at 0m, 0.40 at 360m)
  const confidenceScore =
    currentLeadTimeMinutes <= 0
      ? 1.0
      : Math.max(0.4, Number((1.0 - (currentLeadTimeMinutes / 360) * 0.6).toFixed(2)));

  return (
    <div
      role="region"
      aria-label="Nowcast Timeline"
      className="flex h-16 w-full items-center justify-between rounded-md border border-border-default bg-surface-card/95 px-4 shadow-matte-md backdrop-blur-sm select-none"
    >
      {/* Left: Playback Controls */}
      <TimelinePlayControls
        isPlaying={isPlaying}
        onTogglePlay={onTogglePlay}
        onStepBack={handleStepBack}
        onStepForward={handleStepForward}
        speed={playbackSpeed}
        onCycleSpeed={onCycleSpeed}
      />

      {/* Center: Timeline Scrubber Track */}
      <div className="mx-6 flex flex-1 flex-col gap-1">
        <div className="relative flex items-center justify-between">
          {/* Background Track Line */}
          <div className="absolute top-1/2 left-0 right-0 h-0.5 -translate-y-1/2 bg-border-subtle z-0" />

          {TIMELINE_STEPS.map((step) => {
            const isSelected = step.val === currentLeadTimeMinutes;
            const isNow = step.val === 0;

            return (
              <button
                key={step.val}
                onClick={() => onSelectLeadTime(step.val)}
                aria-label={`Lead time ${step.label}`}
                aria-pressed={isSelected}
                className={`group relative z-10 flex flex-col items-center focus:outline-none transition-transform ${
                  isSelected ? "scale-110" : "opacity-80 hover:opacity-100"
                }`}
              >
                {/* Node Pin */}
                <div
                  className={`h-2.5 w-2.5 rounded-full border transition-all ${
                    isSelected
                      ? "border-brand-800 bg-brand-800 ring-2 ring-brand-100 ring-offset-1"
                      : isNow
                      ? "border-red-600 bg-red-600 ring-2 ring-red-200"
                      : !step.isValidated
                      ? "border-amber-400/80 bg-amber-50/50 border-dashed"
                      : "border-border-default bg-surface-subtle group-hover:border-border-strong"
                  }`}
                  title={step.isValidated ? "Validated Empirical Nowcast (<=30m)" : "Experimental Horizon (>30m) - Unvalidated"}
                />

                {/* Label */}
                <span
                  className={`mt-1 font-mono text-[9px] ${
                    isSelected
                      ? "font-bold text-brand-800"
                      : isNow
                      ? "font-bold text-red-700"
                      : !step.isValidated
                      ? "text-content-muted/70 italic"
                      : "text-content-muted"
                  }`}
                >
                  {step.label}
                </span>
              </button>
            );
          })}
        </div>

        {/* Confidence Band Bar & Single Scan Range Indicator */}
        <div className="flex items-center justify-between text-[9px] text-content-muted">
          <span>
            <strong className="text-emerald-700">Validated Horizon: 30 min</strong> (Spatiotemporal U-Net)
          </span>
          <span className="font-mono">
            {currentLeadTimeMinutes <= 30 ? (
              <span className="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                VALIDATED NOWCAST FRAME
              </span>
            ) : (
              <span className="text-amber-700 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                RESEARCH PROTOTYPE / UNVALIDATED HORIZON
              </span>
            )}
          </span>
          <span className="italic text-amber-800/80">+45m to +6h: Experimental Architecture</span>
        </div>
      </div>

      {/* Right: Active Readout Box */}
      <div className="flex flex-col items-end border-l border-border-subtle pl-4 min-w-[130px]">
        <span className="text-[9px] font-semibold tracking-wider text-content-muted uppercase">
          {currentLeadTimeMinutes <= 30 ? "Lead Time (Validated)" : "Lead Time (Prototype)"}
        </span>
        <span
          className={`font-mono text-xs font-bold ${
            currentLeadTimeMinutes > 30 ? "text-amber-700" : "text-brand-800"
          }`}
        >
          {currentLeadTimeMinutes === 0
            ? "LIVE T-0"
            : currentLeadTimeMinutes < 0
            ? `OBSERVED ${currentLeadTimeMinutes}m`
            : `LEAD +${currentLeadTimeMinutes}m`}
        </span>
        {currentLeadTimeMinutes > 30 && (
          <span className="text-[8px] font-mono font-semibold text-amber-700 uppercase">
            NOT VALIDATED
          </span>
        )}
      </div>
    </div>
  );
};
