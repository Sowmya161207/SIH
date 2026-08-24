import React from 'react';
import { ChatWindow } from '../components/chat/ChatWindow';
import { Message } from '../types/chat';

interface ChatProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (content: string) => void;
  clearConversation: () => void;
  uploadFile?: (file: File) => Promise<any>;
  isUploading?: boolean;
}

export const Chat: React.FC<ChatProps> = ({
  messages,
  isLoading,
  error,
  conversationId,
  sendMessage,
  clearConversation,
  uploadFile,
  isUploading: isFileUploading,
}) => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">AI Assistant</h1>
        <p className="text-xs text-slate-400 mt-1">
          Perform Q&A, retrieve findings, and synthesize insights from indexed workspace files securely.
        </p>
      </div>

      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        error={error}
        conversationId={conversationId}
        onSendMessage={sendMessage}
        onClearConversation={clearConversation}
        onUploadFile={uploadFile}
        isUploading={isFileUploading}
      />
    </div>
  );
};
export default Chat;
