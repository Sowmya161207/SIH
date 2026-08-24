import React from 'react';
import { UploadZone } from '../components/documents/UploadZone';
import { TextInputZone } from '../components/documents/TextInputZone';
import { DocumentList } from '../components/documents/DocumentList';
import { DocumentResponse } from '../types/documents';

interface DocumentsProps {
  documents: DocumentResponse[];
  uploadFile: (file: File) => Promise<any>;
  isUploading: boolean;
  uploadError: string | null;
  uploadSuccess: boolean;
  clearUploadState: () => void;
  removeDocument: (id: string) => void;
  submitText: (title: string, text: string) => Promise<any>;
  isUploadingText: boolean;
  uploadTextError: string | null;
  uploadTextSuccess: boolean;
  clearUploadTextState: () => void;
}

export const Documents: React.FC<DocumentsProps> = ({
  documents,
  uploadFile,
  isUploading,
  uploadError,
  uploadSuccess,
  clearUploadState,
  removeDocument,
  submitText,
  isUploadingText,
  uploadTextError,
  uploadTextSuccess,
  clearUploadTextState,
}) => {
  return (
    <div className="space-y-8 animate-fadeIn">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Sovereign Documents</h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage, index, and query your secure PDF archives.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        <UploadZone
          onUpload={uploadFile}
          isUploading={isUploading}
          uploadError={uploadError}
          uploadSuccess={uploadSuccess}
          clearUploadState={clearUploadState}
        />

        <TextInputZone
          onSubmitText={submitText}
          isSubmitting={isUploadingText}
          submitError={uploadTextError}
          submitSuccess={uploadTextSuccess}
          clearSubmitState={clearUploadTextState}
        />
      </div>

      <div className="pt-4 border-t border-[#1e293b]">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-slate-200">Indexed Workspace Files</h2>
          <span className="px-2.5 py-0.5 rounded bg-slate-800 border border-[#1e293b] text-xs font-mono text-slate-400">
            Total: {documents.length}
          </span>
        </div>
        <DocumentList documents={documents} onRemove={removeDocument} />
      </div>
    </div>
  );
};
export default Documents;
