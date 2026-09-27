import React from "react";
import clsx from "clsx";

interface StatusDotProps {
  status: "ONLINE" | "DEGRADED" | "OFFLINE" | "ACTIVE";
  pulse?: boolean;
  className?: string;
}

export const StatusDot: React.FC<StatusDotProps> = ({ status, pulse = false, className }) => {
  const colorClass =
    status === "ONLINE" || status === "ACTIVE"
      ? "bg-emerald-600"
      : status === "DEGRADED"
        ? "bg-amber-500"
        : "bg-rose-600";

  return (
    <span className={clsx("relative flex h-2 w-2", className)}>
      {pulse && (
        <span
          className={clsx(
            "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
            colorClass,
          )}
        />
      )}
      <span className={clsx("relative inline-flex h-2 w-2 rounded-full", colorClass)} />
    </span>
  );
};
