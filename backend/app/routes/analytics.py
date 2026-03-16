from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.db import get_db
from app.models import Agent, Task, TaskStatusEnum, AnalyticsSnapshot
from app.schemas import AnalyticsMetrics
from app.utils import get_agent_analytics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsMetrics)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Get current analytics summary"""
    analytics = get_agent_analytics(db)
    
    return AnalyticsMetrics(
        total_agents=analytics["total_agents"],
        active_agents=analytics["active_agents"],
        total_tasks=analytics["total_tasks"],
        completed_tasks=analytics["completed_tasks"],
        failed_tasks=analytics["failed_tasks"],
        success_rate=analytics["success_rate"],
        avg_execution_time=analytics["avg_execution_time"],
        total_tokens_used=0,  # Would be tracked from agent executions
        timestamp=datetime.utcnow(),
    )


@router.get("/history")
def get_analytics_history(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Get historical analytics data"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    snapshots = db.query(AnalyticsSnapshot).filter(
        AnalyticsSnapshot.timestamp >= start_date
    ).order_by(AnalyticsSnapshot.timestamp).all()
    
    return {
        "days": days,
        "snapshots": snapshots,
        "count": len(snapshots),
    }


@router.get("/agents/performance")
def get_agents_performance(db: Session = Depends(get_db)):
    """Get performance metrics for each agent"""
    agents = db.query(Agent).all()
    
    performance_data = []
    for agent in agents:
        total_tasks = db.query(Task).filter(Task.agent_id == agent.id).count()
        completed_tasks = db.query(Task).filter(
            Task.agent_id == agent.id,
            Task.status == TaskStatusEnum.COMPLETED
        ).count()
        failed_tasks = db.query(Task).filter(
            Task.agent_id == agent.id,
            Task.status == TaskStatusEnum.FAILED
        ).count()
        
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average execution time
        executed_tasks = db.query(Task).filter(
            Task.agent_id == agent.id,
            Task.execution_time_seconds.isnot(None)
        )
        
        avg_execution_time = None
        if executed_tasks.count() > 0:
            total_time = sum(t.execution_time_seconds for t in executed_tasks)
            avg_execution_time = total_time / executed_tasks.count()
        
        performance_data.append({
            "agent_id": agent.id,
            "agent_name": agent.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": round(success_rate, 2),
            "avg_execution_time": avg_execution_time,
            "status": agent.status.value,
        })
    
    return {
        "agents": performance_data,
        "count": len(performance_data),
    }


@router.get("/tasks/distribution")
def get_tasks_distribution(db: Session = Depends(get_db)):
    """Get task distribution by status"""
    total = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == TaskStatusEnum.PENDING).count()
    in_progress = db.query(Task).filter(Task.status == TaskStatusEnum.IN_PROGRESS).count()
    completed = db.query(Task).filter(Task.status == TaskStatusEnum.COMPLETED).count()
    failed = db.query(Task).filter(Task.status == TaskStatusEnum.FAILED).count()
    cancelled = db.query(Task).filter(Task.status == TaskStatusEnum.CANCELLED).count()
    
    return {
        "total": total,
        "by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
        },
        "percentages": {
            "pending": round((pending / total * 100) if total > 0 else 0, 2),
            "in_progress": round((in_progress / total * 100) if total > 0 else 0, 2),
            "completed": round((completed / total * 100) if total > 0 else 0, 2),
            "failed": round((failed / total * 100) if total > 0 else 0, 2),
            "cancelled": round((cancelled / total * 100) if total > 0 else 0, 2),
        },
    }


@router.get("/execution-timeline")
def get_execution_timeline(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Get execution events timeline"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    completed_tasks = db.query(Task).filter(
        Task.completed_at >= start_time,
        Task.status == TaskStatusEnum.COMPLETED,
    ).order_by(Task.completed_at).all()
    
    timeline = []
    for task in completed_tasks:
        timeline.append({
            "task_id": task.id,
            "task_title": task.title,
            "agent_id": task.agent_id,
            "completed_at": task.completed_at.isoformat(),
            "execution_time": task.execution_time_seconds,
        })
    
    return {
        "hours": hours,
        "event_count": len(timeline),
        "events": timeline,
    }
