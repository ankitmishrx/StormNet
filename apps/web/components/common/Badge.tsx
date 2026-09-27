import React from "react";
import clsx from "clsx";
import { SeverityLevel } from "@/lib/types";
import { SEVERITY_COLORS } from "@/lib/constants";

interface BadgeProps {
  children: React.ReactNode;
  severity?: SeverityLevel;
  variant?: "neutral" | "brand" | "outline";
  size?: "sm" | "md";
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  severity,
  variant = "neutral",
  size = "md",
  className,
}) => {
  if (severity) {
    const config = SEVERITY_COLORS[severity];
    return (
      <span
        className={clsx(
          "inline-flex items-center gap-1.5 rounded-sm border font-mono font-medium tracking-wide",
          size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs",
          config.bg,
          config.border,
          config.text,
          className,
        )}
      >
        <span className={clsx("h-1.5 w-1.5 rounded-full", config.dot)} />
        {children}
      </span>
    );
  }

  const variantStyles = {
    neutral: "bg-surface-muted text-content-secondary border-border-subtle",
    brand: "bg-brand-100 text-brand-800 border-border-default",
    outline: "bg-transparent text-content-muted border-border-default",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-sm border font-mono font-medium",
        size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs",
        variantStyles[variant],
        className,
      )}
    >
      {children}
    </span>
  );
};
