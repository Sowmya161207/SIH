import React, { useState, useRef } from 'react';
import { Upload, X, AlertTriangle, FileText, CheckCircle2, Loader2, CloudUpload } from 'lucide-react';

interface UploadZoneProps {
  onUpload: (file: File) => Promise<any>;
  isUploading: boolean;
  uploadError: string | null;
  uploadSuccess: boolean;
  clearUploadState: () => void;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onUpload,
  isUploading,
  uploadError,
  uploadSuccess,
  clearUploadState,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const maxFileSizeBytes = 200 * 1024 * 1024;

  const validateFile = (file: File): boolean => {
    setValidationError(null);
    clearUploadState();
    const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.ppt', '.pptx', '.txt', '.doc', '.docx', '.csv', '.md'];
    if (!allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
      setValidationError('Unsupported format. Please upload PDF, Image, PPT, TXT, or Word.');
      return false;
    }
    if (file.size === 0) { setValidationError('The selected file is empty.'); return false; }
    if (file.size > maxFileSizeBytes) { setValidationError('File exceeds 200 MB limit.'); return false; }
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file && validateFile(file)) setSelectedFile(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && validateFile(file)) setSelectedFile(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    clearUploadState();
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;
    try {
      await onUpload(selectedFile);
      setSelectedFile(null);
      setTimeout(() => {
        const queryPanel = document.getElementById('query-knowledge-base');
        if (queryPanel) {
          queryPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        const queryInput = document.getElementById('query-knowledge-base-input') as HTMLInputElement;
        if (queryInput) {
          queryInput.focus();
        }
      }, 100);
    } catch (e) { /* handled by hook */ }
  };

  const formatBytes = (bytes: number, decimals = 1) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
  };

  return (
    <div
      style={{
        background: '#0f172a',
        border: '1px solid rgba(148, 163, 184, 0.08)',
        borderRadius: '12px',
        padding: '24px',
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div
          style={{
            fontSize: '9px',
            fontWeight: 700,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'rgba(148, 163, 184, 0.4)',
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          Upload Document
        </div>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,image/png,image/jpeg,.ppt,.pptx,.txt,.doc,.docx"
        className="hidden"
      />

      {/* Drop zone */}
      {!selectedFile && (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="cursor-pointer flex flex-col items-center justify-center text-center"
          style={{
            minHeight: '140px',
            borderRadius: '10px',
            border: `1px dashed ${dragActive ? 'rgba(99, 102, 241, 0.4)' : 'rgba(148, 163, 184, 0.12)'}`,
            background: dragActive ? 'rgba(99, 102, 241, 0.04)' : 'rgba(10, 15, 26, 0.5)',
            transition: 'all 0.2s ease',
            padding: '28px 20px',
          }}
        >
          <div
            className="h-10 w-10 rounded-xl flex items-center justify-center mb-3"
            style={{
              background: dragActive ? 'rgba(99, 102, 241, 0.12)' : 'rgba(148, 163, 184, 0.05)',
              border: `1px solid ${dragActive ? 'rgba(99, 102, 241, 0.2)' : 'rgba(148, 163, 184, 0.08)'}`,
              transition: 'all 0.2s ease',
            }}
          >
            <CloudUpload
              className="h-5 w-5"
              style={{ color: dragActive ? '#818cf8' : 'rgba(148, 163, 184, 0.35)' }}
            />
          </div>
          <p style={{ fontSize: '13px', color: 'rgba(226, 232, 240, 0.7)', fontWeight: 500 }}>
            Drop file or{' '}
            <span style={{ color: '#818cf8', fontWeight: 600 }}>browse</span>
          </p>
          <p
            className="mt-1"
            style={{ fontSize: '11px', color: 'rgba(148, 163, 184, 0.35)' }}
          >
            PDF · Image · PPT · TXT · Word — up to 20 MB
          </p>
        </div>
      )}

      {/* Selected file */}
      {selectedFile && (
        <div
          className="flex items-center justify-between gap-3"
          style={{
            padding: '12px 14px',
            borderRadius: '8px',
            background: 'rgba(10, 15, 26, 0.6)',
            border: '1px solid rgba(148, 163, 184, 0.08)',
          }}
        >
          <div className="flex items-center gap-3 truncate">
            <div
              className="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.15)' }}
            >
              <FileText className="h-4 w-4" style={{ color: '#818cf8' }} />
            </div>
            <div className="truncate min-w-0">
              <p
                className="truncate text-sm font-medium"
                style={{ color: '#e2e8f0' }}
                title={selectedFile.name}
              >
                {selectedFile.name}
              </p>
              <p
                className="text-xs"
                style={{ color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}
              >
                {formatBytes(selectedFile.size)}
              </p>
            </div>
          </div>
          <button
            onClick={handleRemoveFile}
            disabled={isUploading}
            className="cursor-pointer flex-shrink-0"
            style={{
              padding: '5px',
              borderRadius: '6px',
              background: 'transparent',
              border: 'none',
              color: 'rgba(148, 163, 184, 0.3)',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.color = '#fb7185'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.3)'; }}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Errors */}
      {(validationError || uploadError) && (
        <div
          className="mt-3 flex items-start gap-2 animate-fadeIn"
          style={{
            padding: '10px 12px',
            borderRadius: '8px',
            background: 'rgba(244, 63, 94, 0.06)',
            border: '1px solid rgba(244, 63, 94, 0.12)',
          }}
        >
          <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" style={{ color: '#fb7185' }} />
          <div>
            <p className="text-xs font-semibold" style={{ color: '#fb7185' }}>Error</p>
            <p className="text-xs mt-0.5" style={{ color: 'rgba(251, 113, 133, 0.7)' }}>{validationError || uploadError}</p>
          </div>
        </div>
      )}

      {/* Success */}
      {uploadSuccess && (
        <div
          className="mt-3 flex items-start gap-2 animate-fadeIn"
          style={{
            padding: '10px 12px',
            borderRadius: '8px',
            background: 'rgba(16, 185, 129, 0.06)',
            border: '1px solid rgba(16, 185, 129, 0.12)',
          }}
        >
          <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" style={{ color: '#34d399' }} />
          <div>
            <p className="text-xs font-semibold" style={{ color: '#34d399' }}>Document uploaded and indexed successfully.</p>
            <p className="text-xs mt-0.5" style={{ color: 'rgba(52, 211, 153, 0.6)' }}>You can now ask a question.</p>
          </div>
        </div>
      )}

      {/* Actions */}
      {selectedFile && (
        <div className="mt-4 flex justify-end gap-2">
          <button
            onClick={handleRemoveFile}
            disabled={isUploading}
            className="cursor-pointer"
            style={{
              padding: '7px 14px',
              borderRadius: '7px',
              background: 'transparent',
              border: '1px solid rgba(148, 163, 184, 0.08)',
              color: 'rgba(148, 163, 184, 0.5)',
              fontSize: '12px',
              fontWeight: 500,
              transition: 'all 0.15s ease',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleUploadSubmit}
            disabled={isUploading}
            className="cursor-pointer flex items-center gap-1.5"
            style={{
              padding: '7px 16px',
              borderRadius: '7px',
              background: 'linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '12px',
              fontWeight: 600,
              boxShadow: '0 2px 12px rgba(99, 102, 241, 0.25)',
              transition: 'all 0.15s ease',
              opacity: isUploading ? 0.7 : 1,
            }}
          >
            {isUploading ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="h-3.5 w-3.5" />
                <span>Confirm & Upload</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};
export default UploadZone;
