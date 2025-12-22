import type { User, Task, LoginResponse, RegisterData, TaskCreate, TaskUpdate, TaskFilters } from './types';

const API_BASE = 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    let message = text;
    try {
      const json = JSON.parse(text);
      message = json.detail || json.message || text;
    } catch {
      // Keep text message
    }
    throw new ApiError(response.status, message);
  }
  return response.json();
}

export const api = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    return handleResponse<LoginResponse>(response);
  },

  async register(data: RegisterData): Promise<User> {
    const response = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    return handleResponse<User>(response);
  },

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE}/me`, {
      headers: getAuthHeaders(),
    });

    return handleResponse<User>(response);
  },

  async getTasks(filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, String(value));
        }
      });
    }

    const url = `${API_BASE}/tasks${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  async getMyTasks(filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, String(value));
        }
      });
    }

    const url = `${API_BASE}/my-tasks${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    });

    return handleResponse<Task[]>(response);
  },

  async createTask(data: TaskCreate): Promise<Task> {
    const response = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<Task>(response);
  },

  async updateTask(id: number, data: TaskUpdate): Promise<Task> {
    const response = await fetch(`${API_BASE}/task/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse<Task>(response);
  },

  async deleteTask(id: number): Promise<void> {
    const response = await fetch(`${API_BASE}/task/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const text = await response.text();
      let message = text;
      try {
        const json = JSON.parse(text);
        message = json.detail || json.message || text;
      } catch {
        // Keep text message
      }
      throw new ApiError(response.status, message);
    }
  },

  async getUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE}/users`, {
      headers: getAuthHeaders(),
    });

    return handleResponse<User[]>(response);
  },
};

export { ApiError };
