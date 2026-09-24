import React from "react";
import { CheckCircle2, AlertTriangle, AlertOctagon, XCircle, HelpCircle } from "lucide-react";

interface ThresholdBadgeProps {
  state: string;
  size?: "sm" | "md";
}

export default function ThresholdBadge({ state, size = "md" }: ThresholdBadgeProps) {
  const norm = (state || "GREY").toUpperCase();

  const configs: Record<string, { label: string; bg: string; dot: string; icon: any }> = {
    GREEN: {
      label: "Normal (<75%)",
      bg: "bg-emerald-50 text-emerald-800 border-emerald-200",
      dot: "bg-emerald-500",
      icon: CheckCircle2,
    },
    AMBER: {
      label: "Warning (75-90%)",
      bg: "bg-amber-50 text-amber-800 border-amber-200",
      dot: "bg-amber-500",
      icon: AlertTriangle,
    },
    ORANGE: {
      label: "Near Limit (90-100%)",
      bg: "bg-orange-50 text-orange-800 border-orange-200",
      dot: "bg-orange-500",
      icon: AlertOctagon,
    },
    RED: {
      label: "Critical (>100%)",
      bg: "bg-rose-50 text-rose-800 border-rose-200",
      dot: "bg-rose-500 animate-pulse",
      icon: XCircle,
    },
    GREY: {
      label: "Stale / No Data",
      bg: "bg-slate-100 text-slate-600 border-slate-200",
      dot: "bg-slate-400",
      icon: HelpCircle,
    },
  };

  const conf = configs[norm] || configs.GREY;
  const sizeClass = size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2 py-0.5 text-xs";

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${conf.bg} ${sizeClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${conf.dot}`} />
      {conf.label}
    </span>
  );
}
