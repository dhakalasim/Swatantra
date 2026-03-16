from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from pathlib import Path
from app.config import settings
from app.models import Base


class DatabaseManager:
    """Manages database connections for both PostgreSQL and SQLite"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database engine based on configuration"""
        db_url = settings.database_url
        
        # Ensure SQLite directory exists
        if settings.DB_TYPE.value == "sqlite":
            db_path = Path(settings.SQLITE_DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine with appropriate settings
        if settings.DB_TYPE.value == "postgresql":
            self.engine = create_engine(
                db_url,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                echo=settings.DEBUG,
            )
        else:  # SQLite
            self.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                echo=settings.DEBUG,
            )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables from the database (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_db(self) -> Session:
        """Get a database session"""
        db = self.SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations"""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.session_scope() as db:
                db.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False


# Initialize database manager
db = DatabaseManager()


# Dependency for FastAPI
def get_db() -> Session:
    """FastAPI dependency to get database session"""
    database_session = db.get_db()
    try:
        yield database_session
    finally:
        database_session.close()
