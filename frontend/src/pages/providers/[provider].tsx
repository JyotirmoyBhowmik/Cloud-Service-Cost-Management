import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import {
  Cloud,
  CheckCircle,
  RefreshCw,
  Layers,
  DollarSign,
  ArrowRight,
  Clock,
  Shield,
  Server
} from "lucide-react";
import { api } from "../../utils/api";
import PricingStatusBadge from "../../components/PricingStatusBadge";

export default function ProviderCockpit() {
  const router = useRouter();
  const { provider } = router.query;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const provStr = typeof provider === "string" ? provider.toUpperCase() : "AZURE";

  const loadProvider = () => {
    if (!provider) return;
    setLoading(true);
    api.getProviderOverview(provStr)
      .then((res) => setData(res))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProvider();
  }, [provider]);

  const handleSync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
      loadProvider();
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              Provider Cockpit
            </span>
            <span className="text-xs text-slate-400">FOCUS 1.4 Normalized Feed</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">
            {provStr === "AZURE" ? "Microsoft Azure Commercial Estate" :
             provStr === "AWS" ? "Amazon Web Services (AWS) Organization" :
             provStr === "GCP" ? "Google Cloud Platform (GCP) Organization" :
             "Oracle Cloud Infrastructure (OCI) Tenancy"}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Operational and financial posture for {provStr} workloads.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin" : ""}`} /> On-Demand Sync
          </button>
        </div>
      </div>

      {data && (
        <>
          {/* Top KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Total Monthly Spend</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">${data.metrics.monthly_spend.toFixed(2)}</div>
              <div className="text-[11px] text-slate-400 mt-1">Invoiced Billed Actuals</div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Allocated Budget</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">${data.metrics.budget_amount.toFixed(0)}</div>
              <div className="text-[11px] text-slate-400 mt-1">{data.metrics.budget_utilization_pct}% Utilized</div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Active Billable Resources</div>
              <div className="text-2xl font-bold text-slate-900 mt-1">{data.metrics.resource_count}</div>
              <div className="text-[11px] text-slate-400 mt-1">Across 4 core services</div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Connector Health</div>
              <div className="text-base font-bold text-emerald-600 mt-1 flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4" /> {data.connector.status}
              </div>
              <div className="text-[11px] text-slate-400 mt-1">Auth: {data.connector.auth_method}</div>
            </div>
          </div>

          {/* Native Hierarchy Lineage Preview */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Native Hierarchy Scopes</h2>
                <p className="text-xs text-slate-500">
                  {provStr === "AZURE" ? "Management Groups &rarr; Subscriptions &rarr; Resource Groups" :
                   provStr === "AWS" ? "Organizations &rarr; Organizational Units &rarr; Accounts" :
                   provStr === "GCP" ? "Organizations &rarr; Folders &rarr; Projects" :
                   "Tenancy &rarr; Compartments &rarr; Subcompartments"}
                </p>
              </div>
              <Link href="/hierarchy" className="text-xs text-blue-600 hover:underline font-semibold flex items-center gap-1">
                Open Full Tree <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
              {data.native_hierarchy_preview.map((node: any) => (
                <div key={node.id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-800 truncate">{node.name}</span>
                    <PricingStatusBadge status={node.pricing_status} size="sm" />
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">{node.native_type}</div>
                  <div className="text-[10px] text-blue-700 font-semibold">{node.role}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
