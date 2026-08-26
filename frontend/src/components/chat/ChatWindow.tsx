import React, { useRef, useEffect } from 'react';
import { Message } from '../../types/chat';
import { ReportRecord } from '../../types/reports';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import ChatLoading from './ChatLoading';
import { Trash2, AlertTriangle, Cpu } from 'lucide-react';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  onSendMessage: (content: string) => void;
  onClearConversation: () => void;
  onUploadFile?: (file: File) => Promise<any>;
  isUploading?: boolean;
  onGenerateReport?: (record: ReportRecord) => void;
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
  onGenerateReport,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, error]);

  return (
    <div
      className="flex flex-col h-full"
      style={{ background: '#060810' }}
    >
      {/* Chat Header */}
      <div
        className="flex items-center justify-between px-6 py-3 flex-shrink-0"
        style={{
          background: '#0a0f1a',
          borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
        }}
      >
        <div className="flex items-center gap-3">
          <div
            className="h-7 w-7 rounded-md flex items-center justify-center"
            style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.15)' }}
          >
            <Cpu className="h-3.5 w-3.5" style={{ color: '#818cf8' }} />
          </div>
          <div>
            <div className="text-[13px] font-semibold" style={{ color: '#e2e8f0', letterSpacing: '-0.01em' }}>
              Sovereign AI Assistant
            </div>
            {conversationId && (
              <div
                className="text-[9px] mt-0.5"
                style={{
                  color: 'rgba(148, 163, 184, 0.3)',
                  fontFamily: "'JetBrains Mono', monospace",
                  letterSpacing: '0.04em',
                }}
              >
                session:{' '}
                <span style={{ color: 'rgba(148, 163, 184, 0.45)' }}>
                  {conversationId.slice(0, 16)}...
                </span>
              </div>
            )}
          </div>
        </div>

        {messages.length > 0 && (
          <button
            onClick={onClearConversation}
            className="flex items-center gap-1.5 cursor-pointer"
            style={{
              padding: '5px 10px',
              borderRadius: '6px',
              background: 'transparent',
              border: '1px solid rgba(148, 163, 184, 0.08)',
              color: 'rgba(148, 163, 184, 0.4)',
              fontSize: '11px',
              fontWeight: 500,
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(244, 63, 94, 0.06)';
              (e.currentTarget as HTMLButtonElement).style.border = '1px solid rgba(244, 63, 94, 0.15)';
              (e.currentTarget as HTMLButtonElement).style.color = '#fb7185';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
              (e.currentTarget as HTMLButtonElement).style.border = '1px solid rgba(148, 163, 184, 0.08)';
              (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.4)';
            }}
          >
            <Trash2 className="h-3 w-3" />
            <span>New session</span>
          </button>
        )}
      </div>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div
            className="h-full flex flex-col items-center justify-center text-center"
            style={{ padding: '64px 32px' }}
          >
            {/* Empty state */}
            <div
              className="h-16 w-16 rounded-2xl flex items-center justify-center mb-6"
              style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(124,58,237,0.06) 100%)',
                border: '1px solid rgba(99, 102, 241, 0.15)',
                boxShadow: '0 0 40px rgba(99, 102, 241, 0.08)',
              }}
            >
              <Cpu className="h-7 w-7" style={{ color: '#818cf8' }} />
            </div>
            <h3
              className="font-bold mb-2"
              style={{ color: '#e2e8f0', fontSize: '16px', letterSpacing: '-0.02em' }}
            >
              Sovereign Intelligence Layer
            </h3>
            <p
              className="max-w-sm"
              style={{ color: 'rgba(148, 163, 184, 0.45)', fontSize: '13px', lineHeight: 1.6 }}
            >
              Ask questions about indexed documents. Your queries are processed
              entirely within your secure on-premise enclave.
            </p>

            {/* Prompt suggestions */}
            <div className="mt-8 space-y-2 w-full max-w-sm">
              {[
                'Summarize the key findings from indexed documents',
                'What are the main topics covered?',
                'Find information about...',
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => onSendMessage(prompt)}
                  className="w-full text-left cursor-pointer"
                  style={{
                    padding: '10px 14px',
                    borderRadius: '8px',
                    background: 'rgba(148, 163, 184, 0.03)',
                    border: '1px solid rgba(148, 163, 184, 0.07)',
                    color: 'rgba(148, 163, 184, 0.5)',
                    fontSize: '12px',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.background = 'rgba(99, 102, 241, 0.05)';
                    (e.currentTarget as HTMLButtonElement).style.border = '1px solid rgba(99, 102, 241, 0.12)';
                    (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.7)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.background = 'rgba(148, 163, 184, 0.03)';
                    (e.currentTarget as HTMLButtonElement).style.border = '1px solid rgba(148, 163, 184, 0.07)';
                    (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.5)';
                  }}
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div>
            {messages.map((msg, idx) => {
              // Find the preceding user message to use as the query for report titles
              const prevUser = idx > 0 && messages[idx - 1].role === 'user'
                ? messages[idx - 1].content
                : '';
              return (
                <MessageBubble
                  key={msg.id}
                  message={msg}
                  previousUserQuery={prevUser}
                  onGenerateReport={onGenerateReport}
                />
              );
            })}
          </div>
        )}

        {/* Loading */}
        {isLoading && <ChatLoading />}

        {/* Error */}
        {error && (
          <div
            className="mx-6 my-3 flex items-start gap-3 animate-fadeIn"
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              background: 'rgba(244, 63, 94, 0.06)',
              border: '1px solid rgba(244, 63, 94, 0.15)',
            }}
          >
            <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" style={{ color: '#fb7185' }} />
            <div>
              <div className="text-xs font-semibold" style={{ color: '#fb7185' }}>
                Query Failed
              </div>
              <div className="text-xs mt-0.5" style={{ color: 'rgba(251, 113, 133, 0.7)' }}>
                {error}
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div
        className="flex-shrink-0"
        style={{
          padding: '16px 24px 20px',
          background: '#0a0f1a',
          borderTop: '1px solid rgba(148, 163, 184, 0.06)',
        }}
      >
        <ChatInput
          onSend={onSendMessage}
          disabled={isLoading}
          onUploadFile={onUploadFile}
          isUploading={isUploading}
        />
      </div>
    </div>
  );
};
export default ChatWindow;
