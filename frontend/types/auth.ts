// types/auth.ts
export interface User {
  id: number;
  email: string;
  isActive: boolean;
  isVerified: boolean;
  role: string;
  createdAt: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  user: User;
}

export interface LoginForm {
  email: string;
  password: string;
}