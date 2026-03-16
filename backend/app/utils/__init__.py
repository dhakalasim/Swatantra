from datetime import datetime
from typing import Dict, Any, List
import uuid
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def calculate_execution_time(start_dt: datetime, end_dt: datetime = None) -> float:
    """Calculate execution time in seconds"""
    if end_dt is None:
        end_dt = datetime.utcnow()
    delta = end_dt - start_dt
    return delta.total_seconds()


def paginate_query(query, page: int = 1, page_size: int = 20):
    """Paginate SQLAlchemy query"""
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


def get_agent_analytics(db: Session) -> Dict[str, Any]:
    """Calculate agent analytics from database"""
    from app.models import Agent, Task, TaskStatusEnum
    
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.is_active == True).count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatusEnum.COMPLETED).count()
    failed_tasks = db.query(Task).filter(Task.status == TaskStatusEnum.FAILED).count()
    
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate average execution time
    executed_tasks = db.query(Task).filter(Task.execution_time_seconds.isnot(None))
    avg_execution_time = None
    
    if executed_tasks.count() > 0:
        total_time = sum(t.execution_time_seconds for t in executed_tasks)
        avg_execution_time = total_time / executed_tasks.count()
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "success_rate": round(success_rate, 2),
        "avg_execution_time": avg_execution_time,
        "timestamp": datetime.utcnow(),
    }


def validate_task_input(input_data: Dict[str, Any]) -> bool:
    """Validate task input data"""
    required_fields = ["objective"]
    return all(field in input_data for field in required_fields)


def format_error_response(error: Exception) -> Dict[str, Any]:
    """Format exception as API response"""
    logger.error(f"Error: {str(error)}", exc_info=True)
    return {
        "status": "error",
        "message": str(error),
        "error_type": type(error).__name__,
    }


def merge_dicts(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in updates.items():
        if isinstance(value, dict) and key in result:
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
