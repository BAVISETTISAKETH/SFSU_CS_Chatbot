"""
Response Cache Service - Reduce API calls and avoid rate limits
Caches chatbot responses for frequently asked questions
"""

import hashlib
import time
from typing import Optional, Dict, Any
from collections import OrderedDict


class ResponseCache:
    """Simple in-memory cache for chatbot responses."""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """
        Initialize response cache.

        Args:
            max_size: Maximum number of cached responses
            ttl_seconds: Time-to-live for cached responses (default 1 hour)
        """
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def _get_key(self, query: str) -> str:
        """Generate cache key from query."""
        # Normalize query: lowercase, strip whitespace
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response for a query.

        Args:
            query: User query

        Returns:
            Cached response dict or None if not found/expired
        """
        key = self._get_key(query)

        if key not in self.cache:
            return None

        cached_data = self.cache[key]

        # Check if expired
        if time.time() - cached_data['timestamp'] > self.ttl_seconds:
            # Remove expired entry
            del self.cache[key]
            return None

        # Move to end (LRU)
        self.cache.move_to_end(key)

        return cached_data['response']

    def set(self, query: str, response: Dict[str, Any]) -> None:
        """
        Cache a response for a query.

        Args:
            query: User query
            response: Response dict to cache
        """
        key = self._get_key(query)

        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest (first) entry
            self.cache.popitem(last=False)

        # Add/update entry
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }

        # Move to end (most recent)
        self.cache.move_to_end(key)

    def clear(self) -> None:
        """Clear all cached responses."""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'hit_rate': getattr(self, '_hit_rate', 0.0)
        }
