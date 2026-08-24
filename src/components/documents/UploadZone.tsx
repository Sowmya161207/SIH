import React, { useState, useRef } from 'react';
import { Upload, X, AlertTriangle, FileText, CheckCircle2, Loader2 } from 'lucide-react';

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

  const maxFileSizeBytes = 20 * 1024 * 1024; // 20 MB

  const validateFile = (file: File): boolean => {
    setValidationError(null);
    clearUploadState();

    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setValidationError('Only PDF documents are supported.');
      return false;
    }

    if (file.size === 0) {
      setValidationError('The selected file is empty.');
      return false;
    }

    if (file.size > maxFileSizeBytes) {
      setValidationError('File size exceeds the 20 MB limit.');
      return false;
    }

    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    clearUploadState();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;
    try {
      await onUpload(selectedFile);
      setSelectedFile(null); // Clear selected file upon successful upload initiating
    } catch (e) {
      // Error handled by hook state
    }
  };

  const formatBytes = (bytes: number, decimals = 1) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md max-w-2xl mx-auto">
      <h2 className="text-base font-semibold text-slate-200 mb-4">Upload PDF Document</h2>

      {/* Drag & Drop Zone */}
      {!selectedFile && (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={triggerFileInput}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 ${dragActive
              ? 'border-indigo-500 bg-indigo-500/5'
              : 'border-[#1e293b] hover:border-slate-600 bg-[#090d16]/30'
            }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,application/pdf"
            className="hidden"
          />
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="p-3 rounded-full bg-slate-800/40 text-slate-400">
              <Upload className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-300">
                Drag and drop your PDF here, or <span className="text-indigo-400 font-semibold hover:text-indigo-300">browse</span>
              </p>
              <p className="text-xs text-slate-500 mt-1.5">PDF documents up to 20 MB</p>
            </div>
          </div>
        </div>
      )}

      {/* Selected File Details */}
      {selectedFile && (
        <div className="bg-[#090d16] border border-[#1e293b] rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3 truncate">
            <div className="p-2 rounded bg-indigo-500/10 text-indigo-400">
              <FileText className="h-5 w-5" />
            </div>
            <div className="truncate">
              <p className="text-sm font-medium text-slate-300 truncate">{selectedFile.name}</p>
              <p className="text-xs text-slate-500">{formatBytes(selectedFile.size)}</p>
            </div>
          </div>
          <button
            onClick={handleRemoveFile}
            className="text-slate-500 hover:text-slate-300 p-1.5 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
            disabled={isUploading}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Validation or API Errors */}
      {(validationError || uploadError) && (
        <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-start space-x-2 text-rose-400 text-xs animate-fadeIn">
          <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">Error processing file</p>
            <p className="mt-0.5">{validationError || uploadError}</p>
          </div>
        </div>
      )}

      {/* Success Alert */}
      {uploadSuccess && (
        <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-start space-x-2 text-emerald-400 text-xs animate-fadeIn">
          <CheckCircle2 className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Upload Complete</p>
            <p className="mt-0.5">The document has been securely uploaded and is being analyzed.</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {selectedFile && (
        <div className="mt-5 flex justify-end space-x-3">
          <button
            onClick={handleRemoveFile}
            className="px-4 py-2 border border-[#1e293b] rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
            disabled={isUploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUploadSubmit}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/50 disabled:text-slate-500 rounded-lg text-xs font-semibold text-white transition-all flex items-center space-x-1.5 shadow-md shadow-indigo-600/15 cursor-pointer"
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <span>Confirm & Upload</span>
            )}
          </button>
        </div>
      )}
    </div>
  );
};
export default UploadZone;
