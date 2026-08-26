import axios from 'axios';
import { API_BASE_URL } from '../../config/api';
import { ChatRequest, ChatResponse } from '../../types/chat';
import { getToken, loginApi, saveSession } from './auth';

const getAuthHeaders = async () => {
  let token = getToken();
  if (!token) {
    try {
      const loginRes = await loginApi({ username: 'operator', password: 'operator_demo' });
      saveSession(loginRes.access_token, loginRes.user.role, loginRes.user.username);
      token = loginRes.access_token;
    } catch (e) {
      /* ignore */
    }
  }
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const sendChatMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  try {
    const headers = await getAuthHeaders();
    const response = await axios.post<ChatResponse>(
      `${API_BASE_URL}/api/chat`,
      request,
      {
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
      }
    );
    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      try {
        const loginRes = await loginApi({ username: 'operator', password: 'operator_demo' });
        saveSession(loginRes.access_token, loginRes.user.role, loginRes.user.username);
        const retryResponse = await axios.post<ChatResponse>(
          `${API_BASE_URL}/api/chat`,
          request,
          {
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${loginRes.access_token}`,
            },
          }
        );
        return retryResponse.data;
      } catch (retryErr) {
        /* proceed to error handler */
      }
    }

    let message = 'Unable to process your request. Please try again.';
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
