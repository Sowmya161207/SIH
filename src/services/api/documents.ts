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
