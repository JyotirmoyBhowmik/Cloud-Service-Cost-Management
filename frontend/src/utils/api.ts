/**
 * CloudScope Frontend API Client
 * Connects React UI to FastAPI backend with strict error handling and tracing.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchJson<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: response.statusText };
    }
    throw new Error(errorData.message || `API Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Providers
  getProviders: () => fetchJson<any[]>("/providers"),
  getProviderOverview: (provider: string) => fetchJson<any>(`/providers/${provider}/overview`),

  // Hierarchy
  getHierarchyTree: (provider?: string) => 
    fetchJson<any[]>(`/hierarchy/tree${provider ? `?provider=${provider}` : ''}`),
  getHierarchySummary: () => fetchJson<any>("/hierarchy/summary"),

  // Services
  getServices: (provider?: string, family?: string) => {
    const params = new URLSearchParams();
    if (provider) params.append("provider", provider);
    if (family) params.append("family", family);
    return fetchJson<any[]>(`/services?${params.toString()}`);
  },

  // Resources
  getResources: (params: {
    page?: number;
    page_size?: number;
    search?: string;
    provider?: string;
    pricing_status?: string;
    threshold_state?: string;
    environment?: string;
    sort_by?: string;
  }) => {
    const query = new URLSearchParams();
    if (params.page) query.append("page", params.page.toString());
    if (params.page_size) query.append("page_size", params.page_size.toString());
    if (params.search) query.append("search", params.search);
    if (params.provider && params.provider !== "ALL") query.append("provider", params.provider);
    if (params.pricing_status && params.pricing_status !== "ALL") query.append("pricing_status", params.pricing_status);
    if (params.threshold_state && params.threshold_state !== "ALL") query.append("threshold_state", params.threshold_state);
    if (params.environment && params.environment !== "ALL") query.append("environment", params.environment);
    if (params.sort_by) query.append("sort_by", params.sort_by);
    return fetchJson<any>(`/resources?${query.toString()}`);
  },
  getResource360: (id: string) => fetchJson<any>(`/resources/${id}`),
  getResourceExplanation: (id: string) => fetchJson<any>(`/resources/${id}/explanation`),
  getResourceCostBreakdown: (id: string) => fetchJson<any>(`/resources/${id}/cost-breakdown`),

  // Pricing & What-If Simulator
  getPricingSkus: (provider?: string) => 
    fetchJson<any[]>(`/pricing/skus${provider ? `?provider=${provider}` : ''}`),
  simulateWhatIf: (payload: any) => 
    fetchJson<any>("/pricing/what-if", { method: "POST", body: JSON.stringify(payload) }),

  // Costs & Reconciliation
  getCostSummary: () => fetchJson<any>("/costs/summary"),
  getReconciliation: (period: string = "2026-09") => 
    fetchJson<any[]>(`/costs/reconciliation?period=${period}`),
  triggerReconciliation: (period: string = "2026-09") => 
    fetchJson<any>(`/costs/reconciliation/run?period=${period}`, { method: "POST" }),
  getCostForecast: () => fetchJson<any>("/costs/forecast"),

  // Budgets
  getBudgets: () => fetchJson<any[]>("/budgets"),
  createBudget: (payload: any) => 
    fetchJson<any>("/budgets", { method: "POST", body: JSON.stringify(payload) }),
  updateBudget: (id: string, payload: any) => 
    fetchJson<any>(`/budgets/${id}`, { method: "PUT", body: JSON.stringify(payload) }),

  // Thresholds
  getThresholdRules: () => fetchJson<any[]>("/thresholds/rules"),
  evaluateThreshold: (value: number, previousState: string = "GREEN") => 
    fetchJson<any>(`/thresholds/evaluate?value=${value}&previous_state=${previousState}`),

  // Dependencies
  getDependencyGraph: (provider?: string) => 
    fetchJson<any>(`/dependencies/graph${provider ? `?provider=${provider}` : ''}`),

  // Alerts
  getAlerts: (status?: string, severity?: string) => {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    if (severity) params.append("severity", severity);
    return fetchJson<any[]>(`/alerts?${params.toString()}`);
  },
  updateAlertStatus: (id: string, status: string, notes?: string) => 
    fetchJson<any>(`/alerts/${id}/status`, { method: "PUT", body: JSON.stringify({ status, resolution_notes: notes }) }),

  // Connectors & Onboarding
  getConnectors: () => fetchJson<any[]>("/connectors"),
  syncConnector: (id: string) => fetchJson<any>(`/connectors/${id}/sync`, { method: "POST" }),
  validateOnboardingStep: (stepNumber: number, provider: string, authMethod: string, connectionInfo: any) => 
    fetchJson<any>("/onboarding/validate", {
      method: "POST",
      body: JSON.stringify({ step_number: stepNumber, provider, auth_method: authMethod, connection_info: connectionInfo }),
    }),

  // Admin
  getAuditLogs: () => fetchJson<any[]>("/admin/audit-logs"),
  getRoles: () => fetchJson<any[]>("/admin/roles"),
  getSettings: () => fetchJson<any>("/admin/settings"),
};
