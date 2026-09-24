import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import {
  ArrowLeft,
  Server,
  DollarSign,
  Activity,
  GitBranch,
  Bell,
  Clock,
  Info,
  CheckCircle,
  AlertTriangle,
  Cpu,
  HardDrive,
  Network as NetworkIcon,
  Shield,
  Layers
} from "lucide-react";
import { api } from "../../utils/api";
import PricingStatusBadge from "../../components/PricingStatusBadge";
import ThresholdBadge from "../../components/ThresholdBadge";
import CostExplanationModal from "../../components/CostExplanationModal";

export default function ServiceDetail360() {
  const router = useRouter();
  const { id } = router.query;
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (!id || typeof id !== "string") return;
    setLoading(true);
    api.getResource360(id)
      .then((data) => setDetail(data))
      .catch((err) => setError(err.message || "Failed to load resource 360 view"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="py-24 text-center text-slate-400 text-xs">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading complete 360° resource detail...
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-700 space-y-2">
        <div className="font-bold">Error Loading Resource Detail</div>
        <div>{error || "Resource not found."}</div>
        <Link href="/services" className="text-blue-600 hover:underline font-semibold block pt-2">
          &larr; Return to Service Inventory
        </Link>
      </div>
    );
  }

  const { overview, service, cost, usage, runtime, dependencies, alerts } = detail;

  const tabs = [
    { id: "overview", label: "Overview & Identity", icon: Server },
    { id: "pricing_cost", label: "Pricing & Cost", icon: DollarSign },
    { id: "usage_runtime", label: "Usage & Runtime", icon: Activity },
    { id: "topology", label: "Dependencies", icon: GitBranch },
    { id: "alerts", label: `Alerts (${alerts.length})`, icon: Bell },
  ];

  return (
    <div className="space-y-6">
      {/* Back button & Title Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
        <div className="flex items-center justify-between">
          <Link href="/services" className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1 transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Service Inventory
          </Link>
          <div className="flex items-center gap-2">
            <PricingStatusBadge status={overview.pricing_status} />
            <ThresholdBadge state={overview.threshold_state} />
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-2">
          <div>
            <div className="flex items-center gap-2">
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                overview.provider === "AZURE" ? "bg-blue-50 text-blue-700 border-blue-200" :
                overview.provider === "AWS" ? "bg-amber-50 text-amber-700 border-amber-200" :
                overview.provider === "GCP" ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                "bg-rose-50 text-rose-700 border-rose-200"
              }`}>
                {overview.provider}
              </span>
              <span className="text-xs text-slate-400 font-mono">{overview.native_type}</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">{overview.name}</h1>
            <p className="text-xs text-slate-500 font-mono mt-0.5">{overview.native_id}</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Monthly Spend</div>
              <div className="text-2xl font-bold text-slate-900">${cost.monthly_cost.toFixed(2)}</div>
            </div>
            <button
              onClick={() => setShowExplanation(true)}
              className="px-3.5 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Info className="w-4 h-4" /> Why does it cost this? (ⓘ)
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-t border-slate-100 pt-4 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors shrink-0
                  ${isActive
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-100"}
                `}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Panels */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Hierarchy & Placement</h2>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Cloud Provider</span>
                <span className="font-semibold text-slate-800">{overview.provider}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Deployment Region</span>
                <span className="font-semibold text-slate-800">{overview.region || "Global"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Environment</span>
                <span className="font-semibold text-slate-800 capitalize">{overview.environment}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Owner Identity</span>
                <span className="font-semibold text-slate-800">{overview.owner || "Unassigned"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Business Unit</span>
                <span className="font-semibold text-slate-800">{overview.business_unit || "General Engineering"}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Cost Center</span>
                <span className="font-semibold text-slate-800">{overview.cost_center || "CC-CORE"}</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Service Classification</h2>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Service Name</span>
                <span className="font-semibold text-slate-800">{service.name}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Service Family</span>
                <span className="font-semibold text-slate-800">{service.family}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Pricing Model</span>
                <span className="font-semibold text-slate-800">{service.default_pricing_model}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Free Tier Allowance</span>
                <span className="font-semibold text-slate-800">{service.has_free_tier ? "Eligible" : "Not Applicable"}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Data Source Pipeline</span>
                <span className="font-semibold text-slate-800">{overview.data_source} &bull; Synced 15m ago</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "pricing_cost" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic text-center">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Hourly Rate</div>
              <div className="text-xl font-bold text-slate-900 mt-1">${cost.hourly_cost.toFixed(4)}</div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic text-center">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Daily Cost</div>
              <div className="text-xl font-bold text-slate-900 mt-1">${cost.daily_cost.toFixed(2)}</div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic text-center">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Monthly Run-Rate</div>
              <div className="text-xl font-bold text-slate-900 mt-1">${cost.monthly_cost.toFixed(2)}</div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic text-center">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Annualized Projection</div>
              <div className="text-xl font-bold text-slate-900 mt-1">${cost.annualized_cost.toFixed(2)}</div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Financial Breakdown Rationale</h2>
              <button
                onClick={() => setShowExplanation(true)}
                className="text-xs text-blue-600 hover:underline font-semibold flex items-center gap-1"
              >
                <Info className="w-3.5 h-3.5" /> Open Full Calculation Trace
              </button>
            </div>
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-2">
              <div className="font-semibold text-slate-800">Actual vs Estimated Reconciliation:</div>
              <div className="flex items-center justify-between">
                <span>Invoiced Billed Actuals (FOCUS 1.4):</span>
                <span className="font-bold text-slate-900">${cost.actual_cost.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Calculated Estimated Rate (Usage × Price):</span>
                <span className="font-bold text-slate-700">${cost.estimated_cost.toFixed(2)}</span>
              </div>
              <div className="flex items-center justify-between pt-2 border-t border-slate-200 font-semibold text-blue-700">
                <span>Variance:</span>
                <span>${(cost.actual_cost - cost.estimated_cost).toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "usage_runtime" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-500" /> Runtime Profile & Schedule
            </h2>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Profile Definition</span>
                <span className="font-bold text-slate-800">{runtime.profile}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Liveness State</span>
                <span className="inline-flex items-center gap-1 text-emerald-600 font-semibold">
                  <CheckCircle className="w-3 h-3" /> Running (Active)
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Active Hours Today</span>
                <span className="font-semibold text-slate-800">{runtime.active_hours_today} Hours</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Monthly Operating Hours</span>
                <span className="font-semibold text-slate-800">{runtime.active_hours_monthly} Hours</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Schedule Adherence</span>
                <span className="font-semibold text-slate-800">{runtime.schedule_adherence_pct}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-slate-500" /> Telemetry & Consumption Observations
            </h2>
            <div className="space-y-2">
              {usage.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-400">No telemetry records logged.</div>
              ) : (
                usage.map((u: any, idx: number) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                    <div>
                      <span className="font-semibold text-slate-800">{u.metric}</span>
                      <span className="text-[10px] text-slate-400 block">{new Date(u.time).toLocaleTimeString()}</span>
                    </div>
                    <span className="text-sm font-bold text-slate-900">{u.value} {u.unit}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === "topology" && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Topology & Downstream Relationships</h2>
              <p className="text-xs text-slate-500">Connected services and upstream/downstream dependencies.</p>
            </div>
            <Link href="/dependencies" className="text-xs text-blue-600 hover:underline font-semibold">
              Open Interactive Topology Graph &rarr;
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
            <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-2">
              <h3 className="font-semibold text-slate-800">Outgoing Links (Depends On)</h3>
              {dependencies.outgoing.length === 0 ? (
                <div className="text-slate-400 py-3">No outgoing dependencies declared.</div>
              ) : (
                dependencies.outgoing.map((e: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center justify-between">
                    <span className="font-mono text-[11px] text-slate-700">{e.target_id}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-100 rounded text-slate-600">{e.type}</span>
                  </div>
                ))
              )}
            </div>

            <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-2">
              <h3 className="font-semibold text-slate-800">Incoming Links (Depended Upon By)</h3>
              {dependencies.incoming.length === 0 ? (
                <div className="text-slate-400 py-3">No incoming dependencies connected.</div>
              ) : (
                dependencies.incoming.map((e: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-white border border-slate-200 rounded-lg flex items-center justify-between">
                    <span className="font-mono text-[11px] text-slate-700">{e.source_id}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-100 rounded text-slate-600">{e.type}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === "alerts" && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Associated Governance Alerts</h2>
          {alerts.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400">
              <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              No active alerts or policy violations on this resource.
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((a: any) => (
                <div key={a.id} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{a.title}</span>
                    <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                      a.severity === "CRITICAL" ? "bg-rose-100 text-rose-800" : "bg-amber-100 text-amber-800"
                    }`}>
                      {a.severity}
                    </span>
                  </div>
                  <p className="text-slate-600">{a.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Information Icon Modal */}
      {showExplanation && (
        <CostExplanationModal
          resourceId={typeof id === "string" ? id : null}
          onClose={() => setShowExplanation(false)}
        />
      )}
    </div>
  );
}
