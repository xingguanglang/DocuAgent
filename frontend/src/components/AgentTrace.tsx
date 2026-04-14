import type { SSEEvent } from "../types";

interface AgentTraceProps {
  events: SSEEvent[];
}

const EVENT_LABELS: Record<string, { label: string; color: string }> = {
  thought: { label: "Thinking", color: "text-purple-600 bg-purple-50" },
  action: { label: "Action", color: "text-blue-600 bg-blue-50" },
  observation: { label: "Observation", color: "text-green-600 bg-green-50" },
  error: { label: "Error", color: "text-red-600 bg-red-50" },
};

export function AgentTrace({ events }: AgentTraceProps) {
  const traceEvents = events.filter((e) => e.event !== "message" && e.event !== "done");

  if (traceEvents.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
      <p className="mb-2 text-xs font-medium text-gray-500 uppercase">Agent reasoning</p>
      <div className="space-y-1">
        {traceEvents.map((event, i) => {
          const config = EVENT_LABELS[event.event] || {
            label: event.event,
            color: "text-gray-600 bg-gray-100",
          };
          return (
            <div key={i} className="flex items-start gap-2 text-sm">
              <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${config.color}`}>
                {config.label}
              </span>
              <span className="text-gray-700">{event.data}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
