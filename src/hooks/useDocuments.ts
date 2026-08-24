import { useState, useEffect, useRef } from 'react';
import { DocumentResponse } from '../types/documents';
import { uploadDocument, getDocumentStatus } from '../services/api/documents';

export const useDocuments = () => {
  const [documents, setDocuments] = useState<DocumentResponse[]>(() => {
    const saved = localStorage.getItem('sovereign_documents');
    return saved ? JSON.parse(saved) : [];
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Sync to local storage
  useEffect(() => {
    localStorage.setItem('sovereign_documents', JSON.stringify(documents));
  }, [documents]);

  const activePolls = useRef<{ [id: string]: boolean }>({});

  const pollDocumentStatus = (documentId: string) => {
    if (activePolls.current[documentId]) return;
    activePolls.current[documentId] = true;

    const interval = setInterval(async () => {
      try {
        const doc = await getDocumentStatus(documentId);
        setDocuments((prevDocs) =>
          prevDocs.map((d) => (d.document_id === documentId ? doc : d))
        );

        if (doc.status === 'completed' || doc.status === 'failed') {
          clearInterval(interval);
          delete activePolls.current[documentId];
        }
      } catch (error) {
        console.error('Failed to poll document status:', error);
        clearInterval(interval);
        delete activePolls.current[documentId];
      }
    }, 3000);
  };

  // Poll for existing documents that are still in progress when the hook mounts
  useEffect(() => {
    documents.forEach((doc) => {
      if (doc.status === 'uploaded' || doc.status === 'processing') {
        pollDocumentStatus(doc.document_id);
      }
    });
  }, []);

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(false);

    try {
      const doc = await uploadDocument(file);
      setDocuments((prevDocs) => [doc, ...prevDocs]);
      setUploadSuccess(true);

      // Start polling for this new document
      if (doc.status === 'uploaded' || doc.status === 'processing') {
        pollDocumentStatus(doc.document_id);
      }
      return doc;
    } catch (error: any) {
      setUploadError(error.message || 'Upload failed');
      throw error;
    } finally {
      setIsUploading(false);
    }
  };

  const removeDocument = (documentId: string) => {
    setDocuments((prevDocs) => prevDocs.filter((d) => d.document_id !== documentId));
  };

  return {
    documents,
    isUploading,
    uploadError,
    uploadSuccess,
    uploadFile,
    removeDocument,
    clearUploadState: () => {
      setUploadError(null);
      setUploadSuccess(false);
    },
  };
};
