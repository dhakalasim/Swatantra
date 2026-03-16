from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from app.config import settings
from app.db import db
from app.agents import get_orchestrator, get_default_tools
from app.routes import agents, tasks, analytics, health

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI System for autonomous task execution and planning",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.APP_NAME}...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database Type: {settings.DB_TYPE.value}")
    logger.info(f"Mode: {'Offline' if settings.is_offline_mode() else 'Online'}")
    
    # Create database tables
    try:
        db.create_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Initialize agent orchestrator with tools
    try:
        orchestrator = get_orchestrator()
        default_tools = get_default_tools()
        orchestrator.register_tools_batch(default_tools)
        logger.info(f"Agent orchestrator initialized with {len(default_tools)} tools")
    except Exception as e:
        logger.error(f"Failed to initialize agent orchestrator: {e}")
    
    logger.info(f"{settings.APP_NAME} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}...")


# Include route modules
app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(analytics.router)
app.include_router(health.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "mode": "offline" if settings.is_offline_mode() else "online",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/version")
def get_version():
    """Get API version"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "api_version": "v1",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
