export interface User {
    id: string;
    email: string;
    name: string;
    workspaces?: string[];
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    name: string;
    email: string;
    password: string;
    confirmPassword: string;
}

export interface AuthResponse {
    user: User;
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
}
