export interface User {
  id: number;
  username: string;
  role: 'user' | 'admin';
  created_at: string;
}

export interface Task {
  id: number;
  name: string;
  status: 'pending' | 'in progress' | 'completed';
  created_at: string;
  owner_id: number;
  owner?: User;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterData {
  username: string;
  password: string;
  role?: 'user' | 'admin';
}

export interface TaskCreate {
  name: string;
  status: 'pending' | 'in progress' | 'completed';
}

export interface TaskUpdate {
  name?: string;
  status?: 'pending' | 'in progress' | 'completed';
}

export interface TaskFilters {
  limit?: number;
  offset?: number;
  status?: 'pending' | 'in progress' | 'completed';
  starts_with?: string;
  sort_by?: 'asc' | 'desc';
}
