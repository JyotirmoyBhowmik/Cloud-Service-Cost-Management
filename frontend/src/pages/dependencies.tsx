import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  GitBranch,
  ArrowRight,
  Layers,
  Server,
  DollarSign,
  Cloud,
  CheckCircle,
  Info,
  Maximize2,
  RefreshCw
} from "lucide-react";
import { api } from "../utils/api";
import PricingStatusBadge from "../components/PricingStatusBadge";
import ThresholdBadge from "../components/ThresholdBadge";
import CostExplanationModal from "../components/CostExplanationModal";

export default function DependenciesGraph() {
  const [graph, setGraph] = useState<any>(null);
  const [providerFilter, setProviderFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [explanationId, setExplanationId] = useState<string | null>(null);

  const fetchGraph = () => {
    setLoading(true);
    api.getDependencyGraph(providerFilter)
      .then((data) => {
        setGraph(data);
        if (data.nodes.length > 0 && !selectedNode) {
          setSelectedNode(data.nodes[0]);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchGraph();
  }, [providerFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <GitBranch className="w-6 h-6 text-indigo-600" /> Cost-Aware Service Topology & Dependencies
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Visual dependency mapping displaying: <strong>Direct Cost + Dependent Costs = Total Application Cost</strong> per User Request §30, §31, §32.
          </p>
        </div>

        {/* Cloud Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200 text-xs">
          {["ALL", "AZURE", "AWS", "GCP", "OCI"].map((prov) => (
            <button
              key={prov}
              onClick={() => setProviderFilter(prov)}
              className={`
                px-3 py-1.5 rounded-lg font-semibold transition-colors
                ${providerFilter === prov ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"}
              `}
            >
              {prov}
            </button>
          ))}
        </div>
      </div>

      {/* Main Two-Pane View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Interactive Graph Canvas */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-slate-200 shadow-ceramic p-6 space-y-4 min-h-[550px] flex flex-col justify-between">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Service Relationship Map</span>
            <span className="text-xs text-slate-500 font-medium">
              {graph ? `${graph.nodes.length} Services & ${graph.edges.length} Dependency Edges` : "Loading..."}
            </span>
          </div>

          {loading ? (
            <div className="py-24 text-center text-xs text-slate-400">
              <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              Computing multi-cloud topology graphs...
            </div>
          ) : graph ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-3">
              {graph.nodes.map((node: any) => {
                const isSelected = selectedNode?.id === node.id;
                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`
                      p-4 rounded-xl border cursor-pointer transition-all space-y-2
                      ${isSelected
                        ? "bg-indigo-50/70 border-indigo-300 shadow-sm"
                        : "bg-slate-50/50 hover:bg-slate-100/60 border-slate-200"}
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                        node.provider === "AZURE" ? "bg-blue-50 text-blue-700 border-blue-200" :
                        node.provider === "AWS" ? "bg-amber-50 text-amber-700 border-amber-200" :
                        node.provider === "GCP" ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                        "bg-rose-50 text-rose-700 border-rose-200"
                      }`}>
                        {node.provider}
                      </span>
                      <ThresholdBadge state={node.threshold_state} size="sm" />
                    </div>

                    <div>
                      <div className="font-bold text-slate-900 text-xs">{node.name}</div>
                      <div className="text-[11px] text-slate-400">{node.service_name} &bull; {node.environment}</div>
                    </div>

                    {/* Cost Chain Equation */}
                    <div className="pt-2 border-t border-slate-200/60 text-xs flex items-center justify-between">
                      <div>
                        <div className="text-[10px] text-slate-400">Direct Cost</div>
                        <div className="font-semibold text-slate-700">${node.direct_cost.toFixed(2)}</div>
                      </div>
                      <div className="text-slate-400">+</div>
                      <div>
                        <div className="text-[10px] text-slate-400">Dependent</div>
                        <div className="font-semibold text-slate-700">${node.dependent_cost.toFixed(2)}</div>
                      </div>
                      <div className="text-slate-400">=</div>
                      <div className="text-right">
                        <div className="text-[10px] text-indigo-700 font-bold uppercase">Total Cost</div>
                        <div className="font-bold text-indigo-900">${node.total_cost.toFixed(2)}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : null}

          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Dependency relationship types: <strong>DEPENDS_ON, CONNECTS_TO, CONSUMES, BILLS_TO</strong></span>
            <span>Total Topology Spend: <strong>${graph?.total_graph_cost?.toFixed(2) || "0.00"}</strong></span>
          </div>
        </div>

        {/* Right Node Inspector */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-ceramic p-6 space-y-5 h-fit sticky top-24">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Topology Node Detail</span>
            {selectedNode && (
              <PricingStatusBadge status={selectedNode.pricing_status} size="sm" />
            )}
          </div>

          {selectedNode ? (
            <div className="space-y-4 text-xs">
              <div>
                <h3 className="text-base font-bold text-slate-900">{selectedNode.name}</h3>
                <div className="text-slate-400 text-[11px] font-mono mt-0.5">{selectedNode.canonical_id}</div>
              </div>

              {/* Total Application Cost Banner */}
              <div className="bg-gradient-to-br from-indigo-950 to-slate-900 text-white p-5 rounded-2xl shadow-md space-y-2">
                <div className="text-[10px] text-indigo-300 uppercase tracking-wider font-semibold">Total Application Financial Impact</div>
                <div className="text-3xl font-extrabold tracking-tight">${selectedNode.total_cost.toFixed(2)} <span className="text-xs font-normal text-slate-400">/ mo</span></div>
                <div className="pt-2 border-t border-indigo-800/60 grid grid-cols-2 gap-2 text-center text-[11px]">
                  <div className="p-1.5 bg-white/10 rounded-lg">
                    <div className="text-[10px] text-slate-400">Direct Scope</div>
                    <div className="font-bold text-white">${selectedNode.direct_cost.toFixed(2)}</div>
                  </div>
                  <div className="p-1.5 bg-white/10 rounded-lg">
                    <div className="text-[10px] text-slate-400">Downstream Chain</div>
                    <div className="font-bold text-white">${selectedNode.dependent_cost.toFixed(2)}</div>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-slate-600 leading-relaxed text-[11px]">
                <strong className="text-slate-800">FinOps Topology Insight: </strong>
                Modifying, scaling, or migrating this service impacts {selectedNode.dependent_cost > 0 ? `an additional $${selectedNode.dependent_cost.toFixed(2)} in connected downstream infrastructure.` : "only its direct allocated monthly cost."}
              </div>

              <div className="pt-2 flex flex-col gap-2">
                <button
                  onClick={() => setExplanationId(selectedNode.id)}
                  className="w-full py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg font-semibold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Info className="w-3.5 h-3.5" /> Explain Cost Calculation (ⓘ)
                </button>
                <Link
                  href={`/services/${selectedNode.id}`}
                  className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold text-center transition-colors"
                >
                  Open Full 360° Resource Detail
                </Link>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-400 text-xs">
              Select a service from the topology canvas to inspect dependent costs.
            </div>
          )}
        </div>
      </div>

      {/* Explanation Modal */}
      {explanationId && (
        <CostExplanationModal
          resourceId={explanationId}
          onClose={() => setExplanationId(null)}
        />
      )}
    </div>
  );
}
