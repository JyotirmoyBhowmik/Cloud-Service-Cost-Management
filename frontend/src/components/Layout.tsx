import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import {
  LayoutDashboard,
  Cloud,
  Network,
  Layers,
  DollarSign,
  Calculator,
  PieChart,
  GitBranch,
  Bell,
  Sliders,
  ShieldCheck,
  Search,
  CheckCircle,
  HelpCircle,
  ExternalLink,
  ChevronRight,
  Menu,
  X,
  FileSpreadsheet
} from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: "Executive Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Cloud Providers", href: "/providers/azure", icon: Cloud },
    { name: "Hierarchy Explorer", href: "/hierarchy", icon: Network },
    { name: "Service Inventory", href: "/services", icon: Layers },
    { name: "Cost Cockpit", href: "/costs", icon: DollarSign },
    { name: "What-If Calculator", href: "/calculator", icon: Calculator },
    { name: "Budgets & Thresholds", href: "/budgets", icon: PieChart },
    { name: "Dependency Graph", href: "/dependencies", icon: GitBranch },
    { name: "Alerts & Governance", href: "/alerts", icon: Bell },
    { name: "16-Step Onboarding", href: "/onboarding", icon: Sliders },
    { name: "Admin & Audit", href: "/admin", icon: ShieldCheck },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
      {/* Top Enterprise Banner */}
      <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-40 flex items-center justify-between px-4 sm:px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <button 
            className="lg:hidden p-1.5 text-slate-600 hover:bg-slate-100 rounded-md"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-700 via-indigo-600 to-sky-500 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20">
              <Cloud className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 tracking-tight flex items-center gap-1.5">
                CloudScope <span className="text-[10px] bg-blue-50 text-blue-700 border border-blue-200 px-1.5 py-0.5 rounded font-semibold uppercase tracking-wider">Enterprise</span>
              </span>
              <span className="text-[11px] text-slate-400 block -mt-1 font-medium">Multi-Cloud Governance & FinOps</span>
            </div>
          </Link>
        </div>

        {/* Search bar & Quick Actions */}
        <div className="hidden md:flex items-center gap-3 flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search resources, SKUs, subscriptions, tags..."
              className="w-full pl-9 pr-4 py-1.5 bg-slate-100/80 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 focus:bg-white transition-all text-slate-700 placeholder-slate-400"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  router.push(`/services?search=${(e.target as HTMLInputElement).value}`);
                }
              }}
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Provider Status Indicator Badges */}
          <div className="hidden xl:flex items-center gap-2 border-r border-slate-200 pr-4">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-50 text-blue-700 border border-blue-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" /> Azure
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" /> AWS
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> GCP
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> OCI
            </span>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center font-bold text-xs text-slate-700">
              FA
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-semibold text-slate-900 leading-tight">FinOps Architect</div>
              <div className="text-[10px] text-slate-400 font-medium">SUPER_ADMIN</div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Navigation */}
        <aside className={`
          fixed inset-y-16 left-0 z-30 w-64 bg-white border-r border-slate-200 transition-transform duration-200 ease-in-out lg:static lg:translate-x-0
          ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full"}
        `}>
          <div className="flex flex-col h-full justify-between p-3.5">
            <nav className="space-y-1">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">Platform Control Plane</div>
              {navigation.map((item) => {
                const isActive = router.pathname === item.href || (item.href !== "/" && router.pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors
                      ${isActive
                        ? "bg-blue-50 text-blue-700 font-semibold border border-blue-200/60 shadow-sm"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"}
                    `}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                    {item.name}
                  </Link>
                );
              })}
            </nav>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-600 font-medium">
                <span className="flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> Demo Mode Active</span>
                <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-mono">v1.0</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">
                Seeded with Azure, AWS, GCP & OCI demo estates. Real APIs active.
              </p>
              <div className="pt-1 flex gap-2">
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-blue-600 hover:underline font-medium"
                >
                  OpenAPI Specs <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-slate-50">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
