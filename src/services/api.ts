import { API_BASE_URL } from './config';

interface ApiRequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: any;
  headers?: Record<string, string>;
}

class ApiService {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('sgd_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('sgd_token', token);
    } else {
      localStorage.removeItem('sgd_token');
    }
  }

  private async request<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options;
    
    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    if (this.token) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${this.token}`,
      };
    }

    if (body && method !== 'GET') {
      config.body = body instanceof FormData ? body : JSON.stringify(body);
      if (!(body instanceof FormData)) {
        config.headers = {
          ...config.headers,
          'Content-Type': 'application/json',
        };
      }
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, config);

    if (!response.ok) {
      if (response.status === 401) {
        this.setToken(null);
        window.location.href = '/login';
        return Promise.reject(new Error('Unauthorized'));
      }
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }
    
    return response.text() as unknown as T;
  }

  // Document endpoints
  async getDocuments(params?: any) {
    const queryString = params ? new URLSearchParams(params).toString() : '';
    return this.request(`/documents${queryString ? `?${queryString}` : ''}`);
  }

  async getDocument(id: number) {
    return this.request(`/documents/${id}`);
  }

  async uploadDocument(formData: FormData) {
    return this.request('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async updateDocument(id: number, data: any) {
    return this.request(`/documents/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deleteDocument(id: number) {
    return this.request(`/documents/${id}`, {
      method: 'DELETE',
    });
  }

  // Search endpoints
  async searchDocuments(params: any) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/documents/search?${queryString}`);
  }

  async chatWithDocument(documentId: number, query: string) {
    return this.request(`/documents/${documentId}/chat`, {
      method: 'POST',
      body: { query },
    });
  }

  // Analytics endpoints
  async getAnalytics() {
    return this.request('/analytics/metrics');
  }

  // Categories endpoints
  async getCategories() {
    return this.request('/categories');
  }

  // Health endpoints
  async getHealth() {
    return this.request('/health');
  }

  async getDetailedHealth() {
    return this.request('/health/detailed');
  }
}

export const apiService = new ApiService(API_BASE_URL);