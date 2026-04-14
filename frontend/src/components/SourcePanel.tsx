import type { Source } from "../types";

interface SourcePanelProps {
  sources: Source[];
  onClose: () => void;
}

export function SourcePanel({ sources, onClose }: SourcePanelProps) {
  return (
    <aside className="w-80 border-l border-gray-200 bg-white overflow-y-auto">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h2 className="text-sm font-semibold">Sources ({sources.length})</h2>
        <button
          onClick={onClose}
          className="rounded p-1 hover:bg-gray-100"
          aria-label="Close sources"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div className="space-y-3 p-4">
        {sources.map((source, i) => (
          <div key={i} className="rounded-lg border border-gray-200 p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">
                {source.document_name}
              </span>
              <span className="text-xs text-gray-500">
                {Math.round(source.relevance_score * 100)}% match
              </span>
            </div>
            {source.page_number && (
              <span className="text-xs text-gray-400">Page {source.page_number}</span>
            )}
            <p className="mt-2 text-xs text-gray-600 line-clamp-4">{source.chunk_text}</p>
          </div>
        ))}
      </div>
    </aside>
  );
}
