"""
Rate limiter using token bucket algorithm
Prevents API abuse and resource exhaustion
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm
    
    Usage:
        limiter = RateLimiter(max_calls=10, time_window=60)
        
        if await limiter.is_allowed("user_123"):
            # Process request
            await limiter.record_call("user_123")
        else:
            raise HTTPException(429, "Rate limit exceeded")
    """
    
    def __init__(
        self,
        max_calls: int = 10,
        time_window: int = 60
    ):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.buckets: Dict[str, list] = defaultdict(list)  # key -> list of timestamps
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed for the given key
        
        Args:
            key: Unique identifier (e.g., user_id, IP address)
            
        Returns:
            True if allowed, False otherwise
        """
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.time_window)
            
            # Clean old entries
            if key in self.buckets:
                self.buckets[key] = [
                    ts for ts in self.buckets[key] 
                    if ts > cutoff
                ]
            
            # Check if under limit
            count = len(self.buckets.get(key, []))
            return count < self.max_calls
    
    async def record_call(self, key: str):
        """
        Record a call for the given key
        
        Args:
            key: Unique identifier
        """
        async with self.lock:
            now = datetime.utcnow()
            self.buckets[key].append(now)
    
    async def get_remaining(self, key: str) -> int:
        """
        Get remaining calls for the given key
        
        Args:
            key: Unique identifier
            
        Returns:
            Number of remaining calls allowed
        """
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=self.time_window)
            
            if key in self.buckets:
                self.buckets[key] = [
                    ts for ts in self.buckets[key] 
                    if ts > cutoff
                ]
                count = len(self.buckets[key])
            else:
                count = 0
            
            return max(0, self.max_calls - count)
    
    async def get_reset_time(self, key: str) -> datetime:
        """
        Get time when rate limit resets for the given key
        
        Args:
            key: Unique identifier
            
        Returns:
            Datetime when limit resets
        """
        async with self.lock:
            if key not in self.buckets or not self.buckets[key]:
                return datetime.utcnow()
            
            # Get oldest timestamp
            oldest = min(self.buckets[key])
            return oldest + timedelta(seconds=self.time_window)


# Singleton instance
_rate_limiter: RateLimiter = None


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance
    
    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    
    if _rate_limiter is None:
        # Default: 10 requests per minute
        _rate_limiter = RateLimiter(max_calls=10, time_window=60)
    
    return _rate_limiter


async def check_rate_limit(identifier: str) -> Tuple[bool, int, datetime]:
    """
    Convenience function to check rate limit
    
    Args:
        identifier: Unique identifier (IP, user ID, etc.)
        
    Returns:
        Tuple of (is_allowed, remaining_calls, reset_time)
    """
    limiter = get_rate_limiter()
    is_allowed = await limiter.is_allowed(identifier)
    remaining = await limiter.get_remaining(identifier)
    reset_time = await limiter.get_reset_time(identifier)
    
    if is_allowed:
        await limiter.record_call(identifier)
    
    return is_allowed, remaining, reset_time
