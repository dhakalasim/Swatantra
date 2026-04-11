export type AgentStatus = 'Active' | 'Idle' | 'Error';
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';
export type AgentType = 'reasoning' | 'planning' | 'execution' | 'monitoring';

export interface Agent {
  id: number;
  name: string;
  role?: string;
  status?: AgentStatus;
  currentTask?: string;
  progress?: number;
  avatar?: string;
  description?: string;
  agent_type?: AgentType;
  tools?: string[] | { name: string; enabled: boolean }[];
  created_at?: string;
  updated_at?: string;
}

export interface Task {
  id: number;
  title: string;
  objective: string;
  status: TaskStatus;
  priority: number;
  agent_id?: number;
  input_data?: any;
  result?: any;
  error_message?: string;
  execution_time_seconds?: number;
  created_at?: string;
  updated_at?: string;
}

export interface Log {
  id: string;
  time: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  database: string;
  mode: 'online' | 'offline';
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}
