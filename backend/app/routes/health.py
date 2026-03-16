from fastapi import APIRouter, Depends
from datetime import datetime
import logging

from app.config import settings
from app.db import db
from app.schemas import HealthResponse
from app.agents import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check application health"""
    db_status = "healthy"
    
    # Check database connection
    try:
        if not db.health_check():
            db_status = "unhealthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        timestamp=datetime.utcnow(),
        database=db_status,
        mode="offline" if settings.is_offline_mode() else "online",
    )


@router.get("/metrics/available-tools")
def get_available_tools():
    """Get available tools for agents"""
    orchestrator = get_orchestrator()
    tools = orchestrator.get_available_tools_info()
    
    return {
        "count": len(tools),
        "tools": tools,
    }


@router.get("/sync-status")
def get_sync_status():
    """Get offline sync status"""
    if settings.DB_TYPE.value != "sqlite":
        return {
            "mode": "online",
            "message": "Not in offline mode",
        }
    
    from app.db import get_offline_sync_manager
    
    sync_manager = get_offline_sync_manager(settings.SQLITE_DB_PATH)
    sync_status = sync_manager.get_sync_status()
    
    return {
        "mode": "offline",
        **sync_status,
    }


@router.post("/sync-now")
async def sync_now_endpoint():
    """Trigger manual sync from offline to cloud"""
    if settings.DB_TYPE.value != "sqlite":
        return {
            "status": "skipped",
            "message": "Not in offline mode",
        }
    
    from app.db import get_offline_sync_manager
    
    sync_manager = get_offline_sync_manager(settings.SQLITE_DB_PATH)
    result = await sync_manager.sync_to_cloud(
        api_endpoint=settings.API_BASE_URL,
    )
    
    return result


@router.get("/config")
def get_config():
    """Get current configuration (non-sensitive info)"""
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database_type": settings.DB_TYPE.value,
        "llm_model": settings.LLM_MODEL if not settings.USE_OFFLINE_LLM else settings.OFFLINE_LLM_MODEL,
        "mode": "offline" if settings.is_offline_mode() else "online",
        "api_base_url": settings.API_BASE_URL,
    }
