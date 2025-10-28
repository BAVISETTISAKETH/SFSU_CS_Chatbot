"""
Request Queue Service for Multi-User LLM Rate Limiting
Handles concurrent requests from multiple users while respecting API rate limits
"""

import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class QueuedRequest:
    """Represents a queued request"""
    request_id: str
    timestamp: float
    query: str
    context: str
    use_web_context: bool
    conversation_history: Optional[list]
    result_future: asyncio.Future

class RequestQueueService:
    """
    Manages a queue of LLM requests to prevent rate limit errors with multiple users.

    Groq Free Tier Limits:
    - 14 requests per minute
    - 14,400 tokens per minute

    This service ensures we stay under limits even with many concurrent users.
    """

    def __init__(self, max_requests_per_minute: int = 13):
        """
        Initialize request queue service.

        Args:
            max_requests_per_minute: Maximum requests to allow per minute (default 13 for safety)
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.min_request_interval = 60.0 / max_requests_per_minute  # ~4.6 seconds

        self.queue: asyncio.Queue = asyncio.Queue()
        self.processing = False
        self.last_request_time = 0

        # Stats for monitoring
        self.total_requests = 0
        self.requests_processed = 0
        self.current_queue_size = 0

        print(f"[QUEUE] Request queue initialized: {max_requests_per_minute} requests/min max")
        print(f"[QUEUE] Min interval between requests: {self.min_request_interval:.2f}s")

    async def start_processing(self, llm_service):
        """
        Start the background queue processor.

        Args:
            llm_service: The LLM service instance to use for generation
        """
        if self.processing:
            return

        self.processing = True
        print("[QUEUE] Background processor started")

        # Start background task
        asyncio.create_task(self._process_queue(llm_service))

    async def _process_queue(self, llm_service):
        """Background task that processes queued requests one by one."""
        while self.processing:
            try:
                # Get next request from queue (wait if empty)
                queued_request: QueuedRequest = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )

                # Update stats
                self.current_queue_size = self.queue.qsize()

                # Enforce rate limiting
                current_time = time.time()
                time_since_last = current_time - self.last_request_time

                if time_since_last < self.min_request_interval:
                    sleep_time = self.min_request_interval - time_since_last
                    print(f"[QUEUE] Rate limiting: waiting {sleep_time:.1f}s (queue: {self.current_queue_size})")
                    await asyncio.sleep(sleep_time)

                # Process the request
                try:
                    print(f"[QUEUE] Processing request {queued_request.request_id[:8]}... (queue: {self.current_queue_size})")

                    # Call LLM service WITHOUT its internal rate limiting (we handle it here)
                    result = await self._call_llm_direct(
                        llm_service,
                        queued_request.query,
                        queued_request.context,
                        queued_request.use_web_context,
                        queued_request.conversation_history
                    )

                    # Return result to waiting request
                    queued_request.result_future.set_result(result)

                    self.last_request_time = time.time()
                    self.requests_processed += 1

                    print(f"[QUEUE] Request completed (total: {self.requests_processed})")

                except Exception as e:
                    print(f"[QUEUE] Error processing request: {e}")
                    queued_request.result_future.set_exception(e)

                finally:
                    self.queue.task_done()

            except asyncio.TimeoutError:
                # No requests in queue, continue waiting
                continue
            except Exception as e:
                print(f"[QUEUE] Queue processor error: {e}")
                await asyncio.sleep(1)

    async def _call_llm_direct(self, llm_service, query, context, use_web_context, conversation_history):
        """
        Call LLM service directly (works with both Groq and Ollama).
        """
        try:
            # Simply call the generate_response method - works for all LLM services
            response = await llm_service.generate_response(
                query=query,
                context=context,
                use_web_context=use_web_context,
                conversation_history=conversation_history
            )
            return response

        except Exception as e:
            print(f"[QUEUE] LLM error: {str(e)[:100]}")
            return "I'm having trouble generating a response. Please try again."

    async def add_request(
        self,
        query: str,
        context: str,
        use_web_context: bool = False,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Add a request to the queue and wait for result.

        Args:
            query: User's question
            context: Retrieved context
            use_web_context: Whether context includes web search
            conversation_history: Previous conversation

        Returns:
            Generated response
        """
        # Create queued request
        request_id = str(uuid4())
        result_future = asyncio.Future()

        queued_request = QueuedRequest(
            request_id=request_id,
            timestamp=time.time(),
            query=query,
            context=context,
            use_web_context=use_web_context,
            conversation_history=conversation_history,
            result_future=result_future
        )

        # Add to queue
        await self.queue.put(queued_request)
        self.total_requests += 1
        queue_position = self.queue.qsize()

        print(f"[QUEUE] Request {request_id[:8]} added (position: {queue_position})")

        # Wait for result
        try:
            result = await asyncio.wait_for(result_future, timeout=120)  # 2 minute max wait
            return result
        except asyncio.TimeoutError:
            return "Your request timed out. Please try again."
        except Exception as e:
            print(f"[QUEUE] Error waiting for result: {e}")
            return "An error occurred processing your request."

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queue_size": self.queue.qsize(),
            "total_requests": self.total_requests,
            "requests_processed": self.requests_processed,
            "processing": self.processing,
            "max_requests_per_minute": self.max_requests_per_minute
        }

    async def stop(self):
        """Stop the queue processor."""
        self.processing = False
        print("[QUEUE] Queue processor stopped")
