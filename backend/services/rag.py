"""
RAG Service - Retrieval Augmented Generation
Handles document retrieval and context preparation
"""

from typing import Dict, List, Optional
from .database import DatabaseService

class RAGService:
    """Service for RAG operations."""

    def __init__(self):
        """Initialize RAG service."""
        self.db_service = DatabaseService()
        self.ready = True

    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready

    async def search(self, query: str, k: int = 20) -> Dict:
        """
        Search for relevant documents and prepare context.
        Uses hybrid search for accuracy.

        Args:
            query: User query
            k: Number of documents to retrieve (default 20 for quality)

        Returns:
            Dict with context, confidence, and sources
        """
        try:
            # Hybrid search with balanced threshold
            # 20 high-quality documents with 0.15 threshold (balanced)
            docs = await self.db_service.search_documents(query, limit=k, threshold=0.15)

            if not docs:
                print(f"[RAG] NO DOCUMENTS FOUND for query: {query}")
                return {
                    "context": "No relevant information found in the knowledge base.",
                    "confidence": 0.0,
                    "sources": []
                }

            # Prepare context with clear separation
            context_parts = []
            sources = []

            print(f"\n[RAG] Retrieved {len(docs)} documents for: '{query[:60]}...'")

            for i, doc in enumerate(docs):
                # Include source URL if available
                source_info = f"Source: {doc.get('source', 'Unknown')}"
                content = doc.get('content', '').strip()
                similarity = doc.get('similarity', 0.0)

                # Skip empty documents
                if not content:
                    continue

                # Log what we found
                print(f"  [{i+1}] Similarity: {similarity:.3f} | Source: {doc.get('source', 'Unknown')[:60]}...")

                context_parts.append(f"[Document {i+1}] (Relevance: {similarity:.2f})\n{source_info}\n{content}\n")
                sources.append({
                    "id": doc.get('id'),
                    "source": doc.get('source'),
                    "similarity": similarity
                })

            if not context_parts:
                print(f"[RAG] All documents were empty!")
                return {
                    "context": "No relevant information found in the knowledge base.",
                    "confidence": 0.0,
                    "sources": []
                }

            context = "\n---\n".join(context_parts)

            # Calculate weighted confidence (favor higher similarity scores)
            if sources:
                # Weight by position - first result is most important
                weights = [1.0 / (i + 1) for i in range(len(sources))]
                weighted_sim = sum(sources[i]['similarity'] * weights[i] for i in range(len(sources)))
                total_weight = sum(weights)
                avg_confidence = weighted_sim / total_weight
            else:
                avg_confidence = 0.0

            print(f"[RAG] Returning {len(sources)} documents with confidence: {avg_confidence:.2f}\n")

            return {
                "context": context,
                "confidence": avg_confidence,
                "sources": sources
            }

        except Exception as e:
            print(f"[RAG] ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {
                "context": "Error retrieving information from the knowledge base.",
                "confidence": 0.0,
                "sources": []
            }

    async def search_verified_facts(self, query: str) -> Optional[Dict]:
        """
        Search professor-verified facts first (highest priority).

        Args:
            query: User query

        Returns:
            Verified fact if found, None otherwise
        """
        return await self.db_service.search_verified_facts(query)
