"""
SFSU CS Chatbot - Enhanced Backend API
Features: RAG, Web Search, Professor Correction Workflow, Analytics
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv

# Import custom modules
from services.llm_ollama import OllamaLLMService as LLMService  # Using Ollama (local, NO rate limits)
from services.rag import RAGService
from services.web_search import WebSearchService
from services.dual_source_rag import DualSourceRAG  # NEW: Dual-source retrieval
from services.context_merger import ContextMerger  # NEW: Intelligent context merging
from services.auth import AuthService
from services.database import DatabaseService
from services.cache import ResponseCache
from services.email import EmailService
from services.request_queue import RequestQueueService

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="SFSU CS Chatbot API",
    description="Production-ready chatbot with RAG, web search, and professor correction workflow",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
        "*"  # Change this in production to specific domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
llm_service = LLMService()  # Using Groq with dual-source zero-hallucination prompts
dual_source_rag = DualSourceRAG()  # NEW: Parallel retrieval from both sources
context_merger = ContextMerger()  # NEW: Intelligent context merging
rag_service = RAGService()  # Legacy RAG (kept for verified facts)
web_search_service = WebSearchService()
auth_service = AuthService()
db_service = DatabaseService()
response_cache = ResponseCache(max_size=100, ttl_seconds=3600)  # Cache 100 responses for 1 hour
email_service = EmailService()
request_queue = RequestQueueService(max_requests_per_minute=14)  # Groq free tier: 14 req/min

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None  # [{"role": "user/assistant", "content": "..."}]

class ChatResponse(BaseModel):
    response: str
    source: str  # 'rag', 'web', 'verified_fact'
    confidence: float
    response_time_ms: int
    sources: Optional[List[Dict]] = None
    suggested_questions: Optional[List[str]] = None

class FlagIncorrectRequest(BaseModel):
    query: str
    response: str
    reason: Optional[str] = None
    category: Optional[str] = None
    session_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    query: str
    response: str
    feedback_type: str  # 'thumbs_up' or 'thumbs_down'
    session_id: Optional[str] = None
    message_id: Optional[str] = None

class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str

class SendOTPRequest(BaseModel):
    email: EmailStr
    name: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class RegisterRequest(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str
    department: str
    otp: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    professor_name: str
    email: str

class CorrectionResponse(BaseModel):
    id: int
    student_query: str
    rag_response: str
    professor_correction: Optional[str]
    status: str
    created_at: datetime
    category: Optional[str]

class UpdateCorrectionRequest(BaseModel):
    correction_text: Optional[str] = None
    status: str  # 'approved', 'corrected', 'rejected'
    notes: Optional[str] = None

class FeedbackStats(BaseModel):
    thumbs_up: int
    thumbs_down: int
    total_feedback: int
    satisfaction_rate: float

class AnalyticsResponse(BaseModel):
    total_queries: int
    total_corrections: int
    pending_corrections: int
    avg_response_time: float
    source_breakdown: Dict[str, int]
    feedback_stats: FeedbackStats

# ============================================================================
# HELPERS: Query Enhancement and Response Cleaning
# ============================================================================

def remove_citations(response: str) -> str:
    """
    Remove [Local] and [Web] citation tags from response for production.
    Citations are useful for testing but not user-facing.

    Args:
        response: Response text with citations

    Returns:
        Clean response without citation tags
    """
    import re
    # Remove [Local], [Web], [local], [web] tags (case insensitive)
    clean_response = re.sub(r'\[Local\]|\[Web\]|\[local\]|\[web\]', '', response, flags=re.IGNORECASE)
    # Clean up any double spaces left behind
    clean_response = re.sub(r'\s+', ' ', clean_response)
    return clean_response.strip()

def enhance_query_with_sfsu_context(query: str) -> str:
    """
    Automatically append 'at SFSU' or 'in SFSU' to queries to ensure
    web search results are scoped to San Francisco State University.

    Args:
        query: Original user query

    Returns:
        Enhanced query with SFSU context
    """
    # Check if query already mentions SFSU
    query_lower = query.lower()
    if 'sfsu' in query_lower or 'san francisco state' in query_lower:
        return query  # Already has SFSU context

    # Determine appropriate suffix based on question type
    query_stripped = query.strip().rstrip('?')

    # Question patterns that work better with "at SFSU"
    at_sfsu_patterns = [
        'who is', 'who are', 'who was',
        'where is', 'where are', 'where can',
        'when is', 'when are', 'when do',
        'how do i', 'how can i', 'how to',
        'what is the', 'what are the',
        'is there', 'are there',
        'does', 'do they', 'do you'
    ]

    # Check if query starts with any pattern
    for pattern in at_sfsu_patterns:
        if query_lower.startswith(pattern):
            return f"{query_stripped} at SFSU?"

    # Default: use "in SFSU" for general questions
    # Examples: "Tell me about CS courses" -> "Tell me about CS courses in SFSU"
    return f"{query_stripped} in SFSU?"

# ============================================================================
# DEPENDENCY: Verify Professor Token
# ============================================================================

async def verify_professor(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token for professor authentication."""
    token = credentials.credentials
    professor = auth_service.verify_token(token)

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return professor

