import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Chat from './pages/Chat';
import SystemStatus from './pages/SystemStatus';
import Login from './pages/Login';
import Reports from './pages/Reports';
import AuditLogs from './pages/AuditLogs';

import { useDocuments } from './hooks/useDocuments';
import { useChat } from './hooks/useChat';
import { useReports } from './hooks/useReports';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<'admin' | 'employee' | null>(null);
  const [currentTab, setCurrentTab] = useState('dashboard');

  // Custom hooks
  const docState = useDocuments();
  const chatState = useChat();
  const reportState = useReports();



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
            submitText={docState.submitText}
            isUploadingText={docState.isUploadingText}
            uploadTextError={docState.uploadTextError}
            uploadTextSuccess={docState.uploadTextSuccess}
            clearUploadTextState={docState.clearUploadTextState}
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
            onGenerateReport={reportState.addReport}
          />
        );
      case 'reports':
        return (
          <Reports
            history={reportState.history}
            onRemove={reportState.removeReport}
            onClearAll={reportState.clearHistory}
          />
        );
      case 'system':
        if (userRole === 'employee') {
          return <Dashboard documents={docState.documents} setCurrentTab={setCurrentTab} />;
        }
        return <SystemStatus />;
      case 'audit-logs':
        if (userRole === 'employee') {
          return <Dashboard documents={docState.documents} setCurrentTab={setCurrentTab} />;
        }
        return <AuditLogs />;
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
    return (
      <Login
        onLogin={(role) => {
          setIsAuthenticated(true);
          setUserRole(role);
        }}
      />
    );
  }

  return (
    <div className="flex h-screen w-screen bg-[#060810] text-slate-100 overflow-hidden select-none">
      {/* Sidebar Navigation */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} userRole={userRole} />

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Header */}
        <Header currentTab={currentTab} userRole={userRole} />

        {/* Workspace Views */}
        <main className="flex-1 overflow-y-auto">
          <div className="h-full">
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
