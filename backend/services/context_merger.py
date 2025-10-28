"""
Context Merger - Intelligent Merging of Dual Sources
Combines Vector DB and Web Search results intelligently
"""

from typing import Dict, List, Tuple
import re


class ContextMerger:
    """
    Intelligently merges context from Vector DB and Web Search.
    Handles deduplication, ranking, balancing, and formatting.
    """

    def __init__(self):
        """Initialize context merger with configuration."""
        # Token limits for context
        self.max_total_tokens = 8000  # Total context size
        self.vector_ratio = 0.60  # 60% from vector DB
        self.web_ratio = 0.40  # 40% from web search

        # Character estimates (rough: 1 token ≈ 4 characters)
        self.max_total_chars = self.max_total_tokens * 4
        self.max_vector_chars = int(self.max_total_chars * self.vector_ratio)
        self.max_web_chars = int(self.max_total_chars * self.web_ratio)

    def merge_contexts(
        self,
        vector_results: Dict,
        web_results: Dict,
        query: str
    ) -> Dict:
        """
        Merge results from both sources into unified context.

        Args:
            vector_results: Results from vector database
            web_results: Results from web search
            query: Original user query

        Returns:
            Dict with merged context and metadata
        """
        print(f"\n[CONTEXT MERGER] Merging contexts from both sources")

        # Step 1: Extract and format vector DB context
        vector_context = self._format_vector_context(
            vector_results.get('documents', [])
        )

        # Step 2: Extract and format web search context
        web_context = self._format_web_context(
            web_results.get('content', '')
        )

        # Step 3: Balance context sizes
        vector_context_balanced, web_context_balanced = self._balance_contexts(
            vector_context,
            web_context
        )

        # Step 4: Detect conflicts/overlaps
        has_conflicts = self._detect_conflicts(
            vector_context_balanced,
            web_context_balanced,
            query
        )

        # Step 5: Format final combined context
        combined_context = self._format_combined_context(
            vector_context_balanced,
            web_context_balanced,
            vector_results.get('count', 0),
            web_results.get('count', 0),
            has_conflicts
        )

        # Step 6: Calculate confidence scores
        vector_confidence = vector_results.get('confidence', 0.0)
        web_confidence = 0.85 if web_results.get('count', 0) > 0 else 0.0

        # Combined confidence (weighted average)
        if vector_results.get('count', 0) > 0 and web_results.get('count', 0) > 0:
            combined_confidence = (vector_confidence * 0.6) + (web_confidence * 0.4)
        elif vector_results.get('count', 0) > 0:
            combined_confidence = vector_confidence * 0.8  # Reduce if only one source
        elif web_results.get('count', 0) > 0:
            combined_confidence = web_confidence * 0.8
        else:
            combined_confidence = 0.0

        print(f"[CONTEXT MERGER] Vector: {len(vector_context_balanced)} chars, "
              f"Web: {len(web_context_balanced)} chars, "
              f"Total: {len(combined_context)} chars")
        print(f"[CONTEXT MERGER] Confidence: {combined_confidence:.2f} "
              f"(Vector: {vector_confidence:.2f}, Web: {web_confidence:.2f})")

        return {
            'combined_context': combined_context,
            'vector_context': vector_context_balanced,
            'web_context': web_context_balanced,
            'vector_confidence': vector_confidence,
            'web_confidence': web_confidence,
            'combined_confidence': combined_confidence,
            'has_conflicts': has_conflicts,
            'vector_count': vector_results.get('count', 0),
            'web_count': web_results.get('count', 0),
            'total_chars': len(combined_context)
        }

    def _format_vector_context(self, documents: List[Dict]) -> str:
        """
        Format vector database documents into readable context.

        Args:
            documents: List of document dicts from vector DB

        Returns:
            Formatted context string
        """
        if not documents:
            return ""

        context_parts = []

        for i, doc in enumerate(documents):
            content = doc.get('content', '').strip()
            source = doc.get('source', 'Unknown')
            similarity = doc.get('similarity', 0.0)
            category = doc.get('category', 'General')

            if not content:
                continue

            # Format each document clearly
            formatted_doc = (
                f"[Local Document {i+1}] (Relevance: {similarity:.2f}, Category: {category})\n"
                f"Source: {source}\n"
                f"{content}\n"
            )

            context_parts.append(formatted_doc)

        return "\n---\n".join(context_parts)

    def _format_web_context(self, web_content: str) -> str:
        """
        Format web search results into readable context.

        Args:
            web_content: Raw web search results string

        Returns:
            Formatted context string
        """
        if not web_content:
            return ""

        # Web search already returns formatted content
        # Just ensure it's properly marked
        return web_content

    def _balance_contexts(
        self,
        vector_context: str,
        web_context: str
    ) -> Tuple[str, str]:
        """
        Balance context sizes according to configured ratios.

        Args:
            vector_context: Vector DB context
            web_context: Web search context

        Returns:
            Tuple of (balanced_vector, balanced_web)
        """
        # Check current sizes
        vector_len = len(vector_context)
        web_len = len(web_context)
        total_len = vector_len + web_len

        # If total is under limit, return as-is
        if total_len <= self.max_total_chars:
            return vector_context, web_context

        print(f"[CONTEXT MERGER] Balancing: {total_len} chars -> {self.max_total_chars} chars")

        # Truncate each according to ratio
        vector_balanced = vector_context[:self.max_vector_chars]
        web_balanced = web_context[:self.max_web_chars]

        # Add truncation notice if needed
        if len(vector_context) > self.max_vector_chars:
            vector_balanced += "\n\n[... Vector DB context truncated for token limit ...]"

        if len(web_context) > self.max_web_chars:
            web_balanced += "\n\n[... Web search context truncated for token limit ...]"

        return vector_balanced, web_balanced

    def _detect_conflicts(
        self,
        vector_context: str,
        web_context: str,
        query: str
    ) -> bool:
        """
        Detect if there might be conflicting information between sources.

        Args:
            vector_context: Vector DB context
            web_context: Web search context
            query: User query

        Returns:
            True if potential conflicts detected
        """
        # Simple heuristic: if query contains time-sensitive keywords
        # and both sources have content, there might be conflicts
        time_keywords = [
            'current', 'latest', 'recent', 'new', 'upcoming',
            'fall 2025', 'spring 2025', 'this semester', 'next semester'
        ]

        query_lower = query.lower()
        is_time_sensitive = any(kw in query_lower for kw in time_keywords)

        has_both_sources = bool(vector_context) and bool(web_context)

        # If query is time-sensitive and we have both sources,
        # there's a higher chance of conflicts (web being more recent)
        return is_time_sensitive and has_both_sources

    def _format_combined_context(
        self,
        vector_context: str,
        web_context: str,
        vector_count: int,
        web_count: int,
        has_conflicts: bool
    ) -> str:
        """
        Format the final combined context with clear source labels.

        Args:
            vector_context: Vector DB context
            web_context: Web search context
            vector_count: Number of vector documents
            web_count: Number of web results
            has_conflicts: Whether conflicts were detected

        Returns:
            Formatted combined context string
        """
        parts = []

        # Header explaining both sources
        header = """=== INFORMATION FROM TWO SOURCES ===

You have access to TWO independent information sources:
1. LOCAL KNOWLEDGE BASE: Pre-scraped documents from SFSU (may be older)
2. LIVE WEB SEARCH: Current information directly from SFSU websites (most recent)

CRITICAL RULES:
- ALWAYS cite which source you're using: [Local] or [Web]
- If sources conflict, mention both perspectives
- Prioritize Web Search for time-sensitive information
- Use Local Knowledge Base for stable/established facts
- If NEITHER source has the information, say: "I don't have that information in either source"
- NEVER generate information not found in these sources
"""
        parts.append(header)

        # Add vector DB context
        if vector_context:
            vector_section = f"""
=== LOCAL KNOWLEDGE BASE ({vector_count} documents) ===
Source: Pre-scraped SFSU documents
{vector_context}
"""
            parts.append(vector_section)
        else:
            parts.append("\n=== LOCAL KNOWLEDGE BASE ===\nNo relevant documents found.\n")

        # Add web search context
        if web_context:
            web_section = f"""
=== LIVE WEB SEARCH RESULTS ({web_count} results) ===
Source: Current SFSU websites (fetched just now)
{web_context}
"""
            parts.append(web_section)
        else:
            parts.append("\n=== LIVE WEB SEARCH RESULTS ===\nNo web results found.\n")

        # Add conflict warning if detected
        if has_conflicts:
            conflict_warning = """
⚠️ POTENTIAL CONFLICT DETECTED:
This query is time-sensitive. If Local and Web sources provide different information:
- Prioritize Web Search (more current)
- Mention that information may have changed
- Cite both sources with their different information
"""
            parts.append(conflict_warning)

        return "\n".join(parts)

    def ensure_source_diversity(self, merged_context: Dict) -> bool:
        """
        Verify that both sources are represented in the merged context.

        Args:
            merged_context: Result from merge_contexts()

        Returns:
            True if both sources contributed
        """
        has_vector = merged_context.get('vector_count', 0) > 0
        has_web = merged_context.get('web_count', 0) > 0

        if not has_vector and not has_web:
            print("[CONTEXT MERGER] WARNING: Neither source has results!")
            return False

        if not has_vector:
            print("[CONTEXT MERGER] WARNING: No vector DB results")

        if not has_web:
            print("[CONTEXT MERGER] WARNING: No web search results")

        # Ideally both should contribute
        return has_vector and has_web
