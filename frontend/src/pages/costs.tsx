import React, { useEffect, useState } from "react";
import {
  DollarSign,
  TrendingUp,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  FileSpreadsheet,
  PieChart,
  ArrowRight,
  Layers
} from "lucide-react";
import { api } from "../utils/api";

export default function CostCockpit() {
  const [summary, setSummary] = useState<any>(null);
  const [reconciliation, setReconciliation] = useState<any[]>([]);
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [reconciling, setReconciling] = useState(false);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getCostSummary(),
      api.getReconciliation("2026-09"),
      api.getCostForecast(),
    ])
      .then(([sumData, recData, fcData]) => {
        setSummary(sumData);
        setReconciliation(recData);
        setForecast(fcData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunReconciliation = () => {
    setReconciling(true);
    api.triggerReconciliation("2026-09")
      .then(() => loadData())
      .catch(console.error)
      .finally(() => setReconciling(false));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Cost Cockpit & Reconciliation</h1>
          <p className="text-xs text-slate-500 mt-1">
            Reconciles estimated list rates against actual invoiced provider billing aligned with FOCUS 1.4.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleRunReconciliation}
            disabled={reconciling}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reconciling ? "animate-spin" : ""}`} /> Execute Reconciliation
          </button>
          <a
            href="http://localhost:8000/api/v1/reports/costs.csv"
            download
            className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" /> Export Report CSV
          </a>
        </div>
      </div>

      {/* Variance Summary Bar */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
            <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Invoiced Actuals</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">${summary.actual_cost.toFixed(2)}</div>
            <div className="text-[11px] text-slate-500 mt-1">Provider Billing Invoices</div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
            <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Calculated Estimated</div>
            <div className="text-2xl font-bold text-slate-700 mt-1">${summary.estimated_cost.toFixed(2)}</div>
            <div className="text-[11px] text-slate-500 mt-1">Usage × Public Rate Card</div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
            <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Net Variance</div>
            <div className="text-2xl font-bold text-blue-700 mt-1">
              ${(summary.actual_cost - summary.estimated_cost).toFixed(2)}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">Difference between actual and est.</div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic">
            <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Forecast Month-End</div>
            <div className="text-2xl font-bold text-purple-700 mt-1">${summary.forecast_cost.toFixed(2)}</div>
            <div className="text-[11px] text-slate-500 mt-1">Statistical run-rate projection</div>
          </div>
        </div>
      )}

      {/* Reconciliation Table per User Request §8 */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic overflow-hidden space-y-4 p-6">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Cost Reconciliation Analysis (September 2026)</h2>
            <p className="text-xs text-slate-500">Detects variances and classifies driver causes per User Request §8.</p>
          </div>
          <span className="text-xs text-slate-400 font-medium">{reconciliation.length} Resources Evaluated</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold">
                <th className="py-3 px-4">Provider</th>
                <th className="py-3 px-4">Resource Scope</th>
                <th className="py-3 px-4 text-right">Estimated ($)</th>
                <th className="py-3 px-4 text-right">Invoiced Actual ($)</th>
                <th className="py-3 px-4 text-right">Variance ($)</th>
                <th className="py-3 px-4 text-right">Variance %</th>
                <th className="py-3 px-4">Detected Driver</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {reconciliation.map((rec) => (
                <tr key={rec.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                      rec.provider === "AZURE" ? "bg-blue-50 text-blue-700 border-blue-200" :
                      rec.provider === "AWS" ? "bg-amber-50 text-amber-700 border-amber-200" :
                      rec.provider === "GCP" ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                      "bg-rose-50 text-rose-700 border-rose-200"
                    }`}>
                      {rec.provider}
                    </span>
                  </td>

                  <td className="py-3 px-4 font-semibold text-slate-800">
                    {rec.resource_name}
                  </td>

                  <td className="py-3 px-4 text-right text-slate-600">
                    ${rec.estimated_amount.toFixed(2)}
                  </td>

                  <td className="py-3 px-4 text-right font-bold text-slate-900">
                    ${rec.actual_amount.toFixed(2)}
                  </td>

                  <td className="py-3 px-4 text-right font-semibold text-blue-700">
                    {rec.difference >= 0 ? `+$${rec.difference.toFixed(2)}` : `-$${Math.abs(rec.difference).toFixed(2)}`}
                  </td>

                  <td className="py-3 px-4 text-right text-slate-600">
                    {rec.variance_pct}%
                  </td>

                  <td className="py-3 px-4">
                    <span className="text-[11px] font-mono px-2 py-0.5 bg-slate-100 rounded text-slate-700">
                      {rec.driver_type}
                    </span>
                  </td>

                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                      rec.status === "RECONCILED" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                    }`}>
                      <CheckCircle className="w-3 h-3" /> {rec.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6-Month Forecast Horizon */}
      {forecast && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Statistical Cost Forecast (Next 6 Months)</h2>
              <p className="text-xs text-slate-500">Methodology: {forecast.method}</p>
            </div>
            <span className="text-xs text-slate-400 font-medium">92% Baseline Confidence</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {forecast.projections.map((p: any) => (
              <div key={p.period} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-center">
                <div className="text-[11px] font-bold text-slate-600">{p.period}</div>
                <div className="text-base font-bold text-purple-700">${p.projected_cost.toFixed(0)}</div>
                <div className="text-[10px] text-slate-400">
                  ${p.lower_bound.toFixed(0)} - ${p.upper_bound.toFixed(0)}
                </div>
                <div className="text-[10px] text-emerald-600 font-semibold">{p.confidence_pct}% conf</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
