import React, { useEffect, useState } from "react";
import {
  ShieldCheck,
  Lock,
  Users,
  Sliders,
  FileText,
  AlertCircle,
  CheckCircle,
  Database,
  History
} from "lucide-react";
import { api } from "../utils/api";

export default function AdminConsole() {
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [settings, setSettings] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("audit");
  const [loading, setLoading] = useState(true);

  // Administrative Override Form
  const [overrideEntity, setOverrideEntity] = useState("ResourceNode");
  const [overrideId, setOverrideId] = useState("az-vm-web");
  const [overrideField, setOverrideField] = useState("pricing_status");
  const [overrideValue, setOverrideValue] = useState("CONDITIONAL_FREE");
  const [overrideReason, setOverrideReason] = useState("Approved annual promotional grant by FinOps committee");
  const [overrideSuccess, setOverrideSuccess] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getAuditLogs(),
      api.getRoles(),
      api.getSettings(),
    ])
      .then(([auditData, rolesData, settingsData]) => {
        setAuditLogs(auditData);
        setRoles(rolesData);
        setSettings(settingsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleApplyOverride = (e: React.FormEvent) => {
    e.preventDefault();
    fetch("http://localhost:8000/api/v1/admin/overrides", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        entity_type: overrideEntity,
        entity_id: overrideId,
        field_name: overrideField,
        override_value: overrideValue,
        reason: overrideReason,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setOverrideSuccess(data.message);
        loadData();
      })
      .catch(console.error);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-slate-800" /> Platform Administration & Governance
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Enterprise RBAC role scopes, immutable audit trails, and audited administrative overrides per User Request §34, §35, §36.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => setActiveTab("audit")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              activeTab === "audit" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-700"
            }`}
          >
            Audit Trail
          </button>
          <button
            onClick={() => setActiveTab("rbac")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              activeTab === "rbac" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-700"
            }`}
          >
            9 Enterprise Roles
          </button>
          <button
            onClick={() => setActiveTab("override")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors ${
              activeTab === "override" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-700"
            }`}
          >
            Administrative Override
          </button>
        </div>
      </div>

      {activeTab === "audit" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span className="font-semibold text-slate-700">Immutable Compliance Log (All Write & Override Actions)</span>
            <span className="flex items-center gap-1"><History className="w-3.5 h-3.5" /> Append-Only Datastore</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold">
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">User Identity</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Entity Type</th>
                  <th className="py-3 px-4">Scope Target</th>
                  <th className="py-3 px-4">Rationale / Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {auditLogs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-400">
                      No administrative overrides or security actions recorded.
                    </td>
                  </tr>
                ) : (
                  auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-800">
                        {log.user_email}
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-[10px] font-mono px-2 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded font-semibold">
                          {log.action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-600 font-medium">
                        {log.entity_type}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-700 text-[11px]">
                        {log.entity_id}
                      </td>
                      <td className="py-3 px-4 text-slate-600 italic">
                        "{log.reason || "Standard system configuration"}"
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "rbac" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic p-6 space-y-4">
          <div className="pb-3 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Role-Based Access Control Scopes (RBAC)</h2>
            <p className="text-xs text-slate-500">Fine-grained permissions enforced at the FastAPI service layer per User Request §35.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roles.map((r) => (
              <div key={r.role} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900">{r.role}</span>
                  <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono font-semibold">
                    {r.permissions.length} Perms
                  </span>
                </div>
                <div className="flex flex-wrap gap-1 pt-1">
                  {r.permissions.map((p: string) => (
                    <span key={p} className="text-[10px] bg-white border border-slate-200 text-slate-600 px-1.5 py-0.5 rounded font-mono">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "override" && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-ceramic p-6 space-y-5 max-w-xl mx-auto">
          <div>
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Apply Administrative Override</h2>
            <p className="text-xs text-slate-500">All overrides are strictly logged to the immutable compliance trail.</p>
          </div>

          {overrideSuccess && (
            <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-600" /> {overrideSuccess}
            </div>
          )}

          <form onSubmit={handleApplyOverride} className="space-y-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Entity Type</label>
              <select
                value={overrideEntity}
                onChange={(e) => setOverrideEntity(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
              >
                <option value="ResourceNode">ResourceNode</option>
                <option value="Budget">Budget</option>
                <option value="ThresholdRule">ThresholdRule</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Target Entity Identifier</label>
              <input
                type="text"
                required
                value={overrideId}
                onChange={(e) => setOverrideId(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-mono text-xs"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Field to Override</label>
              <input
                type="text"
                required
                value={overrideField}
                onChange={(e) => setOverrideField(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg font-mono text-xs"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">New Value</label>
              <input
                type="text"
                required
                value={overrideValue}
                onChange={(e) => setOverrideValue(e.target.value)}
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-xs"
              />
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Mandatory Business Rationale</label>
              <textarea
                required
                rows={3}
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="Explain the operational rationale for this override..."
                className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-xs"
              />
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-semibold shadow-sm transition-colors"
              >
                Commit Override & Audit Event
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
