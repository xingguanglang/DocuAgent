import { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatInterface } from "./components/ChatInterface";
import { SourcePanel } from "./components/SourcePanel";
import type { Source } from "./types";

function App() {
  const [selectedSources, setSelectedSources] = useState<Source[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden">
      {sidebarOpen && (
        <Sidebar onClose={() => setSidebarOpen(false)} />
      )}
      <main className="flex flex-1 overflow-hidden">
        <ChatInterface
          onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}
          onSourcesChange={setSelectedSources}
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
