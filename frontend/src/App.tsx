import { useCallback, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatInterface } from "./components/ChatInterface";
import { SourcePanel } from "./components/SourcePanel";
import { ToastContainer, useToast } from "./components/Toast";
import type { Conversation, Source } from "./types";

function App() {
  const [selectedSources, setSelectedSources] = useState<Source[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const { messages: toasts, addToast, dismissToast } = useToast();

  /** Called when a new conversation is created (from chat SSE) */
  const handleConversationCreated = useCallback(() => {
    setRefreshKey((k) => k + 1);
  }, []);

  /** Start a new blank conversation */
  const handleNewConversation = useCallback(() => {
    setActiveConversation(null);
  }, []);

  /** Select an existing conversation from sidebar */
  const handleSelectConversation = useCallback((conv: Conversation) => {
    setActiveConversation(conv);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      <ToastContainer messages={toasts} onDismiss={dismissToast} />

      {sidebarOpen && (
        <Sidebar
          onClose={() => setSidebarOpen(false)}
          activeConversationId={activeConversation?.id ?? null}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          onToast={addToast}
          refreshKey={refreshKey}
        />
      )}
      <main className="flex flex-1 overflow-hidden">
        <ChatInterface
          onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
          onSourcesChange={setSelectedSources}
          activeConversation={activeConversation}
          onConversationCreated={handleConversationCreated}
          onSelectConversation={handleSelectConversation}
          onToast={addToast}
        />
        {selectedSources.length > 0 && (
          <SourcePanel
            sources={selectedSources}
            onClose={() => setSelectedSources([])}
          />
        )}
      </main>
    </div>
  );
}

export default App;
