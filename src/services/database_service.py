"""
Database service for managing analysis records, caching, and performance tracking
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models import Analysis, AgentExecution, AgentPerformance, CachedAnalysis

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""

    @staticmethod
    def generate_data_hash(file_content: bytes) -> str:
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    @staticmethod
    def generate_cache_key(data_hash: str, user_question: str) -> str:
        """Generate cache key from data hash and question"""
        combined = f"{data_hash}:{user_question.strip().lower()}"
        return hashlib.sha256(combined.encode()).hexdigest()

    # ========== Analysis Management ==========

    def create_analysis(
        self,
        db: Session,
        filename: str,
        user_question: str,
        selected_agents: List[str],
        user_id: Optional[str] = None,
        cache_key: Optional[str] = None,
    ) -> Analysis:
        """Create a new analysis record"""
        try:
            analysis = Analysis(
                filename=filename,
                user_question=user_question,
                selected_agents=selected_agents,
                user_id=user_id,
                cache_key=cache_key,
                status="pending",
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            logger.info(f"Created analysis record: {analysis.id}")
            return analysis
        except Exception as e:
            logger.error(f"Failed to create analysis: {e}")
            db.rollback()
            raise

    def update_analysis_status(
        self, db: Session, analysis_id: str, status: str
    ) -> Optional[Analysis]:
        """Update analysis status"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = status
                if status == "running" and not analysis.started_at:
                    analysis.started_at = datetime.utcnow()
                elif status in ["completed", "failed"]:
                    analysis.completed_at = datetime.utcnow()
                    if analysis.started_at:
                        delta = analysis.completed_at - analysis.started_at
                        analysis.execution_time_ms = int(delta.total_seconds() * 1000)
                db.commit()
                db.refresh(analysis)
                return analysis
            return None
        except Exception as e:
            logger.error(f"Failed to update analysis status: {e}")
            db.rollback()
            raise

    def save_analysis_results(
        self,
        db: Session,
        analysis_id: str,
        data_sample: Dict[str, Any],
        agent_results: Dict[str, Any],
        report: Dict[str, Any],
        errors: List[str] = None,
    ) -> Optional[Analysis]:
        """Save analysis results"""
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.data_sample = data_sample
                analysis.agent_results = agent_results
                analysis.report = report
                analysis.errors = errors or []
                analysis.status = "completed" if not errors else "completed_with_errors"
                analysis.completed_at = datetime.utcnow()
                if analysis.started_at:
                    delta = analysis.completed_at - analysis.started_at
                    analysis.execution_time_ms = int(delta.total_seconds() * 1000)
                db.commit()
                db.refresh(analysis)
                logger.info(f"Saved results for analysis: {analysis_id}")
                return analysis
            return None
        except Exception as e:
            logger.error(f"Failed to save analysis results: {e}")
            db.rollback()
            raise

    def get_analysis(self, db: Session, analysis_id: str) -> Optional[Analysis]:
        """Get analysis by ID"""
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def get_recent_analyses(
        self, db: Session, limit: int = 10, user_id: Optional[str] = None
    ) -> List[Analysis]:
        """Get recent analyses"""
        query = db.query(Analysis)
        if user_id:
            query = query.filter(Analysis.user_id == user_id)
        return query.order_by(desc(Analysis.created_at)).limit(limit).all()

    def get_analyses_by_status(
        self, db: Session, status: str, limit: int = 100
    ) -> List[Analysis]:
        """Get analyses by status"""
        return (
            db.query(Analysis)
            .filter(Analysis.status == status)
            .order_by(desc(Analysis.created_at))
            .limit(limit)
            .all()
        )

    # ========== Agent Execution Tracking ==========

    def create_agent_execution(
        self, db: Session, analysis_id: str, agent_name: str
    ) -> AgentExecution:
        """Create agent execution record"""
        try:
            execution = AgentExecution(analysis_id=analysis_id, agent_name=agent_name)
            db.add(execution)
            db.commit()
            db.refresh(execution)
            return execution
        except Exception as e:
            logger.error(f"Failed to create agent execution: {e}")
            db.rollback()
            raise

    def complete_agent_execution(
        self,
        db: Session,
        execution_id: str,
        success: bool,
        code_result: Dict[str, Any] = None,
        output: str = None,
        error: str = None,
    ) -> Optional[AgentExecution]:
        """Complete agent execution with results"""
        try:
            execution = (
                db.query(AgentExecution).filter(AgentExecution.id == execution_id).first()
            )
            if execution:
                execution.completed_at = datetime.utcnow()
                execution.success = success
                execution.code_result = code_result
                execution.output = output
                execution.error = error
                delta = execution.completed_at - execution.started_at
                execution.execution_time_ms = int(delta.total_seconds() * 1000)
                db.commit()
                db.refresh(execution)

                # Update agent performance metrics
                self._update_agent_performance(
                    db, execution.agent_name, success, execution.execution_time_ms
                )

                return execution
            return None
        except Exception as e:
            logger.error(f"Failed to complete agent execution: {e}")
            db.rollback()
            raise

    def _update_agent_performance(
        self, db: Session, agent_name: str, success: bool, execution_time_ms: int
    ):
        """Update aggregate agent performance metrics"""
        try:
            perf = (
                db.query(AgentPerformance)
                .filter(AgentPerformance.agent_name == agent_name)
                .first()
            )

            if not perf:
                # Create new performance record
                perf = AgentPerformance(
                    agent_name=agent_name,
                    total_runs=1,
                    successful_runs=1 if success else 0,
                    failed_runs=0 if success else 1,
                    success_rate=1.0 if success else 0.0,
                    avg_execution_time_ms=execution_time_ms,
                    min_execution_time_ms=execution_time_ms,
                    max_execution_time_ms=execution_time_ms,
                )
                db.add(perf)
            else:
                # Update existing performance record
                perf.total_runs += 1
                if success:
                    perf.successful_runs += 1
                else:
                    perf.failed_runs += 1

                perf.success_rate = perf.successful_runs / perf.total_runs

                # Update timing statistics
                if execution_time_ms:
                    if perf.avg_execution_time_ms:
                        # Calculate new average
                        total_time = perf.avg_execution_time_ms * (perf.total_runs - 1)
                        perf.avg_execution_time_ms = int(
                            (total_time + execution_time_ms) / perf.total_runs
                        )
                    else:
                        perf.avg_execution_time_ms = execution_time_ms

                    if (
                        not perf.min_execution_time_ms
                        or execution_time_ms < perf.min_execution_time_ms
                    ):
                        perf.min_execution_time_ms = execution_time_ms

                    if (
                        not perf.max_execution_time_ms
                        or execution_time_ms > perf.max_execution_time_ms
                    ):
                        perf.max_execution_time_ms = execution_time_ms

            db.commit()
        except Exception as e:
            logger.error(f"Failed to update agent performance: {e}")
            db.rollback()

    def get_agent_performance(self, db: Session, agent_name: str) -> Optional[AgentPerformance]:
        """Get performance metrics for an agent"""
        return (
            db.query(AgentPerformance)
            .filter(AgentPerformance.agent_name == agent_name)
            .first()
        )

    def get_all_agent_performance(self, db: Session) -> List[AgentPerformance]:
        """Get performance metrics for all agents"""
        return db.query(AgentPerformance).order_by(desc(AgentPerformance.total_runs)).all()

    # ========== Caching ==========

    def get_cached_analysis(
        self, db: Session, cache_key: str
    ) -> Optional[CachedAnalysis]:
        """Get cached analysis result if available and not expired"""
        try:
            cached = (
                db.query(CachedAnalysis)
                .filter(CachedAnalysis.cache_key == cache_key)
                .first()
            )

            if cached:
                # Check if expired
                if cached.expires_at and cached.expires_at < datetime.utcnow():
                    logger.info(f"Cache expired for key: {cache_key}")
                    db.delete(cached)
                    db.commit()
                    return None

                # Update access statistics
                cached.last_accessed = datetime.utcnow()
                cached.access_count += 1
                db.commit()
                db.refresh(cached)

                logger.info(f"Cache HIT for key: {cache_key[:16]}...")
                return cached

            logger.info(f"Cache MISS for key: {cache_key[:16]}...")
            return None
        except Exception as e:
            logger.error(f"Failed to get cached analysis: {e}")
            return None

    def save_to_cache(
        self,
        db: Session,
        cache_key: str,
        data_hash: str,
        user_question: str,
        analysis_id: str,
        result: Dict[str, Any],
        ttl_hours: int = 24,
        execution_time_ms: int = 0,
    ) -> Optional[CachedAnalysis]:
        """Save analysis result to cache"""
        try:
            # Check if already cached
            existing = (
                db.query(CachedAnalysis)
                .filter(CachedAnalysis.cache_key == cache_key)
                .first()
            )

            if existing:
                # Update existing cache
                existing.cached_result = result
                existing.last_accessed = datetime.utcnow()
                existing.access_count = 0  # Reset on update
                existing.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
                db.commit()
                db.refresh(existing)
                logger.info(f"Updated cache for key: {cache_key[:16]}...")
                return existing

            # Create new cache entry
            cached = CachedAnalysis(
                cache_key=cache_key,
                data_hash=data_hash,
                user_question=user_question,
                analysis_id=analysis_id,
                cached_result=result,
                expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
                time_saved_ms=execution_time_ms,
            )
            db.add(cached)
            db.commit()
            db.refresh(cached)
            logger.info(f"Saved to cache with key: {cache_key[:16]}...")
            return cached
        except Exception as e:
            logger.error(f"Failed to save to cache: {e}")
            db.rollback()
            return None

    def clear_expired_cache(self, db: Session) -> int:
        """Clear all expired cache entries"""
        try:
            result = (
                db.query(CachedAnalysis)
                .filter(CachedAnalysis.expires_at < datetime.utcnow())
                .delete()
            )
            db.commit()
            logger.info(f"Cleared {result} expired cache entries")
            return result
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")
            db.rollback()
            return 0

    # ========== Statistics ==========

    def get_analysis_statistics(self, db: Session) -> Dict[str, Any]:
        """Get overall analysis statistics"""
        try:
            total = db.query(Analysis).count()
            completed = db.query(Analysis).filter(Analysis.status == "completed").count()
            failed = db.query(Analysis).filter(Analysis.status == "failed").count()
            cached = db.query(Analysis).filter(Analysis.is_cached == True).count()

            # Average execution time
            avg_time_result = db.query(
                func.avg(Analysis.execution_time_ms)
            ).filter(Analysis.execution_time_ms.isnot(None)).first()

            avg_execution_time = int(avg_time_result[0]) if avg_time_result[0] else 0

            # Cache statistics
            cache_count = db.query(CachedAnalysis).count()
            total_cache_hits = (
                db.query(func.sum(CachedAnalysis.access_count)).scalar() or 0
            )
            total_time_saved = (
                db.query(func.sum(CachedAnalysis.time_saved_ms)).scalar() or 0
            )

            return {
                "total_analyses": total,
                "completed_analyses": completed,
                "failed_analyses": failed,
                "cached_analyses": cached,
                "success_rate": (completed / total * 100) if total > 0 else 0,
                "avg_execution_time_ms": avg_execution_time,
                "cache_entries": cache_count,
                "total_cache_hits": total_cache_hits,
                "total_time_saved_ms": total_time_saved,
                "cache_hit_rate": (cached / total * 100) if total > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get analysis statistics: {e}")
            return {}
