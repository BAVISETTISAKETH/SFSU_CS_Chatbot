"""
Database Service - Supabase Integration
Handles all database operations
"""

import os
from supabase import create_client, Client
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer
from datetime import datetime

class DatabaseService:
    """Service for database operations using Supabase."""

    def __init__(self):
        """Initialize Supabase client and embedding model."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.ready = True

    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready

    # ========================================================================
    # VECTOR SEARCH
    # ========================================================================

    async def search_documents(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        HYBRID SEARCH: Combines vector similarity + keyword matching for better results.
        This fixes the issue where vector search alone returns irrelevant documents.
        """
        try:
            # Step 1: Vector similarity search (semantic understanding)
            query_embedding = self.embedding_model.encode(query).tolist()

            vector_result = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": limit * 2  # Get more candidates for filtering
                }
            ).execute()

            vector_docs = vector_result.data if vector_result.data else []

            # Step 2: Keyword search (exact matching)
            # Extract important keywords from query
            keywords = self._extract_keywords(query)

            if keywords:
                print(f"[HYBRID SEARCH] Keywords: {keywords}")

                # Search for documents containing these keywords
                keyword_docs = []
                for keyword in keywords[:5]:  # Use top 5 keywords
                    try:
                        keyword_result = self.client.table("documents")\
                            .select("id, content, source, category, metadata")\
                            .ilike("content", f"%{keyword}%")\
                            .limit(20)\
                            .execute()

                        if keyword_result.data:
                            keyword_docs.extend(keyword_result.data)
                    except:
                        pass

                # Combine and deduplicate results
                all_docs = {}

                # Add vector results with their similarity scores
                for doc in vector_docs:
                    doc_id = doc.get('id')
                    all_docs[doc_id] = {
                        **doc,
                        'vector_score': doc.get('similarity', 0),
                        'keyword_score': 0
                    }

                # Add keyword results and boost their scores
                for doc in keyword_docs:
                    doc_id = doc.get('id')

                    # Calculate keyword score (how many keywords appear in content)
                    content_lower = doc.get('content', '').lower()
                    keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
                    keyword_score = keyword_matches / len(keywords) if keywords else 0

                    if doc_id in all_docs:
                        # Document found by both methods - boost it!
                        all_docs[doc_id]['keyword_score'] = keyword_score
                        all_docs[doc_id]['similarity'] = (all_docs[doc_id]['vector_score'] + keyword_score) / 2
                    else:
                        # Document only found by keyword search
                        all_docs[doc_id] = {
                            **doc,
                            'vector_score': 0,
                            'keyword_score': keyword_score,
                            'similarity': keyword_score * 0.7  # Give it a decent score
                        }

                # Sort by combined score
                ranked_docs = sorted(
                    all_docs.values(),
                    key=lambda x: x.get('similarity', 0),
                    reverse=True
                )[:limit]

                print(f"[HYBRID SEARCH] Found {len(vector_docs)} vector + {len(set(d['id'] for d in keyword_docs))} keyword = {len(ranked_docs)} final docs")

                return ranked_docs
            else:
                # No keywords extracted, use vector search only
                print(f"[VECTOR SEARCH ONLY] Found {len(vector_docs)} docs")
                return vector_docs[:limit]

        except Exception as e:
            print(f"[ERROR] Error searching documents: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query for keyword search."""
        # Common stop words to ignore
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'what', 'where', 'when', 'how', 'who',
            'i', 'me', 'my', 'can', 'do', 'does', 'tell', 'about', 'get', 'find'
        }

        # Split and clean
        words = query.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if w.lower() not in stop_words and len(w) > 2]

        # Keep important multi-word terms intact
        important_terms = {
            'cpt', 'opt', 'f-1', 'i-20', 'gpa', 'fafsa', 'housing', 'sfsu',
            'financial aid', 'international', 'student', 'visa', 'scholarship',
            'course', 'cs', 'degree', 'graduate', 'undergraduate', 'registration',
            'professor', 'faculty', 'advisor', 'office hours', 'tuition'
        }

        # Check for multi-word terms
        query_lower = query.lower()
        for term in important_terms:
            if term in query_lower and term not in keywords:
                keywords.insert(0, term)  # Add at beginning (high priority)

        return keywords

    async def search_verified_facts(
        self,
        query: str,
        limit: int = 3,
        threshold: float = 0.7
    ) -> Optional[Dict]:
        """Search verified facts (professor-approved answers)."""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()

            result = self.client.rpc(
                "match_verified_facts",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": limit
                }
            ).execute()

            if result.data and len(result.data) > 0:
                top_match = result.data[0]
                return {
                    "question": top_match["question"],
                    "answer": top_match["answer"],
                    "confidence": top_match["similarity"],
                    "category": top_match.get("category"),
                    "verified_by": top_match.get("verified_by")
                }

            return None

        except Exception as e:
            print(f"[ERROR] Error searching verified facts: {e}")
            return None

    # ========================================================================
    # CORRECTIONS
    # ========================================================================

    async def create_correction(
        self,
        query: str,
        response: str,
        category: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> int:
        """Create a new correction entry."""
        try:
            result = self.client.table("corrections").insert({
                "student_query": query,
                "rag_response": response,
                "category": category,
                "session_id": session_id,
                "status": "pending"
            }).execute()

            return result.data[0]["id"]

        except Exception as e:
            print(f"[ERROR] Error creating correction: {e}")
            raise

    async def get_corrections(self, status: Optional[str] = None) -> List[Dict]:
        """Get corrections, optionally filtered by status."""
        try:
            query = self.client.table("corrections").select("*")

            if status:
                query = query.eq("status", status)

            result = query.order("created_at", desc=True).execute()
            return result.data

        except Exception as e:
            print(f"[ERROR] Error getting corrections: {e}")
            return []

    async def get_correction(self, correction_id: int) -> Optional[Dict]:
        """Get a single correction by ID."""
        try:
            result = self.client.table("corrections").select("*").eq("id", correction_id).execute()
            return result.data[0] if result.data else None

        except Exception as e:
            print(f"[ERROR] Error getting correction: {e}")
            return None

    async def update_correction(
        self,
        correction_id: int,
        status: str,
        correction_text: Optional[str] = None,
        reviewed_by: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Update a correction."""
        try:
            update_data = {
                "status": status,
                "reviewed_at": datetime.utcnow().isoformat(),
                "reviewed_by": reviewed_by
            }

            if correction_text:
                update_data["professor_correction"] = correction_text

            if notes:
                update_data["notes"] = notes

            self.client.table("corrections").update(update_data).eq("id", correction_id).execute()

        except Exception as e:
            print(f"[ERROR] Error updating correction: {e}")
            raise

    # ========================================================================
    # VERIFIED FACTS
    # ========================================================================

    async def add_verified_fact(
        self,
        question: str,
        answer: str,
        verified_by: str,
        category: Optional[str] = None
    ):
        """Add a verified fact (professor-approved answer)."""
        try:
            # Generate embedding for the question
            embedding = self.embedding_model.encode(question).tolist()

            self.client.table("verified_facts").insert({
                "question": question,
                "answer": answer,
                "embedding": embedding,
                "category": category,
                "verified_by": verified_by
            }).execute()

        except Exception as e:
            print(f"[ERROR] Error adding verified fact: {e}")
            raise

    # ========================================================================
    # CHAT LOGS
    # ========================================================================

    async def log_chat(
        self,
        query: str,
        response: str,
        response_time_ms: int,
        source: str,
        confidence_score: float,
        session_id: Optional[str] = None,
        user_type: str = "student"
    ):
        """Log a chat interaction."""
        try:
            self.client.table("chat_logs").insert({
                "session_id": session_id,
                "user_type": user_type,
                "query": query,
                "response": response,
                "response_time_ms": response_time_ms,
                "source": source,
                "confidence_score": confidence_score
            }).execute()

        except Exception as e:
            print(f"[ERROR] Error logging chat: {e}")

    # ========================================================================
    # FEEDBACK
    # ========================================================================

    async def log_feedback(
        self,
        query: str,
        response: str,
        feedback_type: str,  # 'thumbs_up' or 'thumbs_down'
        session_id: Optional[str] = None,
        message_id: Optional[str] = None
    ):
        """Log user feedback for a response."""
        try:
            self.client.table("feedback").insert({
                "session_id": session_id,
                "message_id": message_id,
                "query": query,
                "response": response,
                "feedback_type": feedback_type,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

        except Exception as e:
            print(f"[ERROR] Error logging feedback: {e}")

    # ========================================================================
    # NOTIFICATIONS
    # ========================================================================

    async def create_notification(
        self,
        session_id: str,
        correction_id: int,
        title: str,
        message: str,
        notification_type: str  # 'correction_approved', 'correction_rejected', 'correction_edited'
    ):
        """Create a notification for a student."""
        try:
            self.client.table("notifications").insert({
                "session_id": session_id,
                "correction_id": correction_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "is_read": False,
                "created_at": datetime.utcnow().isoformat()
            }).execute()

        except Exception as e:
            print(f"[ERROR] Error creating notification: {e}")
            # Don't raise - notifications are not critical

    async def get_notifications(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get notifications for a session."""
        try:
            result = self.client.table("notifications")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return result.data

        except Exception as e:
            print(f"[ERROR] Error getting notifications: {e}")
            return []

    async def mark_notification_as_read(self, notification_id: int):
        """Mark a notification as read."""
        try:
            self.client.table("notifications")\
                .update({"is_read": True})\
                .eq("id", notification_id)\
                .execute()

        except Exception as e:
            print(f"[ERROR] Error marking notification as read: {e}")

    async def mark_all_notifications_as_read(self, session_id: str):
        """Mark all notifications for a session as read."""
        try:
            self.client.table("notifications")\
                .update({"is_read": True})\
                .eq("session_id", session_id)\
                .execute()

        except Exception as e:
            print(f"[ERROR] Error marking all notifications as read: {e}")

    # ========================================================================
    # ANALYTICS
    # ========================================================================

    async def get_analytics(self) -> Dict[str, Any]:
        """Get analytics dashboard data."""
        try:
            # Total queries
            total_queries_result = self.client.table("chat_logs").select("id", count="exact").execute()
            total_queries = total_queries_result.count

            # Total corrections
            corrections_result = self.client.table("corrections").select("id", count="exact").execute()
            total_corrections = corrections_result.count

            # Pending corrections
            pending_result = self.client.table("corrections").select("id", count="exact").eq("status", "pending").execute()
            pending_corrections = pending_result.count

            # Average response time
            avg_time_result = self.client.table("chat_logs").select("response_time_ms").execute()
            avg_response_time = sum(row["response_time_ms"] for row in avg_time_result.data) / len(avg_time_result.data) if avg_time_result.data else 0

            # Source breakdown
            source_breakdown = {}
            sources = ['rag', 'web', 'verified_fact']
            for source in sources:
                count_result = self.client.table("chat_logs").select("id", count="exact").eq("source", source).execute()
                source_breakdown[source] = count_result.count

            # Feedback stats (try-catch in case table doesn't exist yet)
            try:
                thumbs_up_result = self.client.table("feedback").select("id", count="exact").eq("feedback_type", "thumbs_up").execute()
                thumbs_down_result = self.client.table("feedback").select("id", count="exact").eq("feedback_type", "thumbs_down").execute()
                total_feedback = thumbs_up_result.count + thumbs_down_result.count
                satisfaction_rate = (thumbs_up_result.count / total_feedback * 100) if total_feedback > 0 else 0

                feedback_stats = {
                    "thumbs_up": thumbs_up_result.count,
                    "thumbs_down": thumbs_down_result.count,
                    "total_feedback": total_feedback,
                    "satisfaction_rate": round(satisfaction_rate, 1)
                }
            except:
                feedback_stats = {
                    "thumbs_up": 0,
                    "thumbs_down": 0,
                    "total_feedback": 0,
                    "satisfaction_rate": 0
                }

            return {
                "total_queries": total_queries,
                "total_corrections": total_corrections,
                "pending_corrections": pending_corrections,
                "avg_response_time": round(avg_response_time, 2),
                "source_breakdown": source_breakdown,
                "feedback_stats": feedback_stats
            }

        except Exception as e:
            print(f"[ERROR] Error getting analytics: {e}")
            return {
                "total_queries": 0,
                "total_corrections": 0,
                "pending_corrections": 0,
                "avg_response_time": 0,
                "source_breakdown": {},
                "feedback_stats": {
                    "thumbs_up": 0,
                    "thumbs_down": 0,
                    "total_feedback": 0,
                    "satisfaction_rate": 0
                }
            }
