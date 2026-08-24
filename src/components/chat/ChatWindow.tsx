import React, { useRef, useEffect } from 'react';
import { Message } from '../../types/chat';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import ChatLoading from './ChatLoading';
import { Trash2, AlertTriangle, Sparkles } from 'lucide-react';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  onSendMessage: (content: string) => void;
  onClearConversation: () => void;
  onUploadFile?: (file: File) => Promise<any>;
  isUploading?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  error,
  conversationId,
  onSendMessage,
  onClearConversation,
  onUploadFile,
  isUploading,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, error]);

  return (
    <div className="bg-[#0f172a]/20 border border-[#1e293b] rounded-xl flex flex-col h-[calc(100vh-12rem)] shadow-md overflow-hidden">
      {/* Chat Window Header */}
      <div className="px-6 py-4 bg-[#0d131f] border-b border-[#1e293b] flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-3">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Sovereign Assistant Session</h3>
            {conversationId && (
              <p className="text-[10px] font-mono text-slate-500 mt-0.5">CID: {conversationId}</p>
            )}
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={onClearConversation}
            className="flex items-center space-x-1.5 px-3 py-1.5 border border-[#1e293b] hover:border-rose-500/30 hover:bg-rose-500/5 text-slate-400 hover:text-rose-400 rounded-lg text-xs font-medium transition-colors cursor-pointer"
            title="Start new conversation"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Reset Chat</span>
          </button>
        )}
      </div>

      {/* Message History Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8">
            <div className="p-4 bg-indigo-500/10 text-indigo-400 rounded-2xl mb-4 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.1)]">
              <Sparkles className="h-7 w-7" />
            </div>
            <h4 className="text-sm font-semibold text-slate-300">Secure On-Premise Assistant</h4>
            <p className="text-xs text-slate-500 max-w-sm mt-1">
              Ask questions about the uploaded and indexed documents. All data remains in your local secure container.
            </p>
          </div>
        ) : (
          <div>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && <ChatLoading />}

        {/* Error State */}
        {error && (
          <div className="my-4 p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start space-x-2.5 text-rose-400 text-xs max-w-[85%]">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Query Failed</p>
              <p className="mt-0.5">{error}</p>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Box Area */}
      <div className="p-4 bg-[#0d131f] border-t border-[#1e293b] flex-shrink-0">
        <ChatInput onSend={onSendMessage} disabled={isLoading} onUploadFile={onUploadFile} isUploading={isUploading} />
      </div>
    </div>
  );
};
export default ChatWindow;
