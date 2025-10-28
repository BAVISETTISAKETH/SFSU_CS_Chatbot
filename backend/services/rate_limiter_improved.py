"""
Improved Rate Limiter for Groq API
Properly handles burst requests with rolling window tracking
"""

import time
from collections import deque
from typing import Optional, Dict


class ImprovedRateLimiter:
    """
    Smart rate limiter that tracks requests over rolling time windows.
    Prevents hitting Groq API rate limits while maximizing throughput.
    """

    def __init__(
        self,
        requests_per_minute: int = 14,
        tokens_per_minute: int = 14400,
        tier: str = "free"
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Max requests allowed per minute
            tokens_per_minute: Max tokens allowed per minute
            tier: 'free' or 'paid' (determines limits)
        """
        # Set limits based on tier
        if tier == "paid":
            self.max_requests_per_minute = 30
            self.max_tokens_per_minute = 100000
        else:  # free tier
            self.max_requests_per_minute = 14
            self.max_tokens_per_minute = 14400

        # Override with custom values if provided
        if requests_per_minute:
            self.max_requests_per_minute = requests_per_minute
        if tokens_per_minute:
            self.max_tokens_per_minute = tokens_per_minute

        # Rolling window tracking (last 60 seconds)
        self.request_times = deque()  # Timestamps of requests
        self.token_usage = deque()     # (timestamp, tokens) tuples
        self.window_seconds = 60

        # Safety buffer (use 90% of limit to be safe)
        self.safety_factor = 0.9
        self.effective_max_requests = int(
            self.max_requests_per_minute * self.safety_factor
        )

        print(f"[RATE LIMITER] Initialized:")
        print(f"  Tier: {tier}")
        print(f"  Max requests/min: {self.max_requests_per_minute} (using {self.effective_max_requests} with safety buffer)")
        print(f"  Max tokens/min: {self.max_tokens_per_minute}")

    def _clean_old_entries(self):
        """Remove entries older than 60 seconds from tracking."""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Clean old request times
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()

        # Clean old token usage
        while self.token_usage and self.token_usage[0][0] < cutoff_time:
            self.token_usage.popleft()

    def check_rate_limit(self, estimated_tokens: int = 500) -> Dict:
        """
        Check if request can proceed without hitting rate limit.

        Args:
            estimated_tokens: Estimated tokens for this request

        Returns:
            Dict with:
                - can_proceed: bool
                - wait_seconds: float (how long to wait if can't proceed)
                - reason: str (why request is blocked)
                - current_usage: Dict (current usage stats)
        """
        self._clean_old_entries()

        current_time = time.time()
        current_requests = len(self.request_times)
        current_tokens = sum(tokens for _, tokens in self.token_usage)

        # Check request limit
        if current_requests >= self.effective_max_requests:
            # Calculate wait time (time until oldest request expires)
            oldest_request_time = self.request_times[0]
            wait_seconds = max(
                0,
                self.window_seconds - (current_time - oldest_request_time) + 1
            )

            return {
                'can_proceed': False,
                'wait_seconds': wait_seconds,
                'reason': f'Request limit reached ({current_requests}/{self.effective_max_requests} requests in last 60s)',
                'current_usage': {
                    'requests': current_requests,
                    'tokens': current_tokens,
                    'requests_limit': self.effective_max_requests,
                    'tokens_limit': self.max_tokens_per_minute
                }
            }

        # Check token limit
        if current_tokens + estimated_tokens > self.max_tokens_per_minute:
            # Calculate wait time (time until enough tokens free up)
            oldest_token_time = self.token_usage[0][0] if self.token_usage else current_time
            wait_seconds = max(
                0,
                self.window_seconds - (current_time - oldest_token_time) + 1
            )

            return {
                'can_proceed': False,
                'wait_seconds': wait_seconds,
                'reason': f'Token limit would be exceeded ({current_tokens + estimated_tokens}/{self.max_tokens_per_minute} tokens)',
                'current_usage': {
                    'requests': current_requests,
                    'tokens': current_tokens,
                    'requests_limit': self.effective_max_requests,
                    'tokens_limit': self.max_tokens_per_minute
                }
            }

        # All clear!
        return {
            'can_proceed': True,
            'wait_seconds': 0,
            'reason': 'OK',
            'current_usage': {
                'requests': current_requests,
                'tokens': current_tokens,
                'requests_limit': self.effective_max_requests,
                'tokens_limit': self.max_tokens_per_minute
            }
        }

    def record_request(self, tokens_used: int = 500):
        """
        Record that a request was made.

        Args:
            tokens_used: Actual tokens used in this request
        """
        current_time = time.time()
        self.request_times.append(current_time)
        self.token_usage.append((current_time, tokens_used))

        self._clean_old_entries()

    async def wait_if_needed(self, estimated_tokens: int = 500) -> Dict:
        """
        Wait if necessary to avoid rate limit, then proceed.

        Args:
            estimated_tokens: Estimated tokens for this request

        Returns:
            Dict with rate limit check results
        """
        import asyncio

        check_result = self.check_rate_limit(estimated_tokens)

        if not check_result['can_proceed']:
            wait_seconds = check_result['wait_seconds']
            print(f"[RATE LIMITER] {check_result['reason']}")
            print(f"[RATE LIMITER] Waiting {wait_seconds:.1f} seconds...")

            # Wait in small increments to allow cancellation
            waited = 0
            while waited < wait_seconds:
                await asyncio.sleep(min(1, wait_seconds - waited))
                waited += 1

                # Re-check in case older requests expired
                if waited % 5 == 0:
                    check_result = self.check_rate_limit(estimated_tokens)
                    if check_result['can_proceed']:
                        print(f"[RATE LIMITER] Rate limit cleared early!")
                        break

        return check_result

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""
        self._clean_old_entries()

        current_requests = len(self.request_times)
        current_tokens = sum(tokens for _, tokens in self.token_usage)

        return {
            'requests_used': current_requests,
            'requests_limit': self.effective_max_requests,
            'requests_available': max(0, self.effective_max_requests - current_requests),
            'requests_percentage': round((current_requests / self.effective_max_requests) * 100, 1),
            'tokens_used': current_tokens,
            'tokens_limit': self.max_tokens_per_minute,
            'tokens_available': max(0, self.max_tokens_per_minute - current_tokens),
            'tokens_percentage': round((current_tokens / self.max_tokens_per_minute) * 100, 1)
        }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
# In backend/services/llm.py:

from .rate_limiter_improved import ImprovedRateLimiter

class LLMService:
    def __init__(self):
        # ... existing code ...

        # Initialize improved rate limiter
        self.rate_limiter = ImprovedRateLimiter(
            tier='free'  # or 'paid' if you upgrade
        )

    async def generate_dual_source_response(self, query, combined_context, conversation_history):
        # Wait if needed to avoid rate limit
        await self.rate_limiter.wait_if_needed(estimated_tokens=1500)

        try:
            # Make API call
            response = self.client.chat.completions.create(...)

            # Record the request
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 500
            self.rate_limiter.record_request(tokens_used)

            return response

        except Exception as e:
            # Handle rate limit errors
            if "rate_limit" in str(e).lower():
                stats = self.rate_limiter.get_usage_stats()
                print(f"[ERROR] Rate limit hit despite limiter: {stats}")

            raise
"""
