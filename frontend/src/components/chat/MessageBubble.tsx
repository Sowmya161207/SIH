import React, { useState } from 'react';
import { Message } from '../../types/chat';
import { ReportRecord } from '../../types/reports';
import SourceList from './SourceList';
import ReportModal from '../reports/ReportModal';
import { deriveReportTitle, deriveReportType } from '../../hooks/useReports';
import { User, Cpu, FileBarChart2 } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
  onGenerateReport?: (record: ReportRecord) => void;
  previousUserQuery?: string;  // the user message immediately before this assistant msg
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onGenerateReport,
  previousUserQuery = '',
}) => {
  const isUser = message.role === 'user';
  const [showReport, setShowReport] = useState(false);
  const [reportRecord, setReportRecord] = useState<ReportRecord | null>(null);

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const hasSources = !isUser && (message.sources?.length ?? 0) > 0;

  const handleGenerateReport = () => {
    const record: ReportRecord = {
      id: crypto.randomUUID(),
      title: deriveReportTitle(previousUserQuery || message.content),
      type: deriveReportType(previousUserQuery || message.content),
      generatedAt: new Date().toISOString(),
      messageContent: message.content,
      sources: message.sources ?? [],
      query: previousUserQuery || '',
    };
    setReportRecord(record);
    setShowReport(true);
    onGenerateReport?.(record);
  };

  return (
    <>
      <div
        className="flex gap-4 animate-fadeIn"
        style={{
          padding: '20px 24px',
          borderBottom: '1px solid rgba(148, 163, 184, 0.04)',
          background: isUser ? 'rgba(10, 15, 26, 0.6)' : 'transparent',
        }}
      >
        {/* Avatar */}
        <div className="flex-shrink-0 mt-0.5">
          <div
            className="h-7 w-7 rounded-md flex items-center justify-center"
            style={
              isUser
                ? {
                    background: 'rgba(148, 163, 184, 0.08)',
                    border: '1px solid rgba(148, 163, 184, 0.1)',
                  }
                : {
                    background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(124,58,237,0.15) 100%)',
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                  }
            }
          >
            {isUser ? (
              <User className="h-3.5 w-3.5" style={{ color: 'rgba(148, 163, 184, 0.5)' }} />
            ) : (
              <Cpu className="h-3.5 w-3.5" style={{ color: '#818cf8' }} />
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Sender label */}
          <div
            className="text-[10px] font-semibold mb-2 tracking-wider uppercase"
            style={{
              color: isUser ? 'rgba(148, 163, 184, 0.4)' : 'rgba(99, 102, 241, 0.6)',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {isUser ? 'You' : 'Sovereign AI'}
          </div>

          {/* Attached file tag on user message */}
          {isUser && message.attached_filename && (
            <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-indigo-950/60 border border-indigo-500/20 text-indigo-300 text-[11px] font-mono">
              <FileBarChart2 className="h-3 w-3 text-indigo-400" />
              <span>Query Document: <strong>{message.attached_filename}</strong></span>
            </div>
          )}

          {/* Message text */}
          <div
            className="leading-relaxed whitespace-pre-wrap mt-1"
            style={{
              fontSize: '14px',
              color: isUser ? 'rgba(226, 232, 240, 0.85)' : '#e2e8f0',
              lineHeight: 1.75,
            }}
          >
            {message.content}
          </div>

          {/* Sources */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-4">
              <SourceList sources={message.sources} />
            </div>
          )}

          {/* Generate & Download PDF Report action for all AI responses */}
          {!isUser && (
            <div className="mt-4">
              <button
                onClick={handleGenerateReport}
                className="flex items-center gap-1.5 cursor-pointer"
                style={{
                  padding: '6px 12px',
                  borderRadius: '7px',
                  background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(124,58,237,0.1) 100%)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  color: '#a5b4fc',
                  fontSize: '11px',
                  fontWeight: 600,
                  letterSpacing: '0.01em',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(99, 102, 241, 0.2)';
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 12px rgba(99,102,241,0.2)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(124,58,237,0.1) 100%)';
                  (e.currentTarget as HTMLButtonElement).style.boxShadow = 'none';
                }}
              >
                <FileBarChart2 className="h-3.5 w-3.5 text-indigo-400" />
                <span>Generate PDF Report & Download</span>
              </button>
            </div>
          )}

          {/* Timestamp */}
          <div
            className="mt-3 text-[10px]"
            style={{
              color: 'rgba(148, 163, 184, 0.25)',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>

      {/* Report Modal */}
      {showReport && reportRecord && (
        <ReportModal
          report={reportRecord}
          onClose={() => setShowReport(false)}
        />
      )}
    </>
  );
};
export default MessageBubble;
