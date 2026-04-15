import { useCallback, useEffect, useRef, useState } from "react";
import { MessageBubble } from "./MessageBubble";
import { AgentTrace } from "./AgentTrace";
import { useSSE } from "../hooks/useSSE";
import { getConversationMessages } from "../services/api";
import type { ChatMessage, Conversation, Source, SSEEvent } from "../types";
import type { ToastMessage } from "./Toast";

interface ChatInterfaceProps {
  onSidebarToggle: () => void;
  onSourcesChange: (sources: Source[]) => void;
  activeConversation: Conversation | null;
  onConversationCreated: () => void;
  onSelectConversation: (conv: Conversation) => void;
  onToast: (type: ToastMessage["type"], text: string) => void;
}

export function ChatInterface({
  onSidebarToggle,
  onSourcesChange,
  activeConversation,
  onConversationCreated,
  onSelectConversation,
  onToast,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [traceEvents, setTraceEvents] = useState<SSEEvent[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const conversationIdRef = useRef<string | null>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const { isStreaming, sendMessage, cancel } = useSSE({
    onMessage: (event) => {
      // Capture conversation_id from SSE stream
      if (event.event === "conversation_id") {
        conversationIdRef.current = event.data;
        return;
      }

      setTraceEvents((prev) => [...prev, event]);

      if (event.event === "message") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + event.data },
            ];
          }
          return [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: event.data,
              sources: [],
              tool_calls: [],
              created_at: new Date().toISOString(),
            },
          ];
        });
        scrollToBottom();
      }
    },
    onDone: () => {
      setTraceEvents([]);
      scrollToBottom();
      // Notify parent that a conversation was created/updated
      if (conversationIdRef.current) {
        onConversationCreated();
        // Update sidebar selection to the new conversation
        if (!activeConversation) {
          onSelectConversation({
            id: conversationIdRef.current,
            title: messages[0]?.content.slice(0, 80) || "New Conversation",
            created_at: new Date().toISOString(),
          });
        }
      }
    },
    onError: () => {
      onToast("error", "Connection error. Please try again.");
    },
  });

  // Load conversation history when activeConversation changes
  useEffect(() => {
    if (!activeConversation) {
      setMessages([]);
      setTraceEvents([]);
      conversationIdRef.current = null;
      return;
    }

    conversationIdRef.current = activeConversation.id;

    let cancelled = false;
    setLoadingHistory(true);

    getConversationMessages(activeConversation.id)
      .then((data) => {
        if (!cancelled) {
          setMessages(
            data.messages.map((msg) => ({
              ...msg,
              sources: msg.sources ?? [],
              tool_calls: msg.tool_calls ?? [],
            })),
          );
          setTraceEvents([]);
          setTimeout(scrollToBottom, 100);
        }
      })
      .catch(() => {
        if (!cancelled) {
          onToast("error", "Failed to load conversation history");
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingHistory(false);
      });

    return () => {
      cancelled = true;
    };
  }, [activeConversation, onToast, scrollToBottom]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      sources: [],
      tool_calls: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    sendMessage(trimmed, activeConversation?.id);
  };

  return (
    <div className="flex flex-1 flex-col">
      <header className="flex items-center gap-3 border-b border-gray-200 px-4 py-3">
        <button
          onClick={onSidebarToggle}
          className="rounded p-1 hover:bg-gray-100"
          aria-label="Toggle sidebar"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <h1 className="text-lg font-semibold">
          {activeConversation ? activeConversation.title : "DocuAgent"}
        </h1>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {loadingHistory ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <svg
              className="mr-2 h-5 w-5 animate-spin text-blue-500"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Loading conversation...
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <p className="text-xl font-medium">Ask anything about your documents</p>
            <p className="mt-2 text-sm">Upload documents and start asking questions</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              onSourceClick={(sources) => onSourcesChange(sources)}
            />
          ))
        )}
        {traceEvents.length > 0 && <AgentTrace events={traceEvents} />}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            disabled={isStreaming || loadingHistory}
          />
          {isStreaming ? (
            <button
              type="button"
              onClick={cancel}
              className="rounded-lg bg-red-500 px-4 py-2 text-white hover:bg-red-600"
            >
              Stop
            </button>
          ) : (
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
              disabled={!input.trim() || loadingHistory}
            >
              Send
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
