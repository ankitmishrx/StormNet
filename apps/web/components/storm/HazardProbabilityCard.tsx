import React from "react";
import { CloudRain, AlertTriangle, Wind, Zap } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { HazardCard } from "@/lib/types";

interface HazardProbabilityCardProps {
  card: HazardCard;
}

export const HazardProbabilityCard: React.FC<HazardProbabilityCardProps> = ({ card }) => {
  const getIcon = () => {
    switch (card.hazardType) {
      case "CLOUDBURST":
        return CloudRain;
      case "HAIL":
        return AlertTriangle;
      case "SQUALL":
        return Wind;
      case "LIGHTNING":
        return Zap;
      default:
        return AlertTriangle;
    }
  };

  const Icon = getIcon();
  const percentage = Math.round(card.probability * 100);

  return (
    <div className="flex flex-col gap-2 rounded-sm border border-border-default bg-surface-card p-3 shadow-sm select-none">
      {/* Header & Warning Badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-sm bg-surface-subtle text-brand-800">
            <Icon className="h-3.5 w-3.5" />
          </div>
          <span className="text-xs font-semibold text-content-primary">{card.title}</span>
        </div>
        <Badge severity={card.warningLevel} size="sm">
          {card.warningLevel}
        </Badge>
      </div>

      {/* Probability Gauge & Key Metric */}
      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-1.5">
          <span className="font-mono text-2xl font-bold tracking-tight text-content-primary">
            {percentage}%
          </span>
          <span className="text-[10px] text-content-muted">Probability</span>
        </div>

        {card.metricValue && (
          <div className="text-right font-mono text-xs font-semibold text-content-primary">
            <span>{card.metricValue}</span>{" "}
            <span className="text-[10px] text-content-muted">{card.metricUnit}</span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-muted">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            card.warningLevel === "RED"
              ? "bg-rose-600"
              : card.warningLevel === "ORANGE"
                ? "bg-amber-500"
                : "bg-emerald-600"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Threshold Reference Alert Note */}
      <div className="flex items-center justify-between rounded-xs bg-surface-subtle px-2 py-1 text-[11px] text-content-secondary">
        <span>{card.thresholdAlert}</span>
      </div>

      {/* Scientific Integrity Status */}
      <div className="text-[9px] font-mono text-content-muted tracking-tight">
        STATUS: RESEARCH PROTOTYPE / NOT VALIDATED
      </div>
    </div>
  );
};
