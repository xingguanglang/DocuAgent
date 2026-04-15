import { useCallback, useEffect, useState } from "react";
import { DocumentUpload } from "./DocumentUpload";
import { deleteConversation, listConversations } from "../services/api";
import type { Conversation } from "../types";
import type { ToastMessage } from "./Toast";

interface SidebarProps {
  onClose: () => void;
  activeConversationId: string | null;
  onSelectConversation: (conv: Conversation) => void;
  onNewConversation: () => void;
  onToast: (type: ToastMessage["type"], text: string) => void;
  refreshKey: number;
}

export function Sidebar({
  onClose,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onToast,
  refreshKey,
}: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchConversations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listConversations();
      setConversations(data.conversations);
    } catch {
      // Silently fail — user may not be logged in
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount and when refreshKey changes (new conversation created)
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations, refreshKey]);

  const handleDelete = useCallback(
    async (e: React.MouseEvent, conv: Conversation) => {
      e.stopPropagation();
      try {
        await deleteConversation(conv.id);
        setConversations((prev) => prev.filter((c) => c.id !== conv.id));
        if (activeConversationId === conv.id) {
          onNewConversation();
        }
        onToast("success", "Conversation deleted");
      } catch {
        onToast("error", "Failed to delete conversation");
      }
    },
    [activeConversationId, onNewConversation, onToast],
  );

  return (
    <aside className="flex w-72 flex-col border-r border-gray-200 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h2 className="text-sm font-semibold">DocuAgent</h2>
        <button
          onClick={onClose}
          className="rounded p-1 hover:bg-gray-100 lg:hidden"
          aria-label="Close sidebar"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Document Upload */}
      <div className="p-4">
        <DocumentUpload onToast={onToast} />
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto px-3">
        <h3 className="mb-2 px-1 text-xs font-medium uppercase text-gray-400">Conversations</h3>

        {loading && conversations.length === 0 ? (
          <p className="px-1 text-sm text-gray-400">Loading...</p>
        ) : conversations.length === 0 ? (
          <p className="px-1 text-sm text-gray-400">No conversations yet</p>
        ) : (
          <ul className="space-y-1">
            {conversations.map((conv) => (
              <li key={conv.id}>
                <button
                  onClick={() => onSelectConversation(conv)}
                  className={`group flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                    activeConversationId === conv.id
                      ? "bg-blue-50 text-blue-700"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  {/* Chat icon */}
                  <svg
                    className="h-4 w-4 flex-shrink-0 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                  <span className="flex-1 truncate">{conv.title}</span>
                  {/* Delete button — visible on hover */}
                  <button
                    onClick={(e) => handleDelete(e, conv)}
                    className="hidden flex-shrink-0 rounded p-0.5 text-gray-400 hover:bg-red-100 hover:text-red-500 group-hover:block"
                    aria-label="Delete conversation"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* New Conversation Button */}
      <div className="border-t border-gray-200 p-4">
        <button
          onClick={onNewConversation}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Conversation
        </button>
      </div>
    </aside>
  );
}
