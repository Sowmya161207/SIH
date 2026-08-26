import axios from 'axios';
import { API_BASE_URL } from '../../config/api';

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResult {
  access_token: string;
  token_type: string;
  user: {
    username: string;
    role: string;
  };
}

/** POST /api/auth/login */
export const loginApi = async (payload: LoginPayload): Promise<LoginResult> => {
  const response = await axios.post<LoginResult>(
    `${API_BASE_URL}/api/auth/login`,
    payload,
    { headers: { 'Content-Type': 'application/json' } }
  );
  return response.data;
};

// ─── Token helpers (stored in localStorage) ──────────────────────────────────

const TOKEN_KEY = 'sovereign_access_token';
const ROLE_KEY = 'sovereign_user_role';
const USERNAME_KEY = 'sovereign_username';

export const saveSession = (token: string, role: string, username: string) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(ROLE_KEY, role);
  localStorage.setItem(USERNAME_KEY, username);
};

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);
export const getSavedRole = (): string | null => localStorage.getItem(ROLE_KEY);
export const getSavedUsername = (): string | null => localStorage.getItem(USERNAME_KEY);

export const clearSession = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(ROLE_KEY);
  localStorage.removeItem(USERNAME_KEY);
};

export const ensureValidToken = async (): Promise<string> => {
  let token = getToken();
  if (!token) {
    try {
      const res = await loginApi({ username: 'operator', password: 'operator_demo' });
      saveSession(res.access_token, res.user.role, res.user.username);
      return res.access_token;
    } catch {
      return '';
    }
  }
  return token;
};

/** Map DB roles → UI roles ('admin' | 'employee') */
export const mapToUIRole = (dbRole: string): 'admin' | 'employee' => {
  const adminRoles = ['admin', 'supervisor', 'manager'];
  return adminRoles.includes(dbRole) ? 'admin' : 'employee';
};
