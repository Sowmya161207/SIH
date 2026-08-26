import React from 'react';
import { DocumentResponse } from '../../types/documents';
import DocumentCard from './DocumentCard';
import { Database } from 'lucide-react';

interface DocumentListProps {
  documents: DocumentResponse[];
  onRemove: (id: string) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, onRemove }) => {
  if (documents.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center text-center"
        style={{
          minHeight: '200px',
          borderRadius: '12px',
          border: '1px dashed rgba(148, 163, 184, 0.08)',
          background: 'rgba(10, 15, 26, 0.3)',
          padding: '48px 24px',
        }}
      >
        <div
          className="h-12 w-12 rounded-xl flex items-center justify-center mb-4"
          style={{ background: 'rgba(148, 163, 184, 0.04)', border: '1px solid rgba(148, 163, 184, 0.06)' }}
        >
          <Database className="h-5 w-5" style={{ color: 'rgba(148, 163, 184, 0.2)' }} />
        </div>
        <p className="font-semibold text-sm" style={{ color: 'rgba(148, 163, 184, 0.4)' }}>
          No documents indexed
        </p>
        <p className="text-xs mt-1.5 max-w-xs" style={{ color: 'rgba(148, 163, 184, 0.25)' }}>
          Upload files using the panel above to begin indexing your knowledge base.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map((doc) => (
        <DocumentCard key={doc.document_id} document={doc} onRemove={onRemove} />
      ))}
    </div>
  );
};
export default DocumentList;
