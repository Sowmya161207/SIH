import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Chat from './pages/Chat';
import SystemStatus from './pages/SystemStatus';
import { useDocuments } from './hooks/useDocuments';
import { useChat } from './hooks/useChat';

function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  
  // Custom hooks
  const docState = useDocuments();
  const chatState = useChat();

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
            uploadStatus={docState.uploadStatus}
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
          />
        );
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
