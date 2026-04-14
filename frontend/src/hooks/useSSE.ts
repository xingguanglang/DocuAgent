import { useCallback, useRef, useState } from "react";
import type { SSEEvent } from "../types";

interface UseSSEOptions {
  onMessage?: (event: SSEEvent) => void;
  onError?: (error: Event) => void;
  onDone?: () => void;
}

interface UseSSEReturn {
  isStreaming: boolean;
  sendMessage: (message: string, conversationId?: string) => void;
  cancel: () => void;
}

/**
 * Hook for sending chat messages and receiving SSE streaming responses.
 * Uses fetch + ReadableStream to support POST requests with SSE.
 */
export function useSSE({ onMessage, onError, onDone }: UseSSEOptions): UseSSEReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
  }, []);

  const sendMessage = useCallback(
    async (message: string, conversationId?: string) => {
      cancel();
      const controller = new AbortController();
      abortRef.current = controller;
      setIsStreaming(true);

      try {
        const token = localStorage.getItem("token");
        const res = await fetch("/api/v1/chat/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ message, conversation_id: conversationId }),
          signal: controller.signal,
        });

        if (!res.ok || !res.body) {
          throw new Error(`HTTP ${res.status}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              const eventType = line.slice(7).trim();
              const nextLine = lines[lines.indexOf(line) + 1];
              const data = nextLine?.startsWith("data: ") ? nextLine.slice(6) : "";
              const sseEvent: SSEEvent = {
                event: eventType as SSEEvent["event"],
                data,
              };
              if (eventType === "done") {
                onDone?.();
              } else {
                onMessage?.(sseEvent);
              }
            }
          }
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          onError?.(err as Event);
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [cancel, onMessage, onError, onDone],
  );

  return { isStreaming, sendMessage, cancel };
}
