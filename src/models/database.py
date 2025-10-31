"""
Database configuration and connection management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL - supports SQLite and PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./vds_data.db"  # Default to SQLite for simplicity
)

# For PostgreSQL compatibility with SQLAlchemy 2.0
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Connection pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # Recycle connections after 1 hour

# Create engine with connection pooling
if "sqlite" in DATABASE_URL:
    # SQLite doesn't support connection pooling
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True,
    )
else:
    # PostgreSQL and other databases with connection pooling
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True,  # Verify connections before using
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT,
        pool_recycle=POOL_RECYCLE,
    )
    logger.info(f"Database connection pool configured: size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session

    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from . import analysis  # noqa

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
