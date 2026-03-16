from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Agent Schemas
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: str = Field(default="reasoning", description="Type: reasoning, planning, execution")
    configuration: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    id: int
    status: AgentStatus
    memory: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    objective: str
    priority: int = Field(default=0, ge=0, le=10)
    input_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    agent_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None


class TaskResponse(TaskBase):
    id: int
    agent_id: int
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Agent Execution Schemas
class ExecutionStep(BaseModel):
    step_number: int
    action_type: str  # reasoning, tool_call, decision
    description: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None


class AgentExecutionResponse(BaseModel):
    id: int
    agent_id: int
    execution_number: int
    status: TaskStatus
    input_prompt: Optional[str] = None
    reasoning_steps: Optional[List[ExecutionStep]] = None
    output: Optional[str] = None
    tokens_used: int
    execution_time_seconds: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsMetrics(BaseModel):
    total_agents: int
    active_agents: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    avg_execution_time: Optional[float] = None
    total_tokens_used: int
    timestamp: datetime


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Health Check Schemas
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    database: str
    mode: str  # online or offline
