const API = import.meta.env.VITE_API_URL ?? "";

let accessToken = localStorage.getItem("dlkip_token") ?? "";

export function setToken(t: string) {
  accessToken = t;
  localStorage.setItem("dlkip_token", t);
}

export function getToken() {
  return accessToken;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "content-type": "application/json",
      ...(accessToken ? { authorization: `Bearer ${accessToken}` } : {}),
      ...(options.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? `request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export interface LoginResponse {
  accessToken: string;
  user: { name: string; email: string; role: string };
}

export const api = {
  login: (email: string, password: string) =>
    request<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  upload: (title: string, text: string) =>
    request("/api/documents", {
      method: "POST",
      body: JSON.stringify({ title, text }),
    }),

  listDocuments: () => request<any[]>("/api/documents"),

  ask: (question: string) =>
    request<any>("/api/ask", { method: "POST", body: JSON.stringify({ question }) }),

  codeLookup: (code: string) =>
    request<any>("/api/search/code", { method: "POST", body: JSON.stringify({ code }) }),
};
