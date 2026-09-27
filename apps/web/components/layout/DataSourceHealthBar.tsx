"use client";

import React, { useEffect, useState } from "react";
import { Radio, Satellite, Zap, Gauge } from "lucide-react";
import { StatusDot } from "@/components/common/StatusDot";
import { stormnetApi } from "@/lib/api";
import { DataSourceStatusDTO } from "@/lib/types";

export const DataSourceHealthBar: React.FC = () => {
  const [sourcesStatus, setSourcesStatus] = useState<DataSourceStatusDTO[]>([]);

  useEffect(() => {
    stormnetApi
      .getFusionSources()
      .then((sources) => {
        if (sources && sources.length > 0) {
          setSourcesStatus(sources);
        }
      })
      .catch(() => {});
  }, []);

  const getSourceDetails = (type: string) => {
    return sourcesStatus.find((s) => s.source_type === type);
  };

  const radarInfo = getSourceDetails("RADAR");
  const satInfo = getSourceDetails("SATELLITE");
  const ltgInfo = getSourceDetails("LIGHTNING");
  const awsInfo = getSourceDetails("AWS");

  const sources = [
    {
      id: "dwr",
      label: "DWR Composite",
      status: radarInfo?.is_available ? ("ONLINE" as const) : ("DEGRADED" as const),
      tierLabel: radarInfo?.data_freshness || "SAMPLE",
      latency: radarInfo ? `${Math.round(radarInfo.latency_seconds || 120)}s` : "120s",
      icon: Radio,
    },
    {
      id: "sat",
      label: "INSAT-3DR",
      status: satInfo?.is_available ? ("ONLINE" as const) : ("DEGRADED" as const),
      tierLabel: satInfo?.data_freshness || "SAMPLE",
      latency: satInfo ? `${Math.round(satInfo.latency_seconds || 180)}s` : "180s",
      icon: Satellite,
    },
    {
      id: "lln",
      label: "IITM Lightning",
      status: ltgInfo?.is_available ? ("ONLINE" as const) : ("DEGRADED" as const),
      tierLabel: ltgInfo?.data_freshness || "SAMPLE",
      latency: ltgInfo ? `${Math.round(ltgInfo.latency_seconds || 15)}s` : "15s",
      icon: Zap,
    },
    {
      id: "aws",
      label: "AWS Grid",
      status: awsInfo?.is_available ? ("ONLINE" as const) : ("DEGRADED" as const),
      tierLabel: awsInfo?.data_freshness || "SAMPLE",
      latency: awsInfo ? `${Math.round(awsInfo.latency_seconds || 300)}s` : "300s",
      icon: Gauge,
    },
  ];

  return (
    <div className="flex items-center gap-1.5 border-l border-border-default pl-3 select-none">
      {sources.map((src) => {
        const Icon = src.icon;
        return (
          <div
            key={src.id}
            className="flex items-center gap-1.5 rounded-sm border border-border-subtle bg-surface-subtle px-2 py-1 text-[11px] text-content-secondary"
            title={`${src.label} - Freshness: ${src.tierLabel} (${src.latency} delay)`}
          >
            <Icon className="h-3 w-3 text-content-muted" />
            <span className="font-medium">{src.label}</span>
            <span
              className={`font-mono text-[9px] font-semibold px-1 py-0.2 rounded border ${
                src.tierLabel === "LIVE"
                  ? "bg-emerald-50 text-emerald-800 border-emerald-200"
                  : "bg-amber-50 text-amber-900 border-amber-200"
              }`}
            >
              {src.tierLabel}
            </span>
            <span className="font-mono text-[10px] text-content-muted">[{src.latency}]</span>
            <StatusDot status={src.status} pulse={src.id === "dwr"} />
          </div>
        );
      })}
    </div>
  );
};
