const API_BASE = "/api/v1";

/** Get stored auth token */
function getToken(): string | null {
  return localStorage.getItem("token");
}

/** Build headers with auth token */
function authHeaders(): Record<string, string> {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/** Login and store token */
export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Login failed");
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
}

/** Register a new account */
export async function register(
  email: string,
  password: string,
  name: string,
): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  if (!res.ok) throw new Error("Registration failed");
}

/** Upload a document */
export async function uploadDocument(file: File): Promise<unknown> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

/** List user documents */
export async function listDocuments(): Promise<unknown> {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

/** Send a chat message and return the SSE response */
export function sendChatMessage(
  message: string,
  conversationId?: string,
): EventSource {
  // We use a custom approach since EventSource doesn't support POST
  // The actual implementation uses the useSSE hook
  const url = new URL(`${API_BASE}/chat`, window.location.origin);
  if (conversationId) url.searchParams.set("conversation_id", conversationId);
  const es = new EventSource(url.toString());
  return es;
}
