from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import asyncio
import logging

from app.db import get_db
from app.models import Task, Agent, TaskStatusEnum, AgentExecution
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.agents import get_orchestrator
from app.utils import paginate_query, calculate_execution_time
from app.db import get_offline_sync_manager
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


async def execute_task_background(task_id: int, db_url: str):
    """Background task execution"""
    # This would run the actual agent task
    pass


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status: str = Query(None),
    agent_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all tasks with filtering"""
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    
    if agent_id:
        query = query.filter(Task.agent_id == agent_id)
    
    result = paginate_query(query, page=(skip // limit) + 1, page_size=limit)
    return result["items"]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_task = Task(
        agent_id=task.agent_id,
        title=task.title,
        description=task.description,
        objective=task.objective,
        priority=task.priority,
        input_data=task.input_data,
        expected_output=task.expected_output,
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Track in offline sync if using SQLite
    if settings.DB_TYPE.value == "sqlite":
        sync_manager = get_offline_sync_manager(settings.SQLITE_DB_PATH)
        sync_manager.add_to_sync_queue("insert", "tasks", db_task.id, db_task.__dict__)
    
    logger.info(f"Created task: {task.title} for agent: {agent.name}")
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
):
    """Update a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    if "status" in update_data:
        if update_data["status"] == TaskStatusEnum.IN_PROGRESS:
            task.started_at = datetime.utcnow()
        elif update_data["status"] in [TaskStatusEnum.COMPLETED, TaskStatusEnum.FAILED]:
            task.completed_at = datetime.utcnow()
            if task.started_at:
                task.execution_time_seconds = calculate_execution_time(task.started_at)
    
    db.commit()
    db.refresh(task)
    
    # Track in offline sync if using SQLite
    if settings.DB_TYPE.value == "sqlite":
        sync_manager = get_offline_sync_manager(settings.SQLITE_DB_PATH)
        sync_manager.add_to_sync_queue("update", "tasks", task_id, task.__dict__)
    
    logger.info(f"Updated task: {task.title}")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Track in offline sync if using SQLite
    if settings.DB_TYPE.value == "sqlite":
        sync_manager = get_offline_sync_manager(settings.SQLITE_DB_PATH)
        sync_manager.add_to_sync_queue("delete", "tasks", task_id)
    
    db.delete(task)
    db.commit()
    
    logger.info(f"Deleted task: {task.title}")
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/execute")
async def execute_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Execute a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update task status
    task.status = TaskStatusEnum.IN_PROGRESS
    task.started_at = datetime.utcnow()
    db.commit()
    
    # Get orchestrator and execute
    orchestrator = get_orchestrator()
    
    try:
        result = await orchestrator.execute_agent_task(
            task_objective=task.objective,
            agent_name=agent.name,
            tool_names=agent.tools if agent.tools else None,
            input_data=task.input_data,
        )
        
        # Update task with results
        task.status = TaskStatusEnum.COMPLETED if result["status"] == "completed" else TaskStatusEnum.FAILED
        task.result = result
        task.completed_at = datetime.utcnow()
        task.execution_time_seconds = calculate_execution_time(task.started_at)
        
        if result.get("error"):
            task.error_message = result.get("error")
        
    except Exception as e:
        task.status = TaskStatusEnum.FAILED
        task.error_message = str(e)
        task.completed_at = datetime.utcnow()
        task.execution_time_seconds = calculate_execution_time(task.started_at)
        logger.error(f"Task execution failed: {str(e)}")
    
    db.commit()
    db.refresh(task)
    
    # Track in offline sync
    if settings.DB_TYPE.value == "sqlite":
        sync_manager = get_offline_sync_manager(settings.SQLITE_DB_PATH)
        sync_manager.add_to_sync_queue("update", "tasks", task_id, task.__dict__)
    
    return task


@router.post("/{task_id}/cancel")
def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """Cancel a running task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS]:
        raise HTTPException(status_code=400, detail="Can only cancel pending or in-progress tasks")
    
    task.status = TaskStatusEnum.CANCELLED
    task.completed_at = datetime.utcnow()
    if task.started_at:
        task.execution_time_seconds = calculate_execution_time(task.started_at)
    
    db.commit()
    
    return {"message": "Task cancelled successfully"}
