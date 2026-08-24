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
      <div className="bg-[#0f172a]/45 border border-[#1e293b] border-dashed rounded-xl p-8 text-center flex flex-col items-center justify-center min-h-[200px]">
        <Database className="h-8 w-8 text-slate-600 mb-3" />
        <p className="text-slate-400 text-sm font-medium">No documents uploaded yet</p>
        <p className="text-slate-500 text-xs mt-1">Upload PDF files to index them into the sovereign workspace.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {documents.map((doc) => (
        <DocumentCard key={doc.document_id} document={doc} onRemove={onRemove} />
      ))}
    </div>
  );
};
export default DocumentList;
