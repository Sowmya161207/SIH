import { useState, useEffect, useRef } from 'react';
import { DocumentResponse } from '../types/documents';
import { uploadDocument, uploadText, getDocumentStatus, listDocuments } from '../services/api/documents';
import { getToken } from '../services/api/auth';

export const useDocuments = () => {
  const [documents, setDocuments] = useState<DocumentResponse[]>(() => {
    const saved = localStorage.getItem('sovereign_documents');
    return saved ? JSON.parse(saved) : [];
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  const [isUploadingText, setIsUploadingText] = useState(false);
  const [uploadTextError, setUploadTextError] = useState<string | null>(null);
  const [uploadTextSuccess, setUploadTextSuccess] = useState(false);

  // Sync to local storage
  useEffect(() => {
    localStorage.setItem('sovereign_documents', JSON.stringify(documents));
  }, [documents]);

  // On mount: fetch real document list from backend and merge with local state
  useEffect(() => {
    const token = getToken();
    if (!token) return; // not authenticated yet

    listDocuments().then((serverDocs) => {
      if (!serverDocs || serverDocs.length === 0) return;
      setDocuments((prev) => {
        // Keep local-only mock documents (txt- prefix), merge real ones from server
        const localOnlyDocs = prev.filter((d) => d.document_id.startsWith('txt-'));
        // Merge: server is authoritative for status/chunks
        const merged = [...serverDocs, ...localOnlyDocs];
        return merged;
      });
    });
  }, []);

  const activePolls = useRef<{ [id: string]: boolean }>({});

  const pollDocumentStatus = (documentId: string) => {
    // Skip mock text-ingestion IDs — they don't have a backend record
    if (documentId.startsWith('txt-')) return;
    if (activePolls.current[documentId]) return;
    activePolls.current[documentId] = true;

    const interval = setInterval(async () => {
      try {
        const doc = await getDocumentStatus(documentId);
        setDocuments((prevDocs) =>
          prevDocs.map((d) => (d.document_id === documentId ? doc : d))
        );

        if (doc.status === 'completed' || doc.status === 'failed' || doc.status === 'ready') {
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

  const submitText = async (title: string, text: string) => {
    setIsUploadingText(true);
    setUploadTextError(null);
    setUploadTextSuccess(false);

    try {
      const doc = await uploadText(title, text);
      setDocuments((prevDocs) => [doc, ...prevDocs]);
      setUploadTextSuccess(true);

      // Mock processing to simulate backend delay for mock responses
      if (doc.document_id.startsWith('txt-')) {
        setTimeout(() => {
          setDocuments((prevDocs) =>
            prevDocs.map((d) =>
              d.document_id === doc.document_id ? { ...d, status: 'completed' } : d
            )
          );
        }, 5000);
      } else {
        if (doc.status === 'uploaded' || doc.status === 'processing') {
          pollDocumentStatus(doc.document_id);
        }
      }
      return doc;
    } catch (error: any) {
      setUploadTextError(error.message || 'Text submission failed');
      throw error;
    } finally {
      setIsUploadingText(false);
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
    isUploadingText,
    uploadTextError,
    uploadTextSuccess,
    submitText,
    removeDocument,
    clearUploadState: () => {
      setUploadError(null);
      setUploadSuccess(false);
    },
    clearUploadTextState: () => {
      setUploadTextError(null);
      setUploadTextSuccess(false);
    },
  };
};
