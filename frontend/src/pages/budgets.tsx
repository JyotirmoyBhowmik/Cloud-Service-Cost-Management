import React, { useEffect, useState } from "react";
import {
  PieChart,
  Plus,
  AlertTriangle,
  Sliders,
  DollarSign,
  CheckCircle,
  HelpCircle,
  RefreshCw,
  Percent
} from "lucide-react";
import { api } from "../utils/api";
import ThresholdBadge from "../components/ThresholdBadge";

export default function BudgetsAndThresholds() {
  const [budgets, setBudgets] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // New Budget Form Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBudgetName, setNewBudgetName] = useState("");
  const [newBudgetScope, setNewBudgetScope] = useState("PROVIDER");
  const [newBudgetScopeId, setNewBudgetScopeId] = useState("AZURE");
  const [newBudgetAmount, setNewBudgetAmount] = useState(1000);
  const [newWarningPct, setNewWarningPct] = useState(75);
  const [newCriticalPct, setNewCriticalPct] = useState(100);

  // Interactive Threshold Tester
  const [testValue, setTestValue] = useState(82);
  const [testPreviousState, setTestPreviousState] = useState("GREEN");
  const [evaluatedResult, setEvaluatedResult] = useState<any>(null);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      api.getBudgets(),
      api.getThresholdRules(),
    ])
      .then(([bData, rData]) => {
        setBudgets(bData);
        setRules(rData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTestThreshold = () => {
    api.evaluateThreshold(testValue, testPreviousState)
      .then((res) => setEvaluatedResult(res))
      .catch(console.error);
  };

  useEffect(() => {
    handleTestThreshold();
  }, [testValue, testPreviousState]);

  const handleCreateBudgetSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    api.createBudget({
      name: newBudgetName,
      scope_type: newBudgetScope,
      scope_id: newBudgetScopeId,
      amount: newBudgetAmount,
      currency: "USD",
      period: "MONTHLY",
      warning_threshold_pct: newWarningPct,
      critical_threshold_pct: newCriticalPct,
      forecast_threshold_pct: 110,
    })
      .then(() => {
        setShowCreateModal(false);
        loadData();
      })
      .catch(console.error);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Financial Budgets & Threshold Governance</h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure hierarchical spending controls and multi-band alert thresholds with hysteresis buffering per User Request §25, §26.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" /> Create Scoped Budget
        </button>
      </div>

      {/* Budgets Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Active Scoped Budgets</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {budgets.map((b) => {
            const isCritical = b.utilization_pct >= b.critical_threshold_pct;
            const isWarning = b.utilization_pct >= b.warning_threshold_pct;
            return (
              <div key={b.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-3 hover:shadow-ceramic-hover transition-shadow">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-100 text-slate-700 rounded font-mono">
                    {b.scope_type}: {b.scope_id}
                  </span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    isCritical ? "bg-rose-100 text-rose-800" : isWarning ? "bg-amber-100 text-amber-800" : "bg-emerald-100 text-emerald-800"
                  }`}>
                    {b.utilization_pct}% Utilized
                  </span>
                </div>

                <div>
                  <h3 className="font-bold text-slate-900 text-sm">{b.name}</h3>
                  <div className="flex items-baseline justify-between mt-2">
                    <span className="text-2xl font-extrabold text-slate-900">${b.current_spend.toFixed(2)}</span>
                    <span className="text-xs text-slate-400">Budget: ${b.amount.toFixed(0)}</span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      isCritical ? "bg-rose-500" : isWarning ? "bg-amber-500" : "bg-emerald-500"
                    }`}
                    style={{ width: `${Math.min(100, b.utilization_pct)}%` }}
                  />
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Warn @ {b.warning_threshold_pct}%</span>
                  <span>Crit @ {b.critical_threshold_pct}%</span>
                  <span>Forecast: ${b.forecasted_spend.toFixed(0)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Threshold Policies & Interactive State Evaluator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rules List */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Configured Threshold State Bands</h2>
          <p className="text-xs text-slate-500">Threshold rules governing automatic alert transitions.</p>

          <div className="space-y-3">
            {rules.map((r) => (
              <div key={r.id} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900">{r.name}</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded">Active</span>
                </div>
                <div className="grid grid-cols-4 gap-2 text-center pt-1 font-mono text-[11px]">
                  <div className="p-1.5 bg-emerald-50 text-emerald-800 rounded border border-emerald-200">
                    &lt;{r.green_max}% Green
                  </div>
                  <div className="p-1.5 bg-amber-50 text-amber-800 rounded border border-amber-200">
                    {r.green_max}-{r.amber_max}% Amber
                  </div>
                  <div className="p-1.5 bg-orange-50 text-orange-800 rounded border border-orange-200">
                    {r.amber_max}-{r.red_min}% Orange
                  </div>
                  <div className="p-1.5 bg-rose-50 text-rose-800 rounded border border-rose-200">
                    &gt;{r.red_min}% Red
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1">
                  <span>Metric: <strong>{r.metric_name}</strong></span>
                  <span>Hysteresis Buffer: <strong>{r.hysteresis_buffer}%</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Hysteresis State Machine Simulator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Hysteresis State Simulator</h2>
            <span className="text-xs text-slate-400">Live Machine Evaluation</span>
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                Simulated Metric Value: <span className="text-slate-900 font-bold">{testValue}%</span>
              </label>
              <input
                type="range"
                min="0"
                max="150"
                value={testValue}
                onChange={(e) => setTestValue(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                Previous State (for Hysteresis Buffer)
              </label>
              <select
                value={testPreviousState}
                onChange={(e) => setTestPreviousState(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2 text-xs font-semibold text-slate-800"
              >
                <option value="GREEN">GREEN (Normal)</option>
                <option value="AMBER">AMBER (Warning)</option>
                <option value="ORANGE">ORANGE (Near Limit)</option>
                <option value="RED">RED (Critical)</option>
              </select>
            </div>

            {evaluatedResult && (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Derived Color State</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">{evaluatedResult.state_label}</div>
                </div>
                <div>
                  <ThresholdBadge state={evaluatedResult.evaluated_state} />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Budget Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-modal w-full max-w-md border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Create Scoped Budget</h2>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
            <form onSubmit={handleCreateBudgetSubmit} className="p-6 space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Budget Name</label>
                <input
                  type="text"
                  required
                  value={newBudgetName}
                  onChange={(e) => setNewBudgetName(e.target.value)}
                  placeholder="e.g. Q4 Analytics Cloud Spend"
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Scope Type</label>
                  <select
                    value={newBudgetScope}
                    onChange={(e) => setNewBudgetScope(e.target.value)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
                  >
                    <option value="PROVIDER">PROVIDER</option>
                    <option value="GLOBAL">GLOBAL</option>
                    <option value="SUBSCRIPTION">SUBSCRIPTION</option>
                  </select>
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Scope Target</label>
                  <input
                    type="text"
                    value={newBudgetScopeId}
                    onChange={(e) => setNewBudgetScopeId(e.target.value)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Budget Target ($)</label>
                <input
                  type="number"
                  required
                  min="1"
                  value={newBudgetAmount}
                  onChange={(e) => setNewBudgetAmount(parseFloat(e.target.value))}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Warning % (Amber)</label>
                  <input
                    type="number"
                    value={newWarningPct}
                    onChange={(e) => setNewWarningPct(parseFloat(e.target.value))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Critical % (Red)</label>
                  <input
                    type="number"
                    value={newCriticalPct}
                    onChange={(e) => setNewCriticalPct(parseFloat(e.target.value))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold shadow-sm"
                >
                  Create Budget
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
