import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
  is_active: boolean;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  confirm_password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
  confirm_new_password: string;
}

export interface GoogleRegisterData {
  password: string;
  confirm_password: string;
  registration_token: string;
}

class AuthService {
  private tokenKey = 'auth_token';
  private refreshTokenKey = 'refresh_token';

  constructor() {
    this.bindInterceptor(axios);
  }

  bindInterceptor(instance: any) {
    instance.interceptors.response.use(
      (response: any) => response,
      async (error: any) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const token = await this.refreshToken();
            instance.defaults.headers.common['Authorization'] = 'Bearer ' + token.access_token;
            originalRequest.headers['Authorization'] = 'Bearer ' + token.access_token;
            return instance(originalRequest);
          } catch (refreshError) {
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async register(data: RegisterData): Promise<{ user: User; token: Token }> {
    const response = await axios.post(`${API_URL}/auth/register`, data);
    if (response.data.token) {
      this.setToken(response.data.token);
    }
    return response.data;
  }

  async login(data: LoginData): Promise<Token> {
    const response = await axios.post(`${API_URL}/auth/login`, data);
    this.setToken(response.data);
    return response.data;
  }

  async refreshToken(): Promise<Token> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token found');
    }
    const response = await axios.post(`${API_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    this.setToken(response.data);
    return response.data;
  }

  async completeGoogleRegister(data: GoogleRegisterData): Promise<void> {
    const response = await axios.post(`${API_URL}/auth/google/complete-register`, data);
    this.setToken(response.data);
  }

  async changePassword(data: ChangePasswordData): Promise<void> {
    const token = this.getToken();
    if (!token) {
      throw new Error('No token found');
    }
    await axios.post(`${API_URL}/auth/change-password`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
  }

  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    if (!token) {
      throw new Error('No token found');
    }
    const response = await axios.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }



  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey);
  }

  private listeners: (() => void)[] = [];

  subscribe(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener());
  }

  setToken(token: Token): void {
    localStorage.setItem(this.tokenKey, token.access_token);
    localStorage.setItem(this.refreshTokenKey, token.refresh_token);
    this.notifyListeners();
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    this.notifyListeners();
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
