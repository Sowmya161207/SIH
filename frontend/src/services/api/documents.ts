import axios from 'axios';
import { API_BASE_URL } from '../../config/api';
import { DocumentResponse } from '../../types/documents';
import { getToken, loginApi, saveSession } from './auth';

const getAuthHeader = async () => {
  let token = getToken();
  if (!token) {
    try {
      const res = await loginApi({ username: 'operator', password: 'operator_demo' });
      saveSession(res.access_token, res.user.role, res.user.username);
      token = res.access_token;
    } catch {
      /* ignore */
    }
  }
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const listDocuments = async (): Promise<DocumentResponse[]> => {
  try {
    const headers = await getAuthHeader();
    const response = await axios.get<DocumentResponse[]>(
      `${API_BASE_URL}/api/documents`,
      { headers }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      try {
        const res = await loginApi({ username: 'operator', password: 'operator_demo' });
        saveSession(res.access_token, res.user.role, res.user.username);
        const retry = await axios.get<DocumentResponse[]>(
          `${API_BASE_URL}/api/documents`,
          { headers: { Authorization: `Bearer ${res.access_token}` } }
        );
        return retry.data;
      } catch {}
    }
    return [];
  }
};

export const uploadDocument = async (file: File): Promise<DocumentResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const headers = await getAuthHeader();
    const response = await axios.post<DocumentResponse>(
      `${API_BASE_URL}/api/documents`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...headers,
        },
      }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      try {
        const res = await loginApi({ username: 'operator', password: 'operator_demo' });
        saveSession(res.access_token, res.user.role, res.user.username);
        const retry = await axios.post<DocumentResponse>(
          `${API_BASE_URL}/api/documents`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              Authorization: `Bearer ${res.access_token}`,
            },
          }
        );
        return retry.data;
      } catch {}
    }

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
export const uploadText = async (title: string, text: string): Promise<DocumentResponse> => {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1000));

  return {
    document_id: `txt-${crypto.randomUUID()}`,
    filename: `${title.trim() || 'Untitled'}.txt`,
    status: 'processing',
    size_bytes: new Blob([text]).size,
    created_at: new Date().toISOString(),
  };
};

export const getDocumentStatus = async (documentId: string): Promise<DocumentResponse> => {
  try {
    const headers = await getAuthHeader();
    const response = await axios.get<DocumentResponse>(
      `${API_BASE_URL}/api/documents/${documentId}`,
      { headers, timeout: 10000 }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      try {
        const res = await loginApi({ username: 'operator', password: 'operator_demo' });
        saveSession(res.access_token, res.user.role, res.user.username);
        const retry = await axios.get<DocumentResponse>(
          `${API_BASE_URL}/api/documents/${documentId}`,
          { headers: { Authorization: `Bearer ${res.access_token}` }, timeout: 10000 }
        );
        return retry.data;
      } catch {}
    }
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
