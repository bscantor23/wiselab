import apiClient from '@/lib/api/client';
import { Workspace, CreateWorkspaceRequest } from '@/types/workspace';

const workspaceService = {
    getWorkspaces: async (): Promise<Workspace[]> => {
        const response = await apiClient.get<Workspace[]>('/workspaces');
        return response.data;
    },

    getWorkspace: async (id: string): Promise<Workspace> => {
        const response = await apiClient.get<Workspace>(`/workspaces/${id}`);
        return response.data;
    },

    createWorkspace: async (data: CreateWorkspaceRequest): Promise<Workspace> => {
        const response = await apiClient.post<Workspace>('/workspaces', data);
        return response.data;
    },

    updateWorkspace: async (id: string, data: Partial<CreateWorkspaceRequest>): Promise<Workspace> => {
        const response = await apiClient.put<Workspace>(`/workspaces/${id}`, data);
        return response.data;
    },

    deleteWorkspace: async (id: string): Promise<void> => {
        await apiClient.delete(`/workspaces/${id}`);
    },
};

export default workspaceService;
