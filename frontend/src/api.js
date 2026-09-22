const TOKEN_KEY = "jobpilot_access_token";
const REFRESH_KEY = "jobpilot_refresh_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveTokens({ access, refresh }) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export async function api(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }), ...options.headers };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(path, { ...options, headers });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = typeof data === "object" ? Object.values(data).flat().join(" ") : "Something went wrong.";
    throw new Error(message || "Something went wrong.");
  }
  return data;
}

export function listResults(data) {
  return Array.isArray(data) ? data : data.results || [];
}
