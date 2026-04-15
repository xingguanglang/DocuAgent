import type { ChatMessage, Conversation, DocumentInfo } from "../types";

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
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Registration failed");
  }
}

// --- Documents ---

/** Upload a document */
export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

/** List user documents */
export async function listDocuments(): Promise<{
  documents: DocumentInfo[];
  total: number;
}> {
  const res = await fetch(`${API_BASE}/documents`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

// --- Conversations ---

/** List user conversations (most recent first) */
export async function listConversations(): Promise<{
  conversations: Conversation[];
  total: number;
}> {
  const res = await fetch(`${API_BASE}/chat/conversations`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

/** Get messages for a conversation */
export async function getConversationMessages(
  conversationId: string,
): Promise<{ conversation_id: string; messages: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to fetch conversation messages");
  return res.json();
}

/** Delete a conversation */
export async function deleteConversation(
  conversationId: string,
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/conversations/${conversationId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to delete conversation");
}
