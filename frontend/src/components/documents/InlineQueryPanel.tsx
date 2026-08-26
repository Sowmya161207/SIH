import React, { useState, useRef } from 'react';
import { Send, Cpu, ChevronDown, ChevronUp, Loader2, AlertTriangle, BookOpen, Paperclip, X, FileBarChart2, FileText } from 'lucide-react';
import { sendChatMessage } from '../../services/api/chat';
import { uploadDocument } from '../../services/api/documents';
import { Source } from '../../types/chat';
import { ReportRecord } from '../../types/reports';
import ReportModal from '../reports/ReportModal';
import { deriveReportTitle, deriveReportType } from '../../hooks/useReports';

interface QAResult {
  question: string;
  answer: string;
  sources: Source[];
  attachedName?: string;
}

export const InlineQueryPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<QAResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [attachedFile, setAttachedFile] = useState<{ id: string; name: string } | null>(null);
  const [isUploadingAttachment, setIsUploadingAttachment] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportRecord, setReportRecord] = useState<ReportRecord | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploadingAttachment(true);
    setError(null);
    try {
      const res = await uploadDocument(file);
      if (res && res.document_id) {
        setAttachedFile({ id: res.document_id, name: res.filename || file.name });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload attachment.');
    } finally {
      setIsUploadingAttachment(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleQuery = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const q = query.trim() || (attachedFile ? `Analyze attached document ${attachedFile.name}` : '');
    if (!q || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const resp = await sendChatMessage({
        message: q,
        document_id: attachedFile?.id || undefined,
        attached_filename: attachedFile?.name || undefined,
      });
      setResult({
        question: q,
        answer: resp.answer,
        sources: resp.sources || [],
        attachedName: attachedFile?.name,
      });
      setQuery('');
      setAttachedFile(null);
      setIsExpanded(true);
    } catch (err: any) {
      setError(err.message || 'Failed to process query.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = () => {
    if (!result) return;
    const record: ReportRecord = {
      id: crypto.randomUUID(),
      title: deriveReportTitle(result.question),
      type: deriveReportType(result.question),
      generatedAt: new Date().toISOString(),
      messageContent: result.answer,
      sources: result.sources,
      query: result.question,
    };
    setReportRecord(record);
    setShowReportModal(true);
  };

  // Suggested prompts
  const suggestions = [
    'Summarize the key procedures',
    'What safety steps are described?',
    'List the main topics covered',
  ];

  return (
    <div
      id="query-knowledge-base"
      style={{
        background: 'rgba(10, 15, 26, 0.95)',
        border: '1px solid rgba(99, 102, 241, 0.18)',
        borderRadius: '12px',
        overflow: 'hidden',
        boxShadow: '0 4px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(99,102,241,0.05)',
      }}
    >
      {/* Panel Header */}
      <div
        className="flex items-center justify-between cursor-pointer"
        style={{
          padding: '14px 18px',
          background: 'rgba(99, 102, 241, 0.04)',
          borderBottom: isExpanded ? '1px solid rgba(99,102,241,0.1)' : 'none',
        }}
        onClick={() => setIsExpanded((v) => !v)}
      >
        <div className="flex items-center gap-2.5">
          <div
            className="h-7 w-7 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(124,58,237,0.12) 100%)',
              border: '1px solid rgba(99,102,241,0.2)',
            }}
          >
            <Cpu className="h-3.5 w-3.5" style={{ color: '#818cf8' }} />
          </div>
          <div>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#c7d2fe', letterSpacing: '-0.01em' }}>
              Query Knowledge Base
            </span>
            <span
              style={{
                marginLeft: '8px',
                fontSize: '9px',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: 'rgba(148, 163, 184, 0.3)',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              AI-Powered · On-Premise
            </span>
          </div>
        </div>
        <div style={{ color: 'rgba(148,163,184,0.3)' }}>
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </div>

      {isExpanded && (
        <div style={{ padding: '16px 18px' }}>
          {/* Hidden file input */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.txt,.ppt,.pptx"
            className="hidden"
          />

          {/* Attached Document Pill */}
          {attachedFile && (
            <div
              className="mb-2.5 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs animate-fadeIn"
              style={{
                background: 'rgba(99, 102, 241, 0.12)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                color: '#a5b4fc',
              }}
            >
              <FileText className="h-3.5 w-3.5 flex-shrink-0 text-indigo-400" />
              <span className="font-mono text-[11px] truncate max-w-[280px]">
                Attached context: <strong>{attachedFile.name}</strong>
              </span>
              <button
                type="button"
                onClick={() => setAttachedFile(null)}
                className="hover:text-rose-400 cursor-pointer ml-1 p-0.5 rounded"
                title="Remove attachment"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}

          {/* Query Input Form */}
          <form onSubmit={handleQuery}>
            <div
              className="flex items-center gap-2"
              style={{
                background: 'rgba(6, 8, 16, 0.8)',
                border: '1px solid rgba(148, 163, 184, 0.1)',
                borderRadius: '8px',
                padding: '8px 10px 8px 14px',
                transition: 'border-color 0.15s ease',
              }}
            >
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading || isUploadingAttachment}
                title="Attach query document or image"
                className="p-1.5 rounded-md hover:bg-slate-800 text-slate-400 hover:text-indigo-300 transition-colors cursor-pointer"
              >
                {isUploadingAttachment ? (
                  <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />
                ) : (
                  <Paperclip className="h-4 w-4" />
                )}
              </button>

              <input
                id="query-knowledge-base-input"
                ref={inputRef}
                type="text"
                value={query}
                onFocus={() => setIsExpanded(true)}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={attachedFile ? `Ask a question about ${attachedFile.name} or company docs…` : "Ask a question about company documents or attach a file…"}
                disabled={isLoading}
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#e2e8f0',
                  fontSize: '13px',
                  caretColor: '#818cf8',
                }}
              />
              <button
                type="submit"
                disabled={(!query.trim() && !attachedFile) || isLoading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  background: (query.trim() || attachedFile) && !isLoading
                    ? 'linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)'
                    : 'rgba(148,163,184,0.06)',
                  border: 'none',
                  cursor: (query.trim() || attachedFile) && !isLoading ? 'pointer' : 'not-allowed',
                  gap: '5px',
                  transition: 'all 0.15s ease',
                  flexShrink: 0,
                }}
              >
                {isLoading ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" style={{ color: '#818cf8' }} />
                ) : (
                  <>
                    <Send className="h-3.5 w-3.5" style={{ color: (query.trim() || attachedFile) ? '#fff' : 'rgba(148,163,184,0.3)' }} />
                    <span style={{ fontSize: '11px', fontWeight: 600, color: (query.trim() || attachedFile) ? '#fff' : 'rgba(148,163,184,0.3)' }}>
                      Ask
                    </span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Suggested prompts (only when no result) */}
          {!result && !isLoading && !error && (
            <div className="flex flex-wrap gap-2 mt-3">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    setQuery(s);
                    inputRef.current?.focus();
                  }}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '5px',
                    background: 'rgba(148,163,184,0.04)',
                    border: '1px solid rgba(148,163,184,0.08)',
                    color: 'rgba(148,163,184,0.5)',
                    fontSize: '11px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div
              className="mt-4 flex items-center gap-3"
              style={{
                padding: '12px 14px',
                borderRadius: '8px',
                background: 'rgba(99,102,241,0.04)',
                border: '1px solid rgba(99,102,241,0.1)',
              }}
            >
              <Loader2 className="h-4 w-4 animate-spin flex-shrink-0" style={{ color: '#818cf8' }} />
              <span style={{ fontSize: '12px', color: 'rgba(148,163,184,0.6)' }}>
                Retrieving from Company Knowledge Base + Query Document…
              </span>
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              className="mt-4 flex items-start gap-2"
              style={{
                padding: '10px 14px',
                borderRadius: '8px',
                background: 'rgba(244,63,94,0.05)',
                border: '1px solid rgba(244,63,94,0.15)',
              }}
            >
              <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" style={{ color: '#fb7185' }} />
              <span style={{ fontSize: '12px', color: 'rgba(251,113,133,0.8)' }}>{error}</span>
            </div>
          )}

          {/* Answer */}
          {result && (
            <div className="mt-4 space-y-3">
              {/* Question echo */}
              <div
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  background: 'rgba(99,102,241,0.06)',
                  border: '1px solid rgba(99,102,241,0.12)',
                  fontSize: '11px',
                  color: 'rgba(199,210,254,0.7)',
                  fontStyle: 'italic',
                }}
              >
                "{result.question}" {result.attachedName ? `[Attached: ${result.attachedName}]` : ''}
              </div>

              {/* Answer body */}
              <div
                style={{
                  padding: '14px 16px',
                  borderRadius: '8px',
                  background: 'rgba(6,8,16,0.6)',
                  border: '1px solid rgba(148,163,184,0.08)',
                  fontSize: '13px',
                  color: '#cbd5e1',
                  lineHeight: 1.7,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {result.answer}
              </div>

              {/* Action bar with PDF Report Generation */}
              <div className="flex items-center justify-between pt-1">
                {result.sources.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.sources.map((src, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-1.5"
                        style={{
                          padding: '3px 9px',
                          borderRadius: '4px',
                          background: 'rgba(148,163,184,0.04)',
                          border: '1px solid rgba(148,163,184,0.08)',
                        }}
                      >
                        <BookOpen className="h-3 w-3" style={{ color: 'rgba(148,163,184,0.4)' }} />
                        <span
                          style={{
                            fontSize: '10px',
                            color: 'rgba(148,163,184,0.5)',
                            fontFamily: "'JetBrains Mono', monospace",
                          }}
                        >
                          {src.document}
                          {src.page != null ? ` · p.${src.page}` : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : <div />}

                <button
                  type="button"
                  onClick={handleGenerateReport}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-600/30 text-xs font-semibold cursor-pointer transition-all"
                >
                  <FileBarChart2 className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Generate PDF Report & Download</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* PDF Report Download Modal */}
      {showReportModal && reportRecord && (
        <ReportModal report={reportRecord} onClose={() => setShowReportModal(false)} />
      )}
    </div>
  );
};

export default InlineQueryPanel;
