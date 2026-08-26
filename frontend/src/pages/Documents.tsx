import React from 'react';
import { UploadZone } from '../components/documents/UploadZone';
import { TextInputZone } from '../components/documents/TextInputZone';
import { DocumentList } from '../components/documents/DocumentList';
import { InlineQueryPanel } from '../components/documents/InlineQueryPanel';
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
    <div className="min-h-full animate-fadeIn">
      {/* Page header */}
      <div
        className="relative overflow-hidden"
        style={{
          background: 'linear-gradient(180deg, #0a0f1a 0%, #080c15 100%)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
          padding: '32px 48px 28px',
        }}
      >
        <div
          className="absolute inset-0 bg-grid opacity-40"
          style={{ pointerEvents: 'none' }}
        />
        <div className="relative">
          <h1
            style={{
              fontSize: '22px',
              fontWeight: 800,
              color: '#f1f5f9',
              letterSpacing: '-0.025em',
            }}
          >
            Knowledge Base
          </h1>
          <p
            className="mt-1.5"
            style={{ fontSize: '13px', color: 'rgba(148, 163, 184, 0.5)', lineHeight: 1.5 }}
          >
            Index organizational documents for secure AI-powered retrieval.
          </p>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '32px 48px', maxWidth: '1280px' }}>

        {/* Upload zone + Text input */}
        <div className="grid grid-cols-2 gap-5 mb-10">
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

        {/* Document library */}
        <div>
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <span
                style={{
                  fontSize: '9px',
                  fontWeight: 700,
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  color: 'rgba(148, 163, 184, 0.35)',
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                Indexed Files
              </span>
              <div
                style={{ height: '1px', width: '60px', background: 'rgba(148, 163, 184, 0.06)' }}
              />
            </div>
            <div
              style={{
                padding: '3px 10px',
                borderRadius: '4px',
                background: 'rgba(148, 163, 184, 0.04)',
                border: '1px solid rgba(148, 163, 184, 0.08)',
                fontSize: '10px',
                color: 'rgba(148, 163, 184, 0.4)',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              {documents.length} files
            </div>
          </div>
          <DocumentList documents={documents} onRemove={removeDocument} />
        </div>

        {/* ── Inline Query Panel — below the file list ── */}
        <div className="mt-8">
          <InlineQueryPanel />
        </div>

      </div>
    </div>
  );
};
export default Documents;
