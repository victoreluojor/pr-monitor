const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  login: (email: string, password: string) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => request("/auth/me"),
  listClients: () => request("/clients/"),
  createClient: (payload: any) => request("/clients/", { method: "POST", body: JSON.stringify(payload) }),
  listKeywords: (clientId: string) => request(`/clients/${clientId}/keywords/`),
  addKeyword: (clientId: string, payload: any) =>
    request(`/clients/${clientId}/keywords/`, { method: "POST", body: JSON.stringify(payload) }),
  getDashboard: (clientId: string) => request(`/clients/${clientId}/dashboard/`),
  listMentions: (clientId: string, params: string = "") =>
    request(`/clients/${clientId}/mentions/${params}`),
  listAlerts: (clientId: string) => request(`/clients/${clientId}/alerts/`),
};

export function saveToken(token: string) {
  localStorage.setItem("token", token);
}

export function logout() {
  localStorage.removeItem("token");
}
