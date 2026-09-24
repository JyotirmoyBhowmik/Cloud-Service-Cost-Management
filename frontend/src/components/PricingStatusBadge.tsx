import React from "react";
import { Tag, Check, AlertCircle, HelpCircle, DollarSign, Clock } from "lucide-react";

interface PricingStatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export default function PricingStatusBadge({ status, size = "md" }: PricingStatusBadgeProps) {
  const norm = (status || "UNKNOWN").toUpperCase();

  const configs: Record<string, { label: string; bg: string; text: string; border: string; icon: any }> = {
    FREE: {
      label: "Free",
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      border: "border-emerald-200",
      icon: Check,
    },
    FREE_TIER: {
      label: "Free Tier",
      bg: "bg-teal-50",
      text: "text-teal-700",
      border: "border-teal-200",
      icon: Tag,
    },
    CONDITIONAL_FREE: {
      label: "Conditional Free",
      bg: "bg-sky-50",
      text: "text-sky-700",
      border: "border-sky-200",
      icon: Clock,
    },
    PAID: {
      label: "Chargeable",
      bg: "bg-slate-100",
      text: "text-slate-800",
      border: "border-slate-300",
      icon: DollarSign,
    },
    ESTIMATED: {
      label: "Estimated",
      bg: "bg-indigo-50",
      text: "text-indigo-700",
      border: "border-indigo-200",
      icon: Clock,
    },
    UNKNOWN: {
      label: "Unknown",
      bg: "bg-amber-50",
      text: "text-amber-700",
      border: "border-amber-200",
      icon: HelpCircle,
    },
    NOT_APPLICABLE: {
      label: "N/A",
      bg: "bg-slate-50",
      text: "text-slate-400",
      border: "border-slate-200",
      icon: AlertCircle,
    },
  };

  const conf = configs[norm] || configs.UNKNOWN;
  const Icon = conf.icon;

  const sizeClass = size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-1 text-xs";

  return (
    <span className={`inline-flex items-center gap-1 font-medium rounded-md border ${conf.bg} ${conf.text} ${conf.border} ${sizeClass}`}>
      <Icon className="w-3 h-3" />
      {conf.label}
    </span>
  );
}
