import { DocumentUpload } from "./DocumentUpload";

interface SidebarProps {
  onClose: () => void;
}

export function Sidebar({ onClose }: SidebarProps) {
  return (
    <aside className="flex w-72 flex-col border-r border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h2 className="text-sm font-semibold">Documents</h2>
        <button
          onClick={onClose}
          className="rounded p-1 hover:bg-gray-100 lg:hidden"
          aria-label="Close sidebar"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-4">
        <DocumentUpload />
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <h3 className="mb-2 text-xs font-medium uppercase text-gray-400">Conversations</h3>
        <p className="text-sm text-gray-400">No conversations yet</p>
      </div>

      <div className="border-t border-gray-200 p-4">
        <button className="w-full rounded-lg bg-gray-100 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200">
          New Conversation
        </button>
      </div>
    </aside>
  );
}
