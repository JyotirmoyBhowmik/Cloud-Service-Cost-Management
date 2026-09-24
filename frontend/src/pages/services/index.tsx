import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Layers,
  Search,
  Filter,
  ArrowUpDown,
  Info,
  ArrowUpRight,
  RefreshCw,
  FileSpreadsheet,
  CheckCircle2,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { api } from "../../utils/api";
import PricingStatusBadge from "../../components/PricingStatusBadge";
import ThresholdBadge from "../../components/ThresholdBadge";
import CostExplanationModal from "../../components/CostExplanationModal";

export default function ServiceInventory() {
  const [resources, setResources] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [provider, setProvider] = useState("ALL");
  const [pricingStatus, setPricingStatus] = useState("ALL");
  const [thresholdState, setThresholdState] = useState("ALL");
  const [environment, setEnvironment] = useState("ALL");
  const [sortBy, setSortBy] = useState("name");
  const [sortDesc, setSortDesc] = useState(false);

  // Explanation Modal
  const [explanationId, setExplanationId] = useState<string | null>(null);

  const fetchResources = () => {
    setLoading(true);
    api.getResources({
      page,
      page_size: pageSize,
      search,
      provider,
      pricing_status: pricingStatus,
      threshold_state: thresholdState,
      environment,
      sort_by: sortBy,
    })
      .then((res) => {
        setResources(res.items);
        setTotalCount(res.total_count);
        setTotalPages(res.total_pages);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchResources();
  }, [page, provider, pricingStatus, thresholdState, environment, sortBy, sortDesc]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchResources();
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Multi-Cloud Service Inventory</h1>
          <p className="text-xs text-slate-500 mt-1">
            Searchable, filterable catalog of all active resources across Azure, AWS, GCP, and OCI with pricing intelligence.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="http://localhost:8000/api/v1/reports/costs.csv"
            download
            className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" /> Export Inventory CSV
          </a>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-ceramic space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by resource name, native ID, owner, business unit, region..."
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 focus:bg-white text-slate-800 placeholder-slate-400 transition-all"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold transition-colors"
          >
            Apply Search
          </button>
        </form>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-100 text-xs">
          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Provider</label>
            <select
              value={provider}
              onChange={(e) => { setProvider(e.target.value); setPage(1); }}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none"
            >
              <option value="ALL">All Clouds</option>
              <option value="AZURE">Microsoft Azure</option>
              <option value="AWS">Amazon Web Services</option>
              <option value="GCP">Google Cloud Platform</option>
              <option value="OCI">Oracle Cloud Infrastructure</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Pricing Status</label>
            <select
              value={pricingStatus}
              onChange={(e) => { setPricingStatus(e.target.value); setPage(1); }}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="PAID">Paid / Chargeable</option>
              <option value="FREE_TIER">Free Tier</option>
              <option value="CONDITIONAL_FREE">Conditional Free</option>
              <option value="FREE">Free</option>
              <option value="ESTIMATED">Estimated</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Threshold State</label>
            <select
              value={thresholdState}
              onChange={(e) => { setThresholdState(e.target.value); setPage(1); }}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none"
            >
              <option value="ALL">All States</option>
              <option value="GREEN">Green (Normal)</option>
              <option value="AMBER">Amber (Warning)</option>
              <option value="ORANGE">Orange (Near Limit)</option>
              <option value="RED">Red (Critical)</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Environment</label>
            <select
              value={environment}
              onChange={(e) => { setEnvironment(e.target.value); setPage(1); }}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg p-1.5 text-xs text-slate-700 focus:outline-none"
            >
              <option value="ALL">All Environments</option>
              <option value="production">Production</option>
              <option value="staging">Staging</option>
              <option value="development">Development</option>
            </select>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold">
                <th className="py-3 px-4">Provider</th>
                <th className="py-3 px-4">Resource Name</th>
                <th className="py-3 px-4">Service</th>
                <th className="py-3 px-4">Region</th>
                <th className="py-3 px-4">Environment</th>
                <th className="py-3 px-4">Pricing Status</th>
                <th className="py-3 px-4">Threshold</th>
                <th className="py-3 px-4 text-right">Monthly Spend</th>
                <th className="py-3 px-4 text-center">Cost Info (ⓘ)</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                    Querying multi-cloud inventory records...
                  </td>
                </tr>
              ) : resources.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    No resources matching active search and filters.
                  </td>
                </tr>
              ) : (
                resources.map((item) => {
                  const monthly = item.cost_snapshot?.monthly_cost || 0.0;
                  return (
                    <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-4">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          item.provider === "AZURE" ? "bg-blue-50 text-blue-700 border-blue-200" :
                          item.provider === "AWS" ? "bg-amber-50 text-amber-700 border-amber-200" :
                          item.provider === "GCP" ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
                          "bg-rose-50 text-rose-700 border-rose-200"
                        }`}>
                          {item.provider}
                        </span>
                      </td>

                      <td className="py-3 px-4 font-semibold text-slate-900">
                        <Link href={`/services/${item.id}`} className="hover:text-blue-600 hover:underline">
                          {item.name}
                        </Link>
                        <span className="text-[10px] text-slate-400 block font-mono font-normal">
                          {item.native_type}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-slate-600">
                        {item.service_id ? item.native_type : "Core Resource"}
                      </td>

                      <td className="py-3 px-4 text-slate-500">
                        {item.region || "Global"}
                      </td>

                      <td className="py-3 px-4">
                        <span className="capitalize px-1.5 py-0.5 bg-slate-100 rounded text-[11px] text-slate-700">
                          {item.environment}
                        </span>
                      </td>

                      <td className="py-3 px-4">
                        <PricingStatusBadge status={item.pricing_status} size="sm" />
                      </td>

                      <td className="py-3 px-4">
                        <ThresholdBadge state={item.threshold_state} size="sm" />
                      </td>

                      <td className="py-3 px-4 text-right font-bold text-slate-900">
                        ${monthly.toFixed(2)}
                      </td>

                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => setExplanationId(item.id)}
                          className="p-1 rounded-full text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                          title="Why does this service cost this amount? (ⓘ)"
                        >
                          <Info className="w-4 h-4" />
                        </button>
                      </td>

                      <td className="py-3 px-4 text-right">
                        <Link
                          href={`/services/${item.id}`}
                          className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] font-semibold inline-flex items-center gap-1 transition-colors"
                        >
                          360° View <ArrowUpRight className="w-3 h-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <div>
            Showing <span className="font-semibold text-slate-800">{resources.length}</span> of{" "}
            <span className="font-semibold text-slate-800">{totalCount}</span> items
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
              className="px-2 py-1 bg-white border border-slate-200 rounded text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span>Page {page} of {totalPages}</span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page >= totalPages}
              className="px-2 py-1 bg-white border border-slate-200 rounded text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Information Icon Modal */}
      {explanationId && (
        <CostExplanationModal
          resourceId={explanationId}
          onClose={() => setExplanationId(null)}
        />
      )}
    </div>
  );
}
