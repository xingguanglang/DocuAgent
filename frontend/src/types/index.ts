/** Citation source from RAG retrieval */
export interface Source {
  document_id: string;
  document_name: string;
  chunk_text: string;
  relevance_score: number;
  page_number?: number;
}

/** Agent tool call metadata */
export interface ToolCallInfo {
  tool_name: string;
  input_summary: string;
  output_summary: string;
}

/** Chat message */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: Source[];
  tool_calls: ToolCallInfo[];
  created_at: string;
}

/** SSE event from the chat endpoint */
export interface SSEEvent {
  event: "thought" | "action" | "observation" | "message" | "source" | "done" | "error";
  data: string;
}

/** Document metadata */
export interface DocumentInfo {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  chunk_count: number;
  status: "processing" | "ready" | "error";
  uploaded_at: string;
}

/** Conversation summary for sidebar */
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
}
