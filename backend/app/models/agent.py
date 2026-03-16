from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AgentStatusEnum(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(100), default="reasoning")  # reasoning, planning, execution
    status = Column(SQLEnum(AgentStatusEnum), default=AgentStatusEnum.IDLE)
    configuration = Column(JSON, nullable=True)  # Stores agent-specific config
    tools = Column(JSON, nullable=True)  # Array of tool definitions
    memory = Column(JSON, nullable=True)  # Agent memory/context
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    objective = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    priority = Column(Integer, default=0)
    input_data = Column(JSON, nullable=True)
    expected_output = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    executions = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    execution_number = Column(Integer, nullable=False)
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.IN_PROGRESS)
    input_prompt = Column(Text, nullable=True)
    reasoning_steps = Column(JSON, nullable=True)  # Array of reasoning steps
    actions_taken = Column(JSON, nullable=True)  # Array of actions
    output = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    execution_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="executions")


class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    action_type = Column(String(100), nullable=False)  # e.g., "tool_call", "reasoning"
    action_description = Column(Text, nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(SQLEnum(TaskStatusEnum), default=TaskStatusEnum.IN_PROGRESS)
    execution_time_ms = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="executions")


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    total_agents = Column(Integer, default=0)
    active_agents = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    avg_execution_time = Column(Float, nullable=True)
    total_tokens_used = Column(Integer, default=0)
    metrics = Column(JSON, nullable=True)  # Additional custom metrics
