"""
Analysis-related database models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .database import Base


class Analysis(Base):
    """Main analysis record"""
    __tablename__ = "analyses"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Request information
    user_id = Column(String(100), nullable=True, index=True)  # Optional user tracking
    filename = Column(String(500), nullable=False)
    user_question = Column(Text, nullable=False)

    # Execution status
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True
    )  # pending, running, completed, failed, cached

    # Selected agents
    selected_agents = Column(JSON, nullable=True)  # List of agent names

    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)  # Total execution time in milliseconds

    # Results (stored as JSON for flexibility)
    data_sample = Column(JSON, nullable=True)
    agent_results = Column(JSON, nullable=True)
    report = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)  # List of error messages

    # Cache information
    is_cached = Column(Boolean, default=False, index=True)
    cache_key = Column(String(64), nullable=True, index=True)  # SHA256 hash for caching

    # Relationships
    agent_executions = relationship("AgentExecution", back_populates="analysis", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_status_created', 'status', 'created_at'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "user_question": self.user_question,
            "status": self.status,
            "selected_agents": self.selected_agents,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time_ms": self.execution_time_ms,
            "is_cached": self.is_cached,
            "data_sample": self.data_sample,
            "agent_results": self.agent_results,
            "report": self.report,
            "errors": self.errors,
        }


class AgentExecution(Base):
    """Individual agent execution record"""
    __tablename__ = "agent_executions"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to Analysis
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    # Agent information
    agent_name = Column(String(100), nullable=False, index=True)

    # Timing
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    # Execution result
    success = Column(Boolean, nullable=False, default=False)
    code_result = Column(JSON, nullable=True)
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="agent_executions")

    # Indexes
    __table_args__ = (
        Index('idx_agent_started', 'agent_name', 'started_at'),
    )

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "agent_name": self.agent_name,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "code_result": self.code_result,
            "output": self.output,
            "error": self.error,
        }


class AgentPerformance(Base):
    """Aggregate performance metrics for each agent"""
    __tablename__ = "agent_performance"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Agent information
    agent_name = Column(String(100), nullable=False, unique=True, index=True)

    # Performance metrics
    total_runs = Column(Integer, nullable=False, default=0)
    successful_runs = Column(Integer, nullable=False, default=0)
    failed_runs = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=False, default=0.0)

    # Timing statistics
    avg_execution_time_ms = Column(Integer, nullable=True)
    min_execution_time_ms = Column(Integer, nullable=True)
    max_execution_time_ms = Column(Integer, nullable=True)

    # Metadata
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "success_rate": self.success_rate,
            "avg_execution_time_ms": self.avg_execution_time_ms,
            "min_execution_time_ms": self.min_execution_time_ms,
            "max_execution_time_ms": self.max_execution_time_ms,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class CachedAnalysis(Base):
    """Cache for analysis results to avoid redundant processing"""
    __tablename__ = "cached_analyses"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Cache key (hash of data + question)
    cache_key = Column(String(64), nullable=False, unique=True, index=True)

    # Original request
    data_hash = Column(String(64), nullable=False, index=True)  # Hash of file content
    user_question = Column(Text, nullable=False)

    # Cached result
    analysis_id = Column(String(36), nullable=False)  # Reference to original Analysis
    cached_result = Column(JSON, nullable=False)

    # Cache metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_accessed = Column(DateTime, nullable=False, default=datetime.utcnow)
    access_count = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime, nullable=True, index=True)  # Optional expiration

    # Cache statistics
    time_saved_ms = Column(Integer, nullable=False, default=0)  # Total time saved by cache hits

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "cache_key": self.cache_key,
            "data_hash": self.data_hash,
            "user_question": self.user_question,
            "analysis_id": self.analysis_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "time_saved_ms": self.time_saved_ms,
        }
