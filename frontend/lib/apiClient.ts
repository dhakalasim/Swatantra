import axios, { AxiosInstance } from 'axios';
import { Agent, Task, HealthStatus, ApiResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health endpoints
  async getHealth(): Promise<HealthStatus> {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  // Agent endpoints
  async getAgents(): Promise<Agent[]> {
    const response = await this.client.get('/api/agents');
    return response.data;
  }

  async getAgent(id: number): Promise<Agent> {
    const response = await this.client.get(`/api/agents/${id}`);
    return response.data;
  }

  async createAgent(agent: Omit<Agent, 'id'>): Promise<Agent> {
    const response = await this.client.post('/api/agents', agent);
    return response.data;
  }

  async updateAgent(id: number, agent: Partial<Agent>): Promise<Agent> {
    const response = await this.client.put(`/api/agents/${id}`, agent);
    return response.data;
  }

  async deleteAgent(id: number): Promise<void> {
    await this.client.delete(`/api/agents/${id}`);
  }

  async activateAgent(id: number): Promise<void> {
    await this.client.post(`/api/agents/${id}/activate`);
  }

  async deactivateAgent(id: number): Promise<void> {
    await this.client.post(`/api/agents/${id}/deactivate`);
  }

  // Task endpoints
  async getTasks(agentId?: number): Promise<Task[]> {
    const params = agentId ? { agent_id: agentId } : {};
    const response = await this.client.get('/api/tasks', { params });
    return response.data;
  }

  async getTask(id: number): Promise<Task> {
    const response = await this.client.get(`/api/tasks/${id}`);
    return response.data;
  }

  async createTask(task: Omit<Task, 'id'>): Promise<Task> {
    const response = await this.client.post('/api/tasks', task);
    return response.data;
  }

  async updateTask(id: number, task: Partial<Task>): Promise<Task> {
    const response = await this.client.put(`/api/tasks/${id}`, task);
    return response.data;
  }

  async deleteTask(id: number): Promise<void> {
    await this.client.delete(`/api/tasks/${id}`);
  }

  async executeTask(id: number): Promise<Task> {
    const response = await this.client.post(`/api/tasks/${id}/execute`);
    return response.data;
  }

  async cancelTask(id: number): Promise<void> {
    await this.client.post(`/api/tasks/${id}/cancel`);
  }

  // Analytics endpoints
  async getAnalyticsSummary(): Promise<any> {
    const response = await this.client.get('/api/analytics/summary');
    return response.data;
  }

  async getAnalyticsHistory(): Promise<any> {
    const response = await this.client.get('/api/analytics/history');
    return response.data;
  }

  async getAgentPerformance(): Promise<any> {
    const response = await this.client.get('/api/analytics/agents/performance');
    return response.data;
  }

  // Sync endpoints
  async getSyncStatus(): Promise<any> {
    const response = await this.client.get('/api/sync-status');
    return response.data;
  }

  async syncNow(): Promise<any> {
    const response = await this.client.post('/api/sync-now');
    return response.data;
  }
}

export const apiClient = new ApiClient();
