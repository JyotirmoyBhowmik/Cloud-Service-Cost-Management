import React, { useState } from "react";
import {
  Calculator,
  DollarSign,
  Cloud,
  Check,
  Info,
  Clock,
  HardDrive,
  Network,
  RotateCcw,
  Sparkles
} from "lucide-react";
import { api } from "../utils/api";

export default function WhatIfCalculator() {
  const [provider, setProvider] = useState("AZURE");
  const [serviceCode, setServiceCode] = useState("Virtual Machines");
  const [region, setRegion] = useState("eastus");
  const [quantity, setQuantity] = useState(2);
  const [runtimeHoursPerDay, setRuntimeHoursPerDay] = useState(24);
  const [daysPerMonth, setDaysPerMonth] = useState(30);
  const [storageGb, setStorageGb] = useState(128);
  const [networkEgressGb, setNetworkEgressGb] = useState(50);

  const [result, setResult] = useState<any>(null);
  const [calculating, setCalculating] = useState(false);

  const handleSimulate = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setCalculating(true);
    api.simulateWhatIf({
      provider,
      service_code: serviceCode,
      region,
      quantity,
      runtime_hours_per_day: runtimeHoursPerDay,
      days_per_month: daysPerMonth,
      storage_gb: storageGb,
      network_egress_gb: networkEgressGb,
    })
      .then((data) => setResult(data))
      .catch(console.error)
      .finally(() => setCalculating(false));
  };

  React.useEffect(() => {
    handleSimulate();
  }, [provider, serviceCode, region, quantity, runtimeHoursPerDay, daysPerMonth, storageGb, networkEgressGb]);

  const serviceOptions: Record<string, string[]> = {
    AZURE: ["Virtual Machines", "SQL Database", "Storage Accounts", "Application Gateway"],
    AWS: ["AmazonEC2", "AmazonRDS", "AmazonS3", "AWSELB"],
    GCP: ["Compute Engine", "Cloud SQL", "Cloud Storage", "Cloud Load Balancing"],
    OCI: ["Compute", "Autonomous Database", "Object Storage", "Virtual Cloud Network"],
  };

  const regionOptions: Record<string, string[]> = {
    AZURE: ["eastus", "westeurope", "southeastasia"],
    AWS: ["us-east-1", "eu-west-1", "ap-southeast-1"],
    GCP: ["us-central1", "europe-west1", "asia-east1"],
    OCI: ["us-ashburn-1", "eu-frankfurt-1", "ap-tokyo-1"],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Calculator className="w-6 h-6 text-blue-600" /> "What Will This Cost?" Simulation Engine
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Simulate workload expenses across Azure, AWS, GCP, and OCI before deploying infrastructure per User Request §53 & §54.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Form: Configuration parameters */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-ceramic space-y-5">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider pb-3 border-b border-slate-100">
            Workload Configuration
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Target Cloud</label>
              <select
                value={provider}
                onChange={(e) => {
                  const p = e.target.value;
                  setProvider(p);
                  setServiceCode(serviceOptions[p][0]);
                  setRegion(regionOptions[p][0]);
                }}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2 text-xs font-semibold text-slate-800"
              >
                <option value="AZURE">Microsoft Azure</option>
                <option value="AWS">Amazon Web Services</option>
                <option value="GCP">Google Cloud Platform</option>
                <option value="OCI">Oracle Cloud Infrastructure</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Service Family</label>
              <select
                value={serviceCode}
                onChange={(e) => setServiceCode(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2 text-xs font-semibold text-slate-800"
              >
                {(serviceOptions[provider] || []).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Deployment Region</label>
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2 text-xs font-semibold text-slate-800"
              >
                {(regionOptions[provider] || []).map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">Instance Quantity ({quantity})</label>
              <input
                type="range"
                min="1"
                max="50"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer mt-2"
              />
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 space-y-4 text-xs">
            <h3 className="font-bold text-slate-800">Operational Runtime & Schedules</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">
                  Operating Hours Per Day: <span className="text-slate-800 font-bold">{runtimeHoursPerDay}h</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="24"
                  value={runtimeHoursPerDay}
                  onChange={(e) => setRuntimeHoursPerDay(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">
                  Operating Days Per Month: <span className="text-slate-800 font-bold">{daysPerMonth} days</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="31"
                  value={daysPerMonth}
                  onChange={(e) => setDaysPerMonth(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 space-y-4 text-xs">
            <h3 className="font-bold text-slate-800">Storage & Network Volume Projections</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">
                  Attached Storage: <span className="text-slate-800 font-bold">{storageGb} GB</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="2000"
                  step="50"
                  value={storageGb}
                  onChange={(e) => setStorageGb(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">
                  Network Egress / Internet Out: <span className="text-slate-800 font-bold">{networkEgressGb} GB</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1000"
                  step="25"
                  value={networkEgressGb}
                  onChange={(e) => setNetworkEgressGb(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Pane: Simulated Cost Output & Formulas */}
        <div className="lg:col-span-5 space-y-4">
          {result && (
            <>
              {/* Primary Output Banner */}
              <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-lg space-y-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5"><Sparkles className="w-4 h-4 text-yellow-400" /> Simulated Cost Projection</span>
                  <span className="bg-white/10 px-2 py-0.5 rounded text-[10px] font-mono">{result.provider}</span>
                </div>
                <div>
                  <div className="text-3xl font-extrabold tracking-tight">${result.monthly_cost.toFixed(2)}</div>
                  <div className="text-xs text-slate-400 mt-1">Projected Monthly Total ({result.currency})</div>
                </div>

                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-700/60 text-center">
                  <div className="p-2 bg-white/5 rounded-xl">
                    <div className="text-[10px] text-slate-400">Hourly</div>
                    <div className="text-xs font-bold">${result.hourly_cost.toFixed(4)}</div>
                  </div>
                  <div className="p-2 bg-white/5 rounded-xl">
                    <div className="text-[10px] text-slate-400">Daily</div>
                    <div className="text-xs font-bold">${result.daily_cost.toFixed(2)}</div>
                  </div>
                  <div className="p-2 bg-white/5 rounded-xl">
                    <div className="text-[10px] text-slate-400">Annualized</div>
                    <div className="text-xs font-bold">${result.annual_cost.toFixed(0)}</div>
                  </div>
                </div>
              </div>

              {/* Mathematical Formula Transparency */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-3 text-xs">
                <div className="font-bold text-slate-800 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-blue-600" /> Calculation Formula Trace
                </div>
                <div className="p-3 bg-slate-900 text-slate-100 rounded-xl font-mono text-[11px] leading-relaxed">
                  {result.formula_explanation}
                </div>
              </div>

              {/* Model Assumptions */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-ceramic space-y-2 text-xs">
                <div className="font-bold text-slate-800 flex items-center gap-1.5 text-emerald-700">
                  <Check className="w-4 h-4" /> Simulation Assumptions
                </div>
                <ul className="space-y-1.5 text-slate-600 text-[11px]">
                  {result.assumptions.map((a: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 font-bold">&bull;</span> {a}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
