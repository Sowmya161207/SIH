import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Chat from './pages/Chat';
import SystemStatus from './pages/SystemStatus';
import Login from './pages/Login';
import EquipmentHealth from './pages/EquipmentHealth';
import SuggestionBox from './pages/SuggestionBox';
import ProblemBox from './pages/ProblemBox';
import { useDocuments } from './hooks/useDocuments';
import { useChat } from './hooks/useChat';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentTab, setCurrentTab] = useState('dashboard');

  // Custom hooks
  const docState = useDocuments();
  const chatState = useChat();

  const handleAskAI = (query: string) => {
    setCurrentTab('chat');
    chatState.sendMessage(query);
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'dashboard':
        return (
          <Dashboard
            documents={docState.documents}
            setCurrentTab={setCurrentTab}
          />
        );
      case 'documents':
        return (
          <Documents
            documents={docState.documents}
            uploadFile={docState.uploadFile}
            isUploading={docState.isUploading}
            uploadError={docState.uploadError}
            uploadSuccess={docState.uploadSuccess}
            clearUploadState={docState.clearUploadState}
            removeDocument={docState.removeDocument}
          />
        );
      case 'chat':
        return (
          <Chat
            messages={chatState.messages}
            isLoading={chatState.isLoading}
            error={chatState.error}
            conversationId={chatState.conversationId}
            sendMessage={chatState.sendMessage}
            clearConversation={chatState.clearConversation}
            uploadFile={docState.uploadFile}
            isUploading={docState.isUploading}
          />
        );
      case 'equipment':
        return <EquipmentHealth onAskAI={handleAskAI} />;
      case 'suggestion':
        return <SuggestionBox />;
      case 'problem':
        return <ProblemBox />;
      case 'system':
        return <SystemStatus />;
      default:
        return (
          <Dashboard
            documents={docState.documents}
            setCurrentTab={setCurrentTab}
          />
        );
    }
  };

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="flex h-screen w-screen bg-[#0b0f19] text-slate-100 overflow-hidden select-none">
      {/* Sidebar Navigation */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header Indicator */}
        <Header />

        {/* Workspace Views */}
        <main className="flex-1 overflow-y-auto px-8 py-6">
          <div className="max-w-6xl mx-auto h-full">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
