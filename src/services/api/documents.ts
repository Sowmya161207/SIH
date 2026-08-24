import axios from 'axios';
import { API_BASE_URL } from '../../config/api';
import { DocumentResponse } from '../../types/documents';

export const uploadDocument = async (file: File): Promise<DocumentResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post<DocumentResponse>(
      `${API_BASE_URL}/api/documents`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error: any) {
    let message = 'Unable to upload document. Please try again.';
    if (error.response?.data?.error?.message) {
      message = error.response.data.error.message;
    } else if (error.response?.data?.detail) {
      message = typeof error.response.data.detail === 'string' 
        ? error.response.data.detail 
        : JSON.stringify(error.response.data.detail);
    }
    throw new Error(message);
  }
};

// MOCK ADAPTER for Direct Text Ingestion
// TODO: Replace with actual axios call when the backend supports a text ingestion endpoint.
// It currently simulates a successful submission and returns a DocumentResponse to be tracked.
export const uploadText = async (title: string, text: string): Promise<DocumentResponse> => {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1000));
  
  // Return a mock DocumentResponse representing the text submission
  return {
    document_id: `txt-${crypto.randomUUID()}`,
    filename: `${title.trim() || 'Untitled'}.txt`,
    status: 'processing', // Starts in processing
    size_bytes: new Blob([text]).size,
    created_at: new Date().toISOString(),
  };
};

export const getDocumentStatus = async (documentId: string): Promise<DocumentResponse> => {
  try {
    const response = await axios.get<DocumentResponse>(
      `${API_BASE_URL}/api/documents/${documentId}`
    );
    return response.data;
  } catch (error: any) {
    let message = 'Unable to retrieve document status. Please try again.';
    if (error.response?.data?.error?.message) {
      message = error.response.data.error.message;
    } else if (error.response?.data?.detail) {
      message = typeof error.response.data.detail === 'string'
        ? error.response.data.detail
        : JSON.stringify(error.response.data.detail);
    }
    throw new Error(message);
  }
};
