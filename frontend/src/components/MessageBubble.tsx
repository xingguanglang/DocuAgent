import type { ChatMessage, Source } from "../types";

interface MessageBubbleProps {
  message: ChatMessage;
  onSourceClick: (sources: Source[]) => void;
}

export function MessageBubble({ message, onSourceClick }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-900 border border-gray-200 shadow-sm"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {message.sources.length > 0 && (
          <button
            onClick={() => onSourceClick(message.sources)}
            className="mt-2 flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
          >
            <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            {message.sources.length} source{message.sources.length > 1 ? "s" : ""}
          </button>
        )}

        {message.tool_calls.length > 0 && (
          <div className="mt-2 space-y-1">
            {message.tool_calls.map((tc, i) => (
              <span
                key={i}
                className="inline-block mr-1 rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
              >
                {tc.tool_name}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
