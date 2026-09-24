import React, { useEffect, useState } from "react";
import { X, HelpCircle, Info, Calculator, Check, AlertCircle, Shield, FileText, ArrowRight } from "lucide-react";
import { api } from "../utils/api";
import PricingStatusBadge from "./PricingStatusBadge";

interface CostExplanationModalProps {
  resourceId: string | null;
  onClose: () => void;
}

export default function CostExplanationModal({ resourceId, onClose }: CostExplanationModalProps) {
  const [data, setData] = useState<any>(null);
  const [breakdown, setBreakdown] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!resourceId) return;
    setLoading(true);
    setError(null);

    Promise.all([
      api.getResourceExplanation(resourceId),
      api.getResourceCostBreakdown(resourceId)
    ])
      .then(([expData, bData]) => {
        setData(expData);
        setBreakdown(bData);
      })
      .catch((err) => {
        setError(err.message || "Failed to load pricing explanation");
      })
      .finally(() => setLoading(false));
  }, [resourceId]);

  if (!resourceId) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-modal w-full max-w-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
              <Info className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900 leading-tight">Cost & Pricing Intelligence</h2>
              <p className="text-xs text-slate-500 font-medium">Why does this service cost this amount?</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          {loading && (
            <div className="py-12 text-center text-slate-500 text-sm">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              Retrieving live catalog rates and calculation trace...
            </div>
          )}

          {error && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700">
              {error}
            </div>
          )}

          {data && (
            <>
              {/* Identity & Status Card */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{data.provider} &bull; {data.service_family}</div>
                  <div className="text-base font-bold text-slate-900">{data.resource_name}</div>
                  <div className="text-xs text-slate-500">{data.service_name} &bull; SKU: <span className="font-mono text-slate-700">{data.provider_sku_id || "N/A"}</span></div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400 mb-1">Pricing Status</div>
                  <PricingStatusBadge status={data.pricing_status} />
                </div>
              </div>

              {/* Status Explanation Banner */}
              <div className="p-3.5 bg-blue-50/70 border border-blue-200/80 rounded-xl text-xs text-blue-900 leading-relaxed flex items-start gap-2.5">
                <HelpCircle className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">Classification Rationale: </span>
                  {data.status_reason}
                </div>
              </div>

              {/* Mathematical Formula Card */}
              <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                    <Calculator className="w-4 h-4 text-indigo-600" /> Transparent Calculation Formula
                  </span>
                  <span className="text-base font-bold text-slate-900">
                    ${data.monthly_cost.toFixed(2)} <span className="text-xs font-normal text-slate-500">/ mo</span>
                  </span>
                </div>
                <div className="p-3 bg-slate-900 text-slate-100 rounded-lg font-mono text-xs overflow-x-auto">
                  {data.calculation_formula}
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-center">
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400">Unit Price</div>
                    <div className="text-xs font-semibold text-slate-800">${data.unit_price.toFixed(4)}</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400">Billing Unit</div>
                    <div className="text-xs font-semibold text-slate-800">{data.billing_unit}</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400">Usage Quantity</div>
                    <div className="text-xs font-semibold text-slate-800">{data.usage_quantity} {data.usage_unit}</div>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[10px] text-slate-400">Region</div>
                    <div className="text-xs font-semibold text-slate-800">{data.region || "Global"}</div>
                  </div>
                </div>
              </div>

              {/* Dimensional Decomposition Breakdown */}
              {breakdown && breakdown.breakdown && (
                <div className="space-y-2">
                  <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Multi-Dimensional Cost Breakdown</h3>
                  <div className="space-y-1.5">
                    {breakdown.breakdown.map((item: any) => (
                      <div key={item.dimension} className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between text-xs">
                        <div>
                          <span className="font-semibold text-slate-800">{item.dimension}</span>
                          <span className="text-[11px] text-slate-400 block">{item.reason}</span>
                        </div>
                        <div className="text-right">
                          <span className="font-bold text-slate-900">${item.amount.toFixed(2)}</span>
                          <span className="text-[10px] text-slate-400 block">{item.percentage}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Assumptions & Boundaries */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="border border-slate-200 rounded-xl p-3.5 space-y-2 bg-slate-50/50">
                  <div className="font-semibold text-slate-800 flex items-center gap-1.5 text-emerald-700">
                    <Check className="w-3.5 h-3.5" /> Included Assumptions
                  </div>
                  <ul className="space-y-1 text-slate-600 text-[11px]">
                    {data.assumptions_included.map((a: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-emerald-500 font-bold">&bull;</span> {a}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="border border-slate-200 rounded-xl p-3.5 space-y-2 bg-slate-50/50">
                  <div className="font-semibold text-slate-800 flex items-center gap-1.5 text-slate-600">
                    <AlertCircle className="w-3.5 h-3.5 text-slate-400" /> Excluded Assumptions
                  </div>
                  <ul className="space-y-1 text-slate-600 text-[11px]">
                    {data.assumptions_excluded.map((a: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-slate-400 font-bold">&bull;</span> {a}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Source Lineage Footer */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>Pricing Catalog Source: <strong className="text-slate-600">{data.pricing_source}</strong></span>
                <span>Retrieved: {new Date(data.retrieval_timestamp).toLocaleTimeString()}</span>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition-colors shadow-sm"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}
