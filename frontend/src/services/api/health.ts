import axios from 'axios';
import { API_BASE_URL } from '../../config/api';
import { HealthResponse } from '../../types/health';

export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await axios.get<HealthResponse>(`${API_BASE_URL}/api/health`, {
      timeout: 3000,
    });
    return response.data;
  } catch (error) {
    return { status: 'error' };
  }
};
