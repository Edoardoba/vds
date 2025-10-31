"""
Circuit Breaker pattern implementation for external API calls
Prevents cascading failures and gives services time to recover
"""

import asyncio
import logging
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject all requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for protecting external service calls
    
    Usage:
        breaker = CircuitBreaker(name="claude_api", failure_threshold=5, timeout=60)
        
        try:
            result = await breaker.call(api_call_function, *args, **kwargs)
        except CircuitBreakerOpenError:
            # Handle service unavailable
            pass
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
        on_open: Optional[Callable] = None
    ):
        """
        Initialize circuit breaker
        
        Args:
            name: Identifier for the circuit breaker
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds before attempting to close circuit (half-open state)
            success_threshold: Number of successes in half-open to fully close
            on_open: Optional callback when circuit opens
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.on_open = on_open
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call a function through the circuit breaker
        
        Args:
            func: Async function to call
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Result from function
            
        Raises:
            CircuitBreakerOpenError: When circuit is open
        """
        async with self.lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    # Circuit still open, reject immediately
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Failed {self.failure_count} times. "
                        f"Will retry in {self._time_until_retry()} seconds"
                    )
        
        # Attempt the call
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful call"""
        async with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    logger.info(f"Circuit breaker '{self.name}' CLOSED (service recovered)")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.state == CircuitState.HALF_OPEN:
                # Failure in half-open state, go back to open
                logger.warning(f"Circuit breaker '{self.name}' reopened after failed recovery")
                self.state = CircuitState.OPEN
                self.success_count = 0
                
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    logger.error(
                        f"Circuit breaker '{self.name}' OPENED after {self.failure_count} failures"
                    )
                    self.state = CircuitState.OPEN
                    
                    # Call notification callback
                    if self.on_open:
                        try:
                            await self.on_open(self.name, self.failure_count)
                        except Exception as e:
                            logger.error(f"Error in circuit breaker on_open callback: {e}")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        if self.last_failure_time is None:
            return False
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
    
    def _time_until_retry(self) -> int:
        """Get seconds until next retry attempt"""
        if self.last_failure_time is None:
            return 0
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        remaining = max(0, self.timeout - elapsed)
        return int(remaining)
    
    def get_stats(self) -> dict:
        """Get current circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else None
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# Singleton instances for common services
_claude_circuit_breaker: Optional[CircuitBreaker] = None


def get_claude_circuit_breaker() -> CircuitBreaker:
    """
    Get or create Claude API circuit breaker instance
    
    Returns:
        CircuitBreaker instance for Claude API
    """
    global _claude_circuit_breaker
    
    if _claude_circuit_breaker is None:
        _claude_circuit_breaker = CircuitBreaker(
            name="claude_api",
            failure_threshold=5,
            timeout=60,  # Wait 60 seconds before retrying
            success_threshold=2
        )
    
    return _claude_circuit_breaker
