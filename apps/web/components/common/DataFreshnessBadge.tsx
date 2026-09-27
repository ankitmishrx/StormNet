"use client";

import React from "react";
import { DataFreshnessTier } from "@/lib/types";
import { Radio, Clock, AlertTriangle, AlertCircle, RefreshCw, Database } from "lucide-react";

interface DataFreshnessBadgeProps {
  status: DataFreshnessTier;
  radarId?: string;
  timestamp?: string;
  latencySeconds?: number;
  size?: "sm" | "md";
  showLabel?: boolean;
}

export const DataFreshnessBadge: React.FC<DataFreshnessBadgeProps> = ({
  status,
  radarId,
  timestamp,
  latencySeconds,
  size = "md",
  showLabel = true,
}) => {
  // Config for each tier
  const config = {
    LIVE: {
      label: "LIVE DWR",
      icon: Radio,
      badgeClass: "bg-emerald-50 border-emerald-300 text-emerald-800",
      dotClass: "bg-emerald-500 animate-pulse",
      desc: "Real-time Doppler Weather Radar telemetry feed",
    },
    HISTORICAL: {
      label: "HISTORICAL ARCHIVE",
      icon: Database,
      badgeClass: "bg-blue-50 border-blue-300 text-blue-800",
      dotClass: "bg-blue-500",
      desc: "Archived volume scan dataset",
    },
    REPLAY: {
      label: "SIMULATION REPLAY",
      icon: RefreshCw,
      badgeClass: "bg-indigo-50 border-indigo-300 text-indigo-800",
      dotClass: "bg-indigo-500",
      desc: "Controlled event reconstruction replay",
    },
    SAMPLE: {
      label: "DEVELOPMENT / SAMPLE",
      icon: AlertTriangle,
      badgeClass: "bg-amber-50 border-amber-300 text-amber-900",
      dotClass: "bg-amber-500 animate-pulse",
      desc: "Non-operational synthetic/calibrated demonstration dataset (SIH26084)",
    },
    STALE: {
      label: "STALE TELEMETRY",
      icon: Clock,
      badgeClass: "bg-rose-50 border-rose-300 text-rose-800",
      dotClass: "bg-rose-500 animate-ping",
      desc: "Telemetry latency exceeds 15-minute operational SLA threshold",
    },
    UNAVAILABLE: {
      label: "DWR OFFLINE",
      icon: AlertCircle,
      badgeClass: "bg-stone-100 border-stone-300 text-stone-700",
      dotClass: "bg-stone-400",
      desc: "Radar transceiver or network link currently unreachable",
    },
    PUBLIC_REAL_DATA: {
      label: "PUBLIC OBSERVATIONAL",
      icon: Radio,
      badgeClass: "bg-teal-50 border-teal-300 text-teal-800",
      dotClass: "bg-teal-500 animate-pulse",
      desc: "Legitimately accessible public observational meteorological dataset (e.g. SEVIR, GPM, NOAA ISD)",
    },
    AUTHORIZED_IMD_DATA: {
      label: "AUTHORIZED IMD DWR",
      icon: Radio,
      badgeClass: "bg-emerald-50 border-emerald-300 text-emerald-800",
      dotClass: "bg-emerald-500 animate-pulse",
      desc: "Authorized India Meteorological Department Doppler radar observation",
    },
    AUTHORIZED_MOSDAC_DATA: {
      label: "AUTHORIZED MOSDAC",
      icon: Radio,
      badgeClass: "bg-cyan-50 border-cyan-300 text-cyan-800",
      dotClass: "bg-cyan-500 animate-pulse",
      desc: "Authorized ISRO SAC / MOSDAC satellite observation product",
    },
    REAL_AUTHORIZED_DATA: {
      label: "AUTHORIZED OBSERVATIONAL",
      icon: Radio,
      badgeClass: "bg-emerald-50 border-emerald-300 text-emerald-800",
      dotClass: "bg-emerald-500 animate-pulse",
      desc: "Authentic observational data from authorized operational source",
    },
    HISTORICAL_DATA: {
      label: "HISTORICAL ARCHIVE",
      icon: Database,
      badgeClass: "bg-blue-50 border-blue-300 text-blue-800",
      dotClass: "bg-blue-500",
      desc: "Official multi-year historical archive dataset",
    },
    SAMPLE_DATA: {
      label: "DEVELOPMENT / SAMPLE",
      icon: AlertTriangle,
      badgeClass: "bg-amber-50 border-amber-300 text-amber-900",
      dotClass: "bg-amber-500 animate-pulse",
      desc: "Development/sample demonstration dataset (SIH26084)",
    },
    SYNTHETIC_DATA: {
      label: "SYNTHETIC BENCHMARK",
      icon: AlertTriangle,
      badgeClass: "bg-purple-50 border-purple-300 text-purple-900",
      dotClass: "bg-purple-500",
      desc: "Controlled synthetic kinematic convective benchmark (Not real weather observations)",
    },
    REPLAY_DATA: {
      label: "SIMULATION REPLAY",
      icon: RefreshCw,
      badgeClass: "bg-indigo-50 border-indigo-300 text-indigo-800",
      dotClass: "bg-indigo-500",
      desc: "Reconstructed observational sequence replay",
    },
  }[status] || {
    label: status,
    icon: AlertTriangle,
    badgeClass: "bg-stone-50 border-stone-300 text-stone-700",
    dotClass: "bg-stone-400",
    desc: "Unclassified data state",
  };

  const Icon = config.icon;

  if (size === "sm") {
    return (
      <div
        className={`inline-flex items-center gap-1.5 rounded-xs border px-1.5 py-0.5 font-mono text-[9px] font-semibold tracking-wider uppercase select-none ${config.badgeClass}`}
        title={`${config.label} — ${config.desc}${timestamp ? ` (${timestamp})` : ""}`}
      >
        <span className={`h-1.5 w-1.5 rounded-full ${config.dotClass}`} />
        <span>{config.label}</span>
      </div>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-2 rounded-xs border px-2 py-1 font-mono text-[10px] font-semibold tracking-wide uppercase select-none shadow-xs ${config.badgeClass}`}
      title={`${config.label} — ${config.desc}`}
    >
      <div className="flex items-center gap-1.5">
        <span className={`h-2 w-2 rounded-full ${config.dotClass}`} />
        <Icon className="h-3 w-3 shrink-0" />
      </div>

      {showLabel && (
        <div className="flex items-center gap-1.5">
          <span>{config.label}</span>
          {radarId && <span className="opacity-60">| {radarId}</span>}
          {latencySeconds !== undefined && (
            <span className="font-normal opacity-75">({latencySeconds}s delay)</span>
          )}
        </div>
      )}
    </div>
  );
};
