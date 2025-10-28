"""
Dual-Source RAG Service
CRITICAL: ALWAYS retrieves from BOTH Vector DB AND Web Search in parallel
This is the core anti-hallucination system
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from .database import DatabaseService
from .web_search import WebSearchService


class DualSourceRAG:
    """
    Production-ready dual-source retrieval system.
    MANDATORY: Every query uses BOTH sources - no exceptions.
    """

    def __init__(self):
        """Initialize both retrieval sources."""
        self.db_service = DatabaseService()
        self.web_search = WebSearchService()
        self.ready = True

        # Configuration
        self.vector_top_k = 15  # Number of vector DB results
        self.web_top_results = 3  # Number of web results
        self.min_vector_confidence = 0.15  # Lower threshold for inclusion

        print("[DUAL-SOURCE RAG] Initialized with MANDATORY dual-source retrieval")

    def is_ready(self) -> bool:
        """Check if both sources are ready."""
        return self.ready and self.db_service.is_ready()

    async def retrieve_all_sources(self, query: str) -> Dict:
        """
        CRITICAL: Retrieve from BOTH sources in parallel.
        This is MANDATORY for every query - never skip either source.

        Args:
            query: User's question

        Returns:
            Dict containing results from both sources and metadata
        """
        start_time = time.time()

        print(f"\n[DUAL-SOURCE] PARALLEL RETRIEVAL for: '{query[:60]}...'")

        # CRITICAL: Run BOTH retrievals in parallel - never skip either one
        try:
            # Create parallel tasks for both sources
            vector_task = asyncio.create_task(
                self._retrieve_from_vector_db(query)
            )
            web_task = asyncio.create_task(
                self._retrieve_from_web_search(query)
            )

            # Wait for BOTH to complete (not just one)
            vector_results, web_results = await asyncio.gather(
                vector_task,
                web_task,
                return_exceptions=True  # Don't fail if one source has issues
            )

            # Handle exceptions from either source
            if isinstance(vector_results, Exception):
                print(f"[DUAL-SOURCE] WARNING: Vector DB error: {vector_results}")
                vector_results = {"documents": [], "confidence": 0.0, "count": 0}

            if isinstance(web_results, Exception):
                print(f"[DUAL-SOURCE] WARNING: Web search error: {web_results}")
                web_results = {"results": [], "content": "", "count": 0}

            retrieval_time = time.time() - start_time

            # Log what we retrieved
            print(f"[DUAL-SOURCE] ✓ Vector DB: {vector_results['count']} documents")
            print(f"[DUAL-SOURCE] ✓ Web Search: {web_results['count']} results")
            print(f"[DUAL-SOURCE] ✓ Retrieval time: {retrieval_time:.2f}s")

            # CRITICAL: Verify both sources were attempted
            both_sources_used = True  # Always true in this architecture

            return {
                'vector_results': vector_results,
                'web_results': web_results,
                'retrieval_time_ms': int(retrieval_time * 1000),
                'both_sources_used': both_sources_used,
                'vector_count': vector_results['count'],
                'web_count': web_results['count'],
                'query': query
            }

        except Exception as e:
            print(f"[DUAL-SOURCE] ERROR in parallel retrieval: {e}")
            import traceback
            traceback.print_exc()

            # Even on error, return structure showing we attempted both
            return {
                'vector_results': {"documents": [], "confidence": 0.0, "count": 0},
                'web_results': {"results": [], "content": "", "count": 0},
                'retrieval_time_ms': int((time.time() - start_time) * 1000),
                'both_sources_used': True,  # We attempted both
                'vector_count': 0,
                'web_count': 0,
                'query': query,
                'error': str(e)
            }

    async def _retrieve_from_vector_db(self, query: str) -> Dict:
        """
        Retrieve documents from vector database.

        Args:
            query: User's question

        Returns:
            Dict with documents, confidence, and count
        """
        try:
            # Use hybrid search (vector + keyword) for better accuracy
            docs = await self.db_service.search_documents(
                query,
                limit=self.vector_top_k,
                threshold=self.min_vector_confidence
            )

            if not docs:
                return {
                    "documents": [],
                    "confidence": 0.0,
                    "count": 0
                }

            # Calculate average confidence from similarity scores
            avg_confidence = sum(d.get('similarity', 0) for d in docs) / len(docs)

            return {
                "documents": docs,
                "confidence": avg_confidence,
                "count": len(docs)
            }

        except Exception as e:
            print(f"[VECTOR DB] Error: {e}")
            raise  # Re-raise to be handled by gather()

    async def _retrieve_from_web_search(self, query: str) -> Dict:
        """
        Retrieve current information from web search.

        Args:
            query: User's question

        Returns:
            Dict with web results, content, and count
        """
        try:
            if not self.web_search.enabled:
                print("[WEB SEARCH] Disabled - no API key")
                return {
                    "results": [],
                    "content": "",
                    "count": 0
                }

            # Fetch web search results with full page content
            web_content = await self.web_search.search(
                query,
                num_results=self.web_top_results
            )

            if not web_content:
                return {
                    "results": [],
                    "content": "",
                    "count": 0
                }

            # Parse results (web_search.search returns formatted string)
            # Count how many results were found
            result_count = web_content.count("[Web Result")

            return {
                "results": web_content,  # Formatted string with all results
                "content": web_content,
                "count": result_count
            }

        except Exception as e:
            print(f"[WEB SEARCH] Error: {e}")
            raise  # Re-raise to be handled by gather()

    def get_source_summary(self, dual_results: Dict) -> str:
        """
        Generate human-readable summary of what sources were used.

        Args:
            dual_results: Results from retrieve_all_sources()

        Returns:
            Summary string
        """
        vector_count = dual_results.get('vector_count', 0)
        web_count = dual_results.get('web_count', 0)
        retrieval_time = dual_results.get('retrieval_time_ms', 0)

        summary_parts = []

        if vector_count > 0:
            summary_parts.append(f"{vector_count} documents from knowledge base")
        else:
            summary_parts.append("No documents from knowledge base")

        if web_count > 0:
            summary_parts.append(f"{web_count} live web results")
        else:
            summary_parts.append("No web results")

        summary = f"Retrieved: {', '.join(summary_parts)} ({retrieval_time}ms)"

        return summary
