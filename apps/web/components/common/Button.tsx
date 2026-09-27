import React from "react";
import clsx from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "secondary",
  size = "md",
  icon,
  className,
  disabled,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center gap-1.5 font-medium transition-colors select-none rounded-sm border focus:outline-none focus:ring-2 focus:ring-brand-800 focus:ring-offset-1 disabled:opacity-50 disabled:pointer-events-none";

  const sizeStyles = {
    sm: "h-7 px-2.5 text-xs",
    md: "h-8 px-3 text-xs",
    lg: "h-10 px-4 text-sm",
  };

  const variantStyles = {
    primary: "bg-brand-800 text-white border-brand-900 hover:bg-brand-900 shadow-sm",
    secondary: "bg-surface-card text-content-primary border-border-default hover:bg-surface-subtle shadow-sm",
    ghost: "bg-transparent text-content-secondary border-transparent hover:bg-surface-subtle",
    danger: "bg-rose-700 text-white border-rose-800 hover:bg-rose-800 shadow-sm",
  };

  return (
    <button
      className={clsx(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </button>
  );
};
