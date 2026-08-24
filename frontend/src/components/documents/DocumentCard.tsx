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
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const handleCopyId = () => {
    navigator.clipboard.writeText(document.document_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-5 hover:border-slate-700 transition-all duration-300 shadow-md flex flex-col justify-between h-[210px]">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3 truncate">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <FileText className="h-5 w-5" />
          </div>
          <div className="truncate">
            <h3 className="text-sm font-semibold text-slate-200 truncate" title={document.filename}>
              {document.filename}
            </h3>
            <span className="text-xs text-slate-500 font-mono">
              {formatBytes(document.size_bytes)}
            </span>
          </div>
        </div>
        <button
          onClick={() => onRemove(document.document_id)}
          className="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-rose-500/10 transition-colors cursor-pointer"
          title="Remove document from session"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      <div className="grid grid-cols-2 gap-y-2 py-4 my-2 border-y border-[#1e293b] text-xs">
        <span className="text-slate-500">Status</span>
        <div className="text-right">
          <DocumentStatus status={document.status} />
        </div>
        
        <span className="text-slate-500">Uploaded</span>
        <span className="text-right text-slate-300 font-medium">{formatDate(document.created_at)}</span>
      </div>

      <div className="flex items-center justify-between text-[11px] font-mono bg-[#090d16] px-3 py-1.5 rounded-lg border border-[#1e293b]/40">
        <span className="text-slate-500 select-all truncate mr-2">
          ID: {document.document_id}
        </span>
        <button
          onClick={handleCopyId}
          className="text-slate-400 hover:text-indigo-400 p-1 rounded transition-colors flex-shrink-0 cursor-pointer"
          title="Copy Document ID"
        >
          {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
        </button>
      </div>
    </div>
  );
};
export default DocumentCard;
