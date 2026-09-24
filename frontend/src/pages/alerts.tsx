import React, { useEffect, useState } from "react";
import {
  Bell,
  AlertTriangle,
  AlertOctagon,
  Info,
  CheckCircle,
  Filter,
  Check,
  Clock,
  UserCheck
} from "lucide-react";
import { api } from "../utils/api";

export default function AlertsGovernance() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  const loadAlerts = () => {
    setLoading(true);
    api.getAlerts(statusFilter, severityFilter)
      .then((data) => setAlerts(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAlerts();
  }, [statusFilter, severityFilter]);

  const handleUpdateStatus = (id: string, newStatus: string) => {
    api.updateAlertStatus(id, newStatus, `Updated to ${newStatus} by FinOps Administrator`)
      .then(() => loadAlerts())
      .catch(console.error);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Bell className="w-6 h-6 text-rose-600" /> Alerts & Governance Center
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Tracks financial budget breaches, runtime schedule drifts, and policy violations through complete lifecycle (Open → Acknowledged → Resolved) per User Request §33.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-3 text-xs">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="p-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-semibold"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">OPEN</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="p-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-semibold"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span className="font-semibold text-slate-700">{alerts.length} Governance Alerts Tracked</span>
          <span>Lifecycle: Created &rarr; Open &rarr; Acknowledged &rarr; Resolved</span>
        </div>

        <div className="divide-y divide-slate-100">
          {loading ? (
            <div className="py-20 text-center text-xs text-slate-400">
              <div className="w-6 h-6 border-2 border-rose-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              Loading governance alerts...
            </div>
          ) : alerts.length === 0 ? (
            <div className="py-16 text-center text-xs text-slate-400">
              <CheckCircle className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              No alerts matching the selected filter criteria.
            </div>
          ) : (
            alerts.map((alert) => (
              <div key={alert.id} className="p-5 hover:bg-slate-50/70 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      alert.severity === "CRITICAL" ? "bg-rose-100 text-rose-800" :
                      alert.severity === "WARNING" ? "bg-amber-100 text-amber-800" :
                      "bg-blue-100 text-blue-800"
                    }`}>
                      {alert.severity}
                    </span>
                    <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono font-medium">
                      {alert.alert_type}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      {new Date(alert.created_at).toLocaleString()}
                    </span>
                  </div>

                  <h3 className="font-bold text-slate-900 text-sm">{alert.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{alert.message}</p>

                  {alert.observed_value !== null && alert.threshold_value !== null && (
                    <div className="text-[11px] text-slate-400 pt-1 flex items-center gap-2">
                      <span>Observed: <strong className="text-slate-700">{alert.observed_value} {alert.unit}</strong></span>
                      <span>&bull;</span>
                      <span>Threshold: <strong className="text-slate-700">{alert.threshold_value} {alert.unit}</strong></span>
                    </div>
                  )}
                </div>

                {/* Lifecycle State Actions */}
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    alert.status === "OPEN" ? "bg-rose-50 text-rose-700 border border-rose-200" :
                    alert.status === "ACKNOWLEDGED" ? "bg-amber-50 text-amber-700 border border-amber-200" :
                    "bg-emerald-50 text-emerald-700 border border-emerald-200"
                  }`}>
                    {alert.status}
                  </span>

                  {alert.status === "OPEN" && (
                    <button
                      onClick={() => handleUpdateStatus(alert.id, "ACKNOWLEDGED")}
                      className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
                    >
                      Acknowledge
                    </button>
                  )}

                  {alert.status !== "RESOLVED" && (
                    <button
                      onClick={() => handleUpdateStatus(alert.id, "RESOLVED")}
                      className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
