export interface Workspace {
    id: string;
    name: string;
    description?: string;
    role: 'owner' | 'admin' | 'editor' | 'viewer';
    category?: string;
    members_count: number;
    created_at: string;
    updated_at: string;
}

export interface CreateWorkspaceRequest {
    name: string;
    description?: string;
}
