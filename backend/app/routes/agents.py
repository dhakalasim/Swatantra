from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.db import get_db
from app.models import Agent, Task, TaskStatusEnum
from app.schemas import AgentCreate, AgentUpdate, AgentResponse, TaskResponse
from app.utils import paginate_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    """List all agents with pagination"""
    query = db.query(Agent)
    
    if active_only:
        query = query.filter(Agent.is_active == True)
    
    result = paginate_query(query, page=(skip // limit) + 1, page_size=limit)
    return result["items"]


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get specific agent by ID"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent


@router.post("", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent"""
    # Check if agent with same name exists
    existing = db.query(Agent).filter(Agent.name == agent.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Agent with this name already exists")
    
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        configuration=agent.configuration,
        tools=agent.tools,
    )
    
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    logger.info(f"Created agent: {agent.name}")
    return db_agent


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    db: Session = Depends(get_db),
):
    """Update an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    db.commit()
    db.refresh(agent)
    
    logger.info(f"Updated agent: {agent.name}")
    return agent


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    
    logger.info(f"Deleted agent: {agent.name}")
    return {"message": "Agent deleted successfully"}


@router.get("/{agent_id}/tasks", response_model=List[TaskResponse])
def get_agent_tasks(
    agent_id: int,
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all tasks for a specific agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    query = db.query(Task).filter(Task.agent_id == agent_id)
    
    if status:
        query = query.filter(Task.status == status)
    
    result = paginate_query(query, page=(skip // limit) + 1, page_size=limit)
    return result["items"]


@router.post("/{agent_id}/activate")
def activate_agent(agent_id: int, db: Session = Depends(get_db)):
    """Activate an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_active = True
    db.commit()
    
    return {"message": f"Agent {agent.name} activated"}


@router.post("/{agent_id}/deactivate")
def deactivate_agent(agent_id: int, db: Session = Depends(get_db)):
    """Deactivate an agent"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_active = False
    db.commit()
    
    return {"message": f"Agent {agent.name} deactivated"}
