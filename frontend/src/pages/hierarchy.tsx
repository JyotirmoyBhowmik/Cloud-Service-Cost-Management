import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Network,
  ChevronDown,
  ChevronRight,
  Folder,
  Layers,
  Server,
  DollarSign,
  Cloud,
  Tag,
  CheckCircle,
  Info,
  Shield,
  Search
} from "lucide-react";
import { api } from "../utils/api";
import PricingStatusBadge from "../components/PricingStatusBadge";
import ThresholdBadge from "../components/ThresholdBadge";
import CostExplanationModal from "../components/CostExplanationModal";

interface TreeNodeProps {
  node: any;
  level?: number;
  onSelectNode: (node: any) => void;
  selectedId: string | null;
  onExplainCost: (id: string) => void;
}

function TreeNode({ node, level = 0, onSelectNode, selectedId, onExplainCost }: TreeNodeProps) {
  const [expanded, setExpanded] = useState(level < 2);
  const hasChildren = node.children && node.children.length > 0;
  const isSelected = selectedId === node.id;

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "GOVERNANCE_ROOT":
        return <Cloud className="w-4 h-4 text-purple-600" />;
      case "GOVERNANCE_GROUP":
        return <Folder className="w-4 h-4 text-blue-600" />;
      case "BILLING_CONTEXT":
        return <DollarSign className="w-4 h-4 text-emerald-600" />;
      case "RESOURCE_CONTAINER":
        return <Layers className="w-4 h-4 text-indigo-600" />;
      default:
        return <Server className="w-4 h-4 text-slate-600" />;
    }
  };

  return (
    <div className="select-none">
      <div
        className={`
          flex items-center justify-between py-2 px-3 rounded-xl cursor-pointer transition-colors text-xs
          ${isSelected ? "bg-blue-50 border border-blue-200 text-blue-900 font-semibold" : "hover:bg-slate-100 text-slate-700"}
        `}
        style={{ paddingLeft: `${Math.max(12, level * 20)}px` }}
        onClick={() => onSelectNode(node)}
      >
        <div className="flex items-center gap-2 min-w-0">
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              className="p-0.5 hover:bg-slate-200 rounded text-slate-400"
            >
              {expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </button>
          ) : (
            <span className="w-3.5" />
          )}

          <div className="shrink-0">{getRoleIcon(node.canonical_role)}</div>

          <span className="truncate font-medium">{node.name}</span>

          <span className="text-[10px] bg-slate-100 text-slate-500 border border-slate-200 px-1.5 py-0.2 rounded font-mono uppercase">
            {node.native_type}
          </span>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {node.canonical_role === "RESOURCE" && (
            <>
              <PricingStatusBadge status={node.pricing_status} size="sm" />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onExplainCost(node.id);
                }}
                className="text-slate-400 hover:text-blue-600 p-0.5"
                title="Explain Cost (ⓘ)"
              >
                <Info className="w-3.5 h-3.5" />
              </button>
            </>
          )}

          <span className="font-bold text-slate-900 w-20 text-right">
            ${node.monthly_cost.toFixed(2)}
          </span>
        </div>
      </div>

      {expanded && hasChildren && (
        <div className="space-y-0.5 mt-0.5">
          {node.children.map((child: any) => (
            <TreeNode
              key={child.id}
              node={child}
              level={level + 1}
              onSelectNode={onSelectNode}
              selectedId={selectedId}
              onExplainCost={onExplainCost}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function HierarchyExplorer() {
  const [tree, setTree] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [providerFilter, setProviderFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [explanationId, setExplanationId] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.getHierarchyTree(providerFilter)
      .then((data) => {
        setTree(data);
        if (data.length > 0 && !selectedNode) {
          setSelectedNode(data[0]);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [providerFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Multi-Cloud Hierarchy Explorer</h1>
          <p className="text-xs text-slate-500 mt-1">
            Preserves native cloud trees (Management Groups, OUs, Folders, Compartments) mapped to canonical governance scopes.
          </p>
        </div>

        {/* Provider Filter Tabs */}
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
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Pane: Interactive Hierarchy Tree */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-ceramic space-y-3 min-h-[500px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Cloud Estate Tree Lineage</span>
            <span className="text-xs text-slate-500">{tree.length} Root Lineages</span>
          </div>

          {loading ? (
            <div className="py-20 text-center text-xs text-slate-400">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              Loading multi-cloud hierarchy...
            </div>
          ) : (
            <div className="space-y-1">
              {tree.map((rootNode) => (
                <TreeNode
                  key={rootNode.id}
                  node={rootNode}
                  onSelectNode={setSelectedNode}
                  selectedId={selectedNode?.id}
                  onExplainCost={setExplanationId}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right Pane: Selected Node Inspector */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-ceramic space-y-5 h-fit sticky top-24">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Node Inspector</span>
            {selectedNode && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                selectedNode.provider === "AZURE" ? "bg-blue-50 text-blue-700 border-blue-200" :
                selectedNode.provider === "AWS" ? "bg-amber-50 text-amber-700 border-amber-200" :
                selectedNode.provider === "GCP" ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                "bg-rose-50 text-rose-700 border-rose-200"
              }`}>
                {selectedNode.provider}
              </span>
            )}
          </div>

          {selectedNode ? (
            <div className="space-y-4 text-xs">
              <div>
                <h3 className="text-base font-bold text-slate-900 leading-snug">{selectedNode.name}</h3>
                <div className="text-slate-400 text-[11px] font-mono mt-0.5">{selectedNode.canonical_id}</div>
              </div>

              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div>
                  <div className="text-[10px] text-slate-400">Native Type</div>
                  <div className="font-semibold text-slate-800">{selectedNode.native_type}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400">Canonical Role</div>
                  <div className="font-semibold text-slate-800">{selectedNode.canonical_role}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400">Region</div>
                  <div className="font-semibold text-slate-800">{selectedNode.region || "Global"}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400">Environment</div>
                  <div className="font-semibold text-slate-800 capitalize">{selectedNode.environment}</div>
                </div>
              </div>

              {/* Financial Roll-up Card */}
              <div className="p-4 bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-xl shadow-md space-y-1">
                <div className="text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Total Scope Spend</span>
                  <span className="text-[10px] bg-white/10 px-1.5 py-0.2 rounded font-mono">Monthly Roll-up</span>
                </div>
                <div className="text-2xl font-bold">${selectedNode.monthly_cost.toFixed(2)}</div>
                <p className="text-[10px] text-slate-400">Aggregates direct cost plus all subordinate container children.</p>
              </div>

              {/* Threshold & Pricing Badges */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Threshold State</span>
                  <ThresholdBadge state={selectedNode.threshold_state} size="sm" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Pricing Status</span>
                  <PricingStatusBadge status={selectedNode.pricing_status} size="sm" />
                </div>
              </div>

              {selectedNode.canonical_role === "RESOURCE" && (
                <div className="pt-3 border-t border-slate-100 flex flex-col gap-2">
                  <button
                    onClick={() => setExplanationId(selectedNode.id)}
                    className="w-full py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg font-semibold flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Info className="w-3.5 h-3.5" /> Explain Cost Rationale (ⓘ)
                  </button>
                  <Link
                    href={`/services/${selectedNode.id}`}
                    className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold text-center transition-colors"
                  >
                    Open 360° Resource Detail
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="py-12 text-center text-slate-400 text-xs">
              Select a node from the hierarchy tree to inspect lineage and financial details.
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
