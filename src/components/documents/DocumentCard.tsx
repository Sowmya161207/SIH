import React from 'react';
import { DocumentResponse } from '../../types/documents';
import DocumentStatus from './DocumentStatus';
import { FileText, Trash2, Copy, Check } from 'lucide-react';

interface DocumentCardProps {
  document: DocumentResponse;
  onRemove: (id: string) => void;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ document, onRemove }) => {
  const [copied, setCopied] = React.useState(false);

  const formatBytes = (bytes: number, decimals = 1) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
      });
    } catch { return dateString; }
  };

  const handleCopyId = () => {
    navigator.clipboard.writeText(document.document_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        background: '#0f172a',
        border: '1px solid rgba(148, 163, 184, 0.08)',
        borderRadius: '12px',
        padding: '18px',
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '14px',
        transition: 'all 0.2s ease',
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.border = '1px solid rgba(99, 102, 241, 0.12)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 24px rgba(0,0,0,0.2)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.border = '1px solid rgba(148, 163, 184, 0.08)';
        (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
      }}
    >
      {/* Top: icon + name + delete */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-3 truncate">
          <div
            className="h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.12)',
            }}
          >
            <FileText className="h-4 w-4" style={{ color: '#818cf8' }} />
          </div>
          <div className="truncate min-w-0">
            <h3
              className="text-sm font-semibold truncate"
              style={{ color: '#e2e8f0', letterSpacing: '-0.01em' }}
              title={document.filename}
            >
              {document.filename}
            </h3>
            <span
              className="text-xs"
              style={{ color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}
            >
              {formatBytes(document.size_bytes)}
            </span>
          </div>
        </div>
        <button
          onClick={() => onRemove(document.document_id)}
          className="cursor-pointer flex-shrink-0"
          style={{
            padding: '5px',
            borderRadius: '6px',
            background: 'transparent',
            border: 'none',
            color: 'rgba(148, 163, 184, 0.25)',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = '#fb7185';
            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(244, 63, 94, 0.06)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.25)';
            (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
          }}
          title="Remove document"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Meta row */}
      <div
        className="grid grid-cols-2 gap-y-2 text-xs"
        style={{
          paddingTop: '12px',
          borderTop: '1px solid rgba(148, 163, 184, 0.05)',
        }}
      >
        <span style={{ color: 'rgba(148, 163, 184, 0.35)' }}>Status</span>
        <div className="text-right">
          <DocumentStatus status={document.status} />
        </div>
        <span style={{ color: 'rgba(148, 163, 184, 0.35)' }}>Indexed</span>
        <span className="text-right" style={{ color: 'rgba(148, 163, 184, 0.6)', fontFamily: "'JetBrains Mono', monospace" }}>
          {formatDate(document.created_at)}
        </span>
      </div>

      {/* ID row */}
      <div
        className="flex items-center justify-between gap-2"
        style={{
          padding: '7px 10px',
          borderRadius: '6px',
          background: 'rgba(10, 15, 26, 0.6)',
          border: '1px solid rgba(148, 163, 184, 0.05)',
        }}
      >
        <span
          className="text-[10px] truncate"
          style={{ color: 'rgba(148, 163, 184, 0.3)', fontFamily: "'JetBrains Mono', monospace" }}
        >
          {document.document_id}
        </span>
        <button
          onClick={handleCopyId}
          className="cursor-pointer flex-shrink-0"
          style={{
            background: 'none',
            border: 'none',
            color: 'rgba(148, 163, 184, 0.3)',
            transition: 'color 0.15s ease',
            padding: '2px',
          }}
          title="Copy ID"
          onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = '#818cf8'; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.3)'; }}
        >
          {copied ? <Check className="h-3 w-3" style={{ color: '#34d399' }} /> : <Copy className="h-3 w-3" />}
        </button>
      </div>
    </div>
  );
};
export default DocumentCard;
