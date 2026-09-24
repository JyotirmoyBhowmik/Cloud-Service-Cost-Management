import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
  Layers,
  ArrowUpRight,
  ShieldAlert,
  Cloud,
  CheckCircle,
  FileSpreadsheet,
  AlertTriangle,
  RefreshCw,
  Info
} from "lucide-react";
import { api } from "../utils/api";
import CostExplanationModal from "../components/CostExplanationModal";

export default function ExecutiveDashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [providers, setProviders] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedResourceId, setSelectedResourceId] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getCostSummary(),
      api.getProviders(),
      api.getAlerts("OPEN")
    ])
      .then(([sumData, provData, alertData]) => {
        setSummary(sumData);
        setProviders(provData);
        setAlerts(alertData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-ceramic">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Cloud Cockpit</h1>
          <p className="text-xs text-slate-500 mt-1">
            Global multi-cloud spend, budget utilization, and threshold governance across Azure, AWS, GCP, and OCI.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={loadData}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh Data
          </button>
          <a
            href="http://localhost:8000/api/v1/reports/costs.csv"
            download
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm shadow-blue-500/20 transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" /> Export FOCUS CSV
          </a>
        </div>
      </div>

      {/* Primary KPI Horizon Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
              <span>Total Cloud Spend</span>
              <span className="p-1 rounded bg-blue-50 text-blue-700"><DollarSign className="w-3.5 h-3.5" /></span>
            </div>
            <div className="text-2xl font-bold text-slate-900">
              ${summary.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-[11px] text-slate-400 flex items-center gap-1">
              <span className="text-emerald-600 font-semibold flex items-center"><TrendingUp className="w-3 h-3" /> +2.4%</span> vs last cycle
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
              <span>Billed Actuals</span>
              <span className="text-[10px] bg-slate-100 text-slate-700 font-mono px-1.5 py-0.5 rounded">FOCUS 1.4</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">
              ${summary.actual_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-[11px] text-slate-400">
              Provider Invoiced Feed
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
              <span>Estimated Rate</span>
              <span className="text-[10px] bg-indigo-50 text-indigo-700 font-mono px-1.5 py-0.5 rounded">Catalog</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">
              ${summary.estimated_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-[11px] text-slate-400">
              Pre-bill usage × list rate
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
              <span>Projected Forecast</span>
              <span className="text-[10px] bg-purple-50 text-purple-700 font-mono px-1.5 py-0.5 rounded">Run-Rate</span>
            </div>
            <div className="text-2xl font-bold text-purple-700">
              ${summary.forecast_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-[11px] text-slate-400">
              Month-end estimate
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
              <span>Budget Utilization</span>
              <span className="text-[10px] bg-emerald-50 text-emerald-700 font-mono px-1.5 py-0.5 rounded">{summary.budget_utilization_pct}%</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">
              ${summary.budget_amount.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full ${summary.budget_utilization_pct > 90 ? "bg-rose-500" : summary.budget_utilization_pct > 75 ? "bg-amber-500" : "bg-emerald-500"}`}
                style={{ width: `${Math.min(100, summary.budget_utilization_pct)}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Multi-Cloud Provider Estates Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Cloud Provider Estates</h2>
          <span className="text-xs text-slate-400 font-medium">4 of 4 Connected & Synced</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {providers.map((p) => {
            const colors: Record<string, { bg: string; text: string; border: string }> = {
              AZURE: { bg: "bg-blue-50/50", text: "text-blue-700", border: "border-blue-200" },
              AWS: { bg: "bg-amber-50/50", text: "text-amber-700", border: "border-amber-200" },
              GCP: { bg: "bg-emerald-50/50", text: "text-emerald-700", border: "border-emerald-200" },
              OCI: { bg: "bg-rose-50/50", text: "text-rose-700", border: "border-rose-200" },
            };
            const theme = colors[p.provider] || colors.AZURE;

            return (
              <div key={p.provider} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-ceramic flex flex-col justify-between hover:shadow-ceramic-hover transition-shadow">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-md border ${theme.bg} ${theme.text} ${theme.border}`}>
                      {p.provider}
                    </span>
                    <span className="inline-flex items-center gap-1 text-[11px] text-emerald-600 font-medium">
                      <CheckCircle className="w-3.5 h-3.5" /> Healthy
                    </span>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">{p.display_name}</h3>
                    <p className="text-xs text-slate-400">{p.resource_count} billable resources &bull; {p.service_count} services</p>
                  </div>
                  <div className="pt-2 border-t border-slate-100 flex items-baseline justify-between">
                    <div>
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider">Monthly Spend</div>
                      <div className="text-lg font-bold text-slate-900">${p.monthly_spend.toFixed(2)}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider">Utilization</div>
                      <div className="text-xs font-semibold text-slate-700">{p.budget_utilization_pct}% of ${p.budget_amount.toFixed(0)}</div>
                    </div>
                  </div>
                </div>
                <div className="pt-4 mt-2">
                  <Link
                    href={`/providers/${p.provider.toLowerCase()}`}
                    className="w-full py-1.5 px-3 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold flex items-center justify-center gap-1 transition-colors"
                  >
                    Provider Cockpit <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Two Column Section: Top Cost Drivers & Active Governance Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Cost Drivers */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-ceramic space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Top Financial Cost Drivers</h2>
              <p className="text-xs text-slate-500">Resources generating highest consumption in the current period.</p>
            </div>
            <Link href="/services" className="text-xs text-blue-600 hover:underline font-semibold flex items-center gap-1">
              View All Resources <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {summary && summary.top_cost_drivers && summary.top_cost_drivers.map((driver: any, idx: number) => (
              <div key={idx} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between hover:bg-slate-100/70 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-800 text-xs">{driver.category}</span>
                    <button
                      onClick={() => setSelectedResourceId("resource-modal")}
                      className="text-slate-400 hover:text-blue-600 p-0.5"
                      title="Explain Cost (ⓘ)"
                    >
                      <Info className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="w-64 bg-slate-200 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-blue-600 h-full rounded-full" style={{ width: `${Math.min(100, driver.percentage * 2)}%` }} />
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-slate-900">${driver.amount.toFixed(2)}</div>
                  <div className="text-[10px] text-slate-400">{driver.percentage}% of total estate</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Governance & Budget Alerts */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-ceramic space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Governance Alerts</h2>
            <Link href="/alerts" className="text-xs text-blue-600 hover:underline font-semibold">
              View All ({alerts.length})
            </Link>
          </div>

          <div className="space-y-3">
            {alerts.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400">
                <CheckCircle className="w-6 h-6 text-emerald-500 mx-auto mb-2" />
                All budgets and thresholds within normal bounds.
              </div>
            ) : (
              alerts.slice(0, 4).map((a) => (
                <div key={a.id} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className={`font-bold text-[10px] px-2 py-0.5 rounded-full ${
                      a.severity === "CRITICAL" ? "bg-rose-100 text-rose-800" : "bg-amber-100 text-amber-800"
                    }`}>
                      {a.severity}
                    </span>
                    <span className="text-[10px] text-slate-400">{new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <div className="text-xs font-semibold text-slate-800 leading-snug">{a.title}</div>
                  <p className="text-[11px] text-slate-500 leading-tight">{a.message}</p>
                </div>
              ))
            )}
          </div>

          <div className="pt-2 border-t border-slate-100">
            <Link
              href="/onboarding"
              className="w-full py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm shadow-blue-500/20 transition-all"
            >
              Launch 16-Step Cloud Onboarding <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Information Icon Modal if triggered */}
      {selectedResourceId && (
        <CostExplanationModal
          resourceId="az-vm-web"
          onClose={() => setSelectedResourceId(null)}
        />
      )}
    </div>
  );
}