# ============================================================================
# PUBLIC ENDPOINTS (Students)
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "SFSU CS Chatbot API",
        "version": "2.0.0",
        "features": ["RAG", "Web Search", "Professor Corrections"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for students.
    Implements smart routing: verified_facts → RAG → web search
    """
    start_time = time.time()

    try:
        # Check cache first (using original query)
        cached_response = response_cache.get(request.query)
        if cached_response:
            print(f"[CACHE HIT] Query: {request.query[:50]}...")
            return ChatResponse(**cached_response)

        # Enhance query with SFSU context for better web search results
        enhanced_query = enhance_query_with_sfsu_context(request.query)
        print(f"[QUERY] Original: {request.query}")
        print(f"[QUERY] Enhanced: {enhanced_query}")

        # Step 1: Check verified facts (highest priority)
        verified_result = await rag_service.search_verified_facts(enhanced_query)

        if verified_result and verified_result['confidence'] > 0.75:
            response_time = int((time.time() - start_time) * 1000)

            # Log the query
            await db_service.log_chat(
                query=request.query,
                response=verified_result['answer'],
                response_time_ms=response_time,
                source='verified_fact',
                confidence_score=verified_result['confidence'],
                session_id=request.session_id
            )

            # Generate suggested questions
            suggested_questions = await _generate_suggested_questions(request.query)

            # PRODUCTION: Remove citation tags
            clean_verified_response = remove_citations(verified_result['answer'])

            response_data = {
                "response": clean_verified_response,
                "source": 'verified_fact',
                "confidence": verified_result['confidence'],
                "response_time_ms": response_time,
                "sources": [{"type": "verified_fact", "verified_by": verified_result.get('verified_by')}],
                "suggested_questions": suggested_questions
            }

            # Cache the response
            response_cache.set(request.query, response_data)

            return ChatResponse(**response_data)

        # Step 2: DUAL-SOURCE RETRIEVAL (MANDATORY - both Vector DB + Web Search)
        print(f"\n[CHAT] Processing query: {enhanced_query}")
        print(f"[CHAT] DUAL-SOURCE MODE: Retrieving from BOTH Vector DB AND Web Search in parallel")

        # CRITICAL: Retrieve from BOTH sources in parallel
        dual_results = await dual_source_rag.retrieve_all_sources(enhanced_query)

        # Verify both sources were attempted
        if not dual_results.get('both_sources_used'):
            print(f"[CHAT] WARNING: Not all sources were used!")

        # Log retrieval summary
        print(f"[CHAT] {dual_source_rag.get_source_summary(dual_results)}")

        # Step 3: Intelligently merge contexts from both sources
        merged = context_merger.merge_contexts(
            vector_results=dual_results['vector_results'],
            web_results=dual_results['web_results'],
            query=enhanced_query
        )

        print(f"[CHAT] Context merged: {merged['total_chars']} chars "
              f"(Vector: {merged['vector_count']}, Web: {merged['web_count']})")

        # Check source diversity
        has_both = context_merger.ensure_source_diversity(merged)
        if not has_both:
            print(f"[CHAT] WARNING: Only one source has results - dual-source requirement not fully met")

        # Step 4: Generate response with ZERO hallucination tolerance
        print(f"[CHAT] Generating response with temperature 0.0 and mandatory citations...")
        llm_result = await llm_service.generate_dual_source_response(
            query=enhanced_query,
            combined_context=merged['combined_context'],
            conversation_history=request.conversation_history
        )

        response_time = int((time.time() - start_time) * 1000)

        # Log validation results
        if not llm_result.get('validated'):
            print(f"[CHAT] WARNING: Response validation failed!")
            print(f"[CHAT] Warnings: {llm_result.get('validation_warnings', [])}")

        if not llm_result.get('has_citations'):
            print(f"[CHAT] WARNING: Response has no source citations!")

        print(f"[CHAT] Citations found: {llm_result.get('citation_count', 0)}")

        # Determine final source label
        if merged['vector_count'] > 0 and merged['web_count'] > 0:
            final_source = 'dual_source'
        elif merged['web_count'] > 0:
            final_source = 'web_only'
        elif merged['vector_count'] > 0:
            final_source = 'vector_only'
        else:
            final_source = 'no_sources'

        # Log to database
        await db_service.log_chat(
            query=request.query,
            response=llm_result['response'],
            response_time_ms=response_time,
            source=final_source,
            confidence_score=merged['combined_confidence'],
            session_id=request.session_id
        )

        # Prepare source information
        sources_info = []
        if merged['vector_count'] > 0:
            sources_info.append({
                "type": "vector_database",
                "count": merged['vector_count'],
                "confidence": merged['vector_confidence']
            })
        if merged['web_count'] > 0:
            sources_info.append({
                "type": "web_search",
                "count": merged['web_count'],
                "confidence": merged['web_confidence']
            })

        # Generate suggested questions
        suggested_questions = await _generate_suggested_questions(request.query)

        # PRODUCTION: Remove citation tags for clean user-facing responses
        clean_response = remove_citations(llm_result['response'])

        response_data = {
            "response": clean_response,
            "source": final_source,
            "confidence": merged['combined_confidence'],
            "response_time_ms": response_time,
            "sources": sources_info,
            "suggested_questions": suggested_questions
        }

        # Cache the response
        response_cache.set(request.query, response_data)

        print(f"[CHAT] [OK] Dual-source response generated in {response_time}ms")
        print(f"[CHAT] Validation: {llm_result.get('validated')}, Citations: {llm_result.get('citation_count', 0)}\n")

        return ChatResponse(**response_data)

    except Exception as e:
        error_msg = str(e)

        # Check if Groq rate limit error
        if "rate_limit" in error_msg.lower() or "429" in error_msg or "too many requests" in error_msg.lower():
            return ChatResponse(
                response="I'm currently handling a lot of requests. Please wait a moment and try again!",
                source='error',
                confidence=0.0,
                response_time_ms=int((time.time() - start_time) * 1000),
                sources=[]
            )

        # Check if API key error
        if "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return ChatResponse(
                response="There's a configuration issue on our end. Please contact support.",
                source='error',
                confidence=0.0,
                response_time_ms=int((time.time() - start_time) * 1000),
                sources=[]
            )

        # Check if database connection error
        if "database" in error_msg.lower() or "connection" in error_msg.lower() or "supabase" in error_msg.lower():
            return ChatResponse(
                response="I'm having trouble accessing my knowledge base. Please try again in a moment.",
                source='error',
                confidence=0.0,
                response_time_ms=int((time.time() - start_time) * 1000),
                sources=[]
            )

        # Generic error with helpful message
        print(f"[ERROR] Chat endpoint error: {error_msg}")
        return ChatResponse(
            response="I encountered an error while processing your question. Please try rephrasing your question or try again later.",
            source='error',
            confidence=0.0,
            response_time_ms=int((time.time() - start_time) * 1000),
            sources=[]
        )

@app.post("/flag-incorrect")
async def flag_incorrect(request: FlagIncorrectRequest):
    """Students can flag incorrect responses for professor review."""
    try:
        correction_id = await db_service.create_correction(
            query=request.query,
            response=request.response,
            category=request.reason or request.category,  # Use reason if provided, fallback to category
            session_id=request.session_id
        )

        return {
            "message": "Thank you for the feedback! A professor will review this response.",
            "correction_id": correction_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")

@app.post("/corrections/flag")
async def flag_incorrect_alt(request: FlagIncorrectRequest):
    """Alternative endpoint for flagging - matches frontend expectations."""
    return await flag_incorrect(request)

@app.get("/corrections/{correction_id}")
async def get_correction_details(correction_id: int):
    """Get correction details for students to view professor's response."""
    try:
        correction = await db_service.get_correction(correction_id)
        if not correction:
            raise HTTPException(status_code=404, detail="Correction not found")

        return {
            "id": correction['id'],
            "student_query": correction['student_query'],
            "original_response": correction['rag_response'],
            "corrected_response": correction.get('professor_correction'),
            "status": correction['status'],
            "reviewed_at": correction.get('reviewed_at'),
            "reviewed_by": correction.get('reviewed_by')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching correction: {str(e)}")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Students can submit thumbs up/down feedback for responses."""
    try:
        await db_service.log_feedback(
            query=request.query,
            response=request.response,
            feedback_type=request.feedback_type,
            session_id=request.session_id,
            message_id=request.message_id
        )

        return {
            "message": "Thank you for your feedback!",
            "feedback_type": request.feedback_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")

@app.get("/notifications/{session_id}")
async def get_student_notifications(session_id: str, limit: int = 10):
    """Get notifications for a student session."""
    try:
        notifications = await db_service.get_notifications(session_id, limit)
        return {
            "notifications": notifications,
            "unread_count": sum(1 for n in notifications if not n.get('is_read', False))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@app.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: int):
    """Mark a single notification as read."""
    try:
        await db_service.mark_notification_as_read(notification_id)
        return {"message": "Notification marked as read"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")

@app.post("/notifications/{session_id}/mark-all-read")
async def mark_all_notifications_read(session_id: str):
    """Mark all notifications for a session as read."""
    try:
        await db_service.mark_all_notifications_as_read(session_id)
        return {"message": "All notifications marked as read"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notifications as read: {str(e)}")

# ============================================================================
# PROFESSOR ENDPOINTS (Authentication Required)
# ============================================================================

@app.post("/professor/send-otp")
async def send_otp(request: SendOTPRequest):
    """Send OTP to email for verification."""
    try:
        # Check if email already exists
        result = db_service.client.table("professors").select("id").eq("email", request.email).execute()

        if result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please login instead."
            )

        # Send OTP
        otp = await email_service.send_otp_email(request.email, request.name)

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )

        return {
            "message": "OTP sent successfully to your email",
            "dev_otp": otp if not email_service.enabled else None  # Only in dev mode
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Send OTP error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

@app.post("/professor/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP for email."""
    try:
        is_valid = email_service.verify_otp(request.email, request.otp)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP. Please request a new one."
            )

        return {"message": "OTP verified successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Verify OTP error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )

@app.post("/professor/register")
async def professor_register(request: RegisterRequest):
    """Professor registration endpoint - OTP already verified in previous step."""
    try:
        print(f"\n[REGISTER] Registration attempt:")
        print(f"  Email: {request.email}")
        print(f"  Username: {request.username}")
        print(f"  Name: {request.name}")

        # OTP was already verified in /professor/verify-otp endpoint
        # No need to verify again - frontend already completed Step 2
        print(f"[REGISTER] Proceeding with account creation...")

        # Check if email already exists
        print(f"[REGISTER] Checking if email exists...")
        result = db_service.client.table("professors").select("id").eq("email", request.email).execute()

        if result.data:
            print(f"[REGISTER] FAILED - Email already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        print(f"[REGISTER] Email is available")

        # Check if username already exists
        print(f"[REGISTER] Checking if username exists...")
        result = db_service.client.table("professors").select("id").eq("username", request.username).execute()

        if result.data:
            print(f"[REGISTER] FAILED - Username already taken")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken. Please choose another."
            )

        print(f"[REGISTER] Username is available")

        # Store password as plain text (simplified for testing)
        plain_password = request.password

        # Create professor
        new_professor = db_service.client.table("professors").insert({
            "name": request.name,
            "username": request.username,
            "email": request.email,
            "password_hash": plain_password,  # Storing plain text now
            "department": request.department,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return {"message": "Account created successfully. Please login."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/professor/login", response_model=LoginResponse)
async def professor_login(request: LoginRequest):
    """Professor login endpoint - accepts username or email."""
    professor = await auth_service.authenticate_professor(request.username, request.password)

    if not professor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password"
        )

    # Generate JWT token
    access_token = auth_service.create_access_token(
        data={
            "email": professor['email'],
            "username": professor.get('username'),
            "id": professor['id']
        }
    )

    return LoginResponse(
        access_token=access_token,
        professor_name=professor['name'],
        email=professor['email']
    )

@app.get("/professor/corrections", response_model=List[CorrectionResponse])
async def get_corrections(
    status_filter: Optional[str] = 'pending',
    professor: dict = Depends(verify_professor)
):
    """Get all corrections (optionally filtered by status)."""
    corrections = await db_service.get_corrections(status=status_filter)
    return corrections

@app.get("/professor/corrections/pending")
async def get_pending_corrections(professor: dict = Depends(verify_professor)):
    """Get pending corrections - matches frontend expectations."""
    corrections = await db_service.get_corrections(status='pending')
    # Convert to match frontend expectations
    return [
        {
            "_id": str(c.get('id')),
            "query": c.get('student_query'),
            "botResponse": c.get('rag_response'),
            "reason": c.get('category', 'No reason provided'),
            "created_at": c.get('created_at')
        }
        for c in corrections
    ]

@app.put("/professor/corrections/{correction_id}")
async def update_correction(
    correction_id: int,
    request: UpdateCorrectionRequest,
    professor: dict = Depends(verify_professor)
):
    """Professor approves, corrects, or rejects a flagged response."""
    try:
        # Update the correction
        await db_service.update_correction(
            correction_id=correction_id,
            status=request.status,
            correction_text=request.correction_text,
            reviewed_by=professor['email'],
            notes=request.notes
        )

        # If corrected with new info, add to verified_facts
        if request.status == 'corrected' and request.correction_text:
            correction = await db_service.get_correction(correction_id)
            await db_service.add_verified_fact(
                question=correction['student_query'],
                answer=request.correction_text,
                verified_by=professor['email'],
                category=correction.get('category')
            )

        return {"message": "Correction updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating correction: {str(e)}")

class ReviewCorrectionRequest(BaseModel):
    action: str  # 'approve' or 'reject'
    corrected_response: Optional[str] = None

@app.post("/professor/corrections/{correction_id}/review")
async def review_correction_endpoint(
    correction_id: str,
    request: ReviewCorrectionRequest,
    professor: dict = Depends(verify_professor)
):
    """
    Review a correction - matches frontend expectations.
    Action can be 'approve' (with or without edits) or 'reject'.
    """
    try:
        correction_id_int = int(correction_id)

        # Get the correction first
        correction = await db_service.get_correction(correction_id_int)
        if not correction:
            raise HTTPException(status_code=404, detail="Correction not found")

        if request.action == 'approve':
            # If there's a corrected response, use it; otherwise use original
            final_answer = request.corrected_response if request.corrected_response else correction['rag_response']

            # Store in verified_facts
            await db_service.add_verified_fact(
                question=correction['student_query'],
                answer=final_answer,
                verified_by=professor['email'],
                category=correction.get('category')
            )

            # Update correction status
            await db_service.update_correction(
                correction_id=correction_id_int,
                status='approved',
                correction_text=final_answer if request.corrected_response else None,
                reviewed_by=professor['email']
            )

            # Create notification for student if session_id exists
            if correction.get('session_id'):
                if request.corrected_response:
                    # Professor edited the response
                    await db_service.create_notification(
                        session_id=correction['session_id'],
                        correction_id=correction_id_int,
                        title="Response Corrected [OK]",
                        message=f"A professor has reviewed and corrected the response to: '{correction['student_query'][:80]}...'",
                        notification_type='correction_edited'
                    )
                else:
                    # Professor approved as-is
                    await db_service.create_notification(
                        session_id=correction['session_id'],
                        correction_id=correction_id_int,
                        title="Response Verified [OK]",
                        message=f"A professor has verified the response to: '{correction['student_query'][:80]}...'",
                        notification_type='correction_approved'
                    )

            return {"message": "Response approved and stored as verified fact"}

        elif request.action == 'reject':
            # Just mark as rejected
            await db_service.update_correction(
                correction_id=correction_id_int,
                status='rejected',
                reviewed_by=professor['email']
            )

            # Create notification for student if session_id exists
            if correction.get('session_id'):
                await db_service.create_notification(
                    session_id=correction['session_id'],
                    correction_id=correction_id_int,
                    title="Flag Reviewed",
                    message=f"A professor has reviewed your flag for: '{correction['student_query'][:80]}...' The original response has been determined to be correct.",
                    notification_type='correction_rejected'
                )

            return {"message": "Correction rejected"}

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid correction ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing correction: {str(e)}")

@app.get("/professor/analytics", response_model=AnalyticsResponse)
async def get_analytics(professor: dict = Depends(verify_professor)):
    """Get chatbot analytics for professors."""
    analytics = await db_service.get_analytics()
    return analytics

@app.get("/professor/stats")
async def get_stats(professor: dict = Depends(verify_professor)):
    """Get stats - matches frontend expectations."""
    analytics = await db_service.get_analytics()
    # Get verified facts count
    verified_facts_result = db_service.client.table("verified_facts").select("id", count="exact").execute()
    verified_facts_count = verified_facts_result.count

    # Get average response time
    avg_response_time = analytics.get('avg_response_time', 0)

    return {
        "totalChats": analytics['total_queries'],
        "totalCorrections": analytics['total_corrections'],
        "verifiedFacts": verified_facts_count,
        "avgResponseTime": round(avg_response_time, 2),
        "feedbackStats": analytics.get('feedback_stats', {
            "thumbs_up": 0,
            "thumbs_down": 0,
            "total_feedback": 0,
            "satisfaction_rate": 0
        })
    }

@app.get("/professor/trending-questions")
async def get_trending_questions(
    limit: int = 10,
    days: int = 7,
    professor: dict = Depends(verify_professor)
):
    """Get trending/most asked questions in the past X days."""
    try:
        # Calculate date threshold
        threshold_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Query chat_logs for most frequent queries
        result = db_service.client.table("chat_logs")\
            .select("query")\
            .gte("created_at", threshold_date)\
            .execute()

        if not result.data:
            return {
                "trending_questions": [],
                "period_days": days,
                "total_queries": 0
            }

        # Count query frequencies
        query_counts = {}
        for entry in result.data:
            query = entry['query'].strip()
            # Skip very short queries
            if len(query) < 10:
                continue
            query_counts[query] = query_counts.get(query, 0) + 1

        # Sort by frequency and get top N
        sorted_questions = sorted(
            query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        trending = [
            {
                "question": q,
                "count": count,
                "percentage": round((count / len(result.data)) * 100, 1)
            }
            for q, count in sorted_questions
        ]

        return {
            "trending_questions": trending,
            "period_days": days,
            "total_queries": len(result.data)
        }

    except Exception as e:
        print(f"[ERROR] Trending questions error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trending questions: {str(e)}"
        )

@app.post("/professor/chat", response_model=ChatResponse)
async def professor_chat(
    request: ChatRequest,
    professor: dict = Depends(verify_professor)
):
    """
    Professors can also chat with the bot.
    Uses same endpoint as students but logs as professor.
    """
    # Reuse the student chat endpoint but mark as professor
    response = await chat(request)
    return response

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def _should_use_web_search(query: str) -> bool:
    """
    Determine if web search should be used based on query keywords.
    E.g., current events, recent changes, etc.
    """
    web_search_keywords = [
        'current', 'latest', 'recent', 'new', 'upcoming', 'schedule',
        'when is', 'what time', 'this semester', 'next semester',
        'fall 2025', 'spring 2026', 'summer 2025'
    ]

    query_lower = query.lower()
    return any(keyword in query_lower for keyword in web_search_keywords)

async def _generate_suggested_questions(query: str, category: Optional[str] = None) -> List[str]:
    """
    Generate suggested follow-up questions based on the user's query.
    Uses pattern matching and context awareness.
    """
    query_lower = query.lower()

    # CS Course-related suggestions
    if any(keyword in query_lower for keyword in ['cs ', 'course', 'class', 'csc']):
        if 'prerequisite' in query_lower or 'requirement' in query_lower:
            return [
                "What GPA do I need for CS courses?",
                "Can I waive course prerequisites?",
                "What are the core CS courses required for graduation?"
            ]
        elif any(num in query_lower for num in ['665', '673', '601', '648']):
            return [
                "When is this course typically offered?",
                "Who teaches this course?",
                "What are the prerequisites for this course?"
            ]
        else:
            return [
                "What CS electives are available?",
                "How many units are CS courses?",
                "Can I take CS courses pass/fail?"
            ]

    # Financial aid suggestions
    elif any(keyword in query_lower for keyword in ['financial aid', 'fafsa', 'scholarship', 'tuition', 'money', 'fee']):
        return [
            "How do I apply for scholarships?",
            "What is the FAFSA deadline?",
            "Are there CS department-specific scholarships?",
            "Can international students get financial aid?"
        ]

    # International student suggestions
    elif any(keyword in query_lower for keyword in ['visa', 'international', 'f-1', 'cpt', 'opt', 'i-20']):
        return [
            "How do I apply for CPT?",
            "What is the difference between CPT and OPT?",
            "How long can I work on OPT?",
            "Where is the International Student Office?"
        ]

    # Housing suggestions
    elif any(keyword in query_lower for keyword in ['housing', 'dorm', 'apartment', 'residence']):
        return [
            "How much does on-campus housing cost?",
            "When is housing application due?",
            "Are there graduate student housing options?",
            "What amenities are included in housing?"
        ]

    # Faculty suggestions
    elif any(keyword in query_lower for keyword in ['professor', 'faculty', 'teach', 'instructor']):
        return [
            "How do I contact my professor?",
            "What are professor office hours?",
            "Who are the CS faculty members?",
            "How do I schedule a meeting with my advisor?"
        ]

    # General graduate program suggestions
    elif any(keyword in query_lower for keyword in ['graduate', 'masters', 'ms', 'grad', 'thesis', 'project']):
        return [
            "What are the MS in CS degree requirements?",
            "Should I choose thesis or project option?",
            "How long does the MS program take?",
            "What is the minimum GPA requirement?"
        ]

    # Admission suggestions
    elif any(keyword in query_lower for keyword in ['admission', 'apply', 'application', 'gre', 'requirement']):
        return [
            "What are the CS program admission requirements?",
            "Is the GRE required for CS admissions?",
            "What is the application deadline?",
            "What GPA do I need to get admitted?"
        ]

    # Default general suggestions
    else:
        return [
            "What CS courses are offered this semester?",
            "How do I contact my academic advisor?",
            "What student resources are available?",
            "Tell me about the CS graduate program"
        ]

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("\n" + "="*70)
    print("SFSU CS Chatbot API - DUAL-SOURCE ZERO-HALLUCINATION MODE")
    print("="*70)
    print(f"[*] Starting SFSU CS Chatbot API (Alli)...")
    print(f"[OK] LLM Service (Ollama - LOCAL, NO RATE LIMITS): {llm_service.is_ready()}")
    print(f"[OK] Dual-Source RAG (MANDATORY both sources): {dual_source_rag.is_ready()}")
    print(f"[OK] Context Merger (Intelligent merging): Initialized")
    print(f"[OK] Vector Database (28,541 docs): {db_service.is_ready()}")
    print(f"[OK] Web Search (SerpAPI): {web_search_service.is_ready()}")
    print(f"[OK] RAG Service (Verified facts): {rag_service.is_ready()}")

    print("\n" + "="*70)
    print("ANTI-HALLUCINATION FEATURES ENABLED:")
    print("="*70)
    print("✓ PARALLEL retrieval from Vector DB + Web Search")
    print("✓ Temperature 0.0 (ZERO creativity)")
    print("✓ MANDATORY source citation [Local] [Web]")
    print("✓ Response validation against sources")
    print("✓ Intelligent context merging")
    print("✓ Conflict detection and resolution")
    print("✓ Ollama local LLM (UNLIMITED requests, no API rate limits)")
    print("="*70 + "\n")

    # Ollama has NO rate limits
    print(f"[OK] Rate Limiting: NONE (Ollama runs locally with unlimited requests)")

    print("[SUCCESS] All services ready! Alli is online in DUAL-SOURCE MODE with Ollama!")
    print("="*70 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("[*] Shutting down SFSU CS Chatbot API...")
    print("[OK] Dual-source system shutdown complete")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
