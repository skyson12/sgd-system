import { API_BASE_URL } from './config';

interface LoginResponse {
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
    isActive: boolean;
  };
}

export class AuthService {
  static async login(email: string, password: string): Promise<LoginResponse> {
    try {
      // In a real implementation, this would authenticate with Keycloak
      // For demo purposes, we'll simulate a login
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      throw new Error('Authentication failed');
    }
  }

  static async getCurrentUser(token: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get user info');
      }

      return await response.json();
    } catch (error) {
      throw error;
    }
  }

  static async logout() {
    // In a real implementation, this might call Keycloak logout
    localStorage.removeItem('sgd_token');
  }
}