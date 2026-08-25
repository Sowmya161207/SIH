import React from 'react';
import { ChatWindow } from '../components/chat/ChatWindow';
import { Message } from '../types/chat';
import { ReportRecord } from '../types/reports';

interface ChatProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (content: string) => void;
  clearConversation: () => void;
  uploadFile?: (file: File) => Promise<any>;
  isUploading?: boolean;
  onGenerateReport?: (record: ReportRecord) => void;
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
  onGenerateReport,
}) => {
  return (
    <div className="h-full flex flex-col">
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        error={error}
        conversationId={conversationId}
        onSendMessage={sendMessage}
        onClearConversation={clearConversation}
        onUploadFile={uploadFile}
        isUploading={isFileUploading}
        onGenerateReport={onGenerateReport}
      />
    </div>
  );
};
export default Chat;
