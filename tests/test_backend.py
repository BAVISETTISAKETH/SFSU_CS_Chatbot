"""
Simple Backend Test - Verify everything works
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="SFSU CS Chatbot Test API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
print("[*] Initializing services...")

# Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("[OK] Groq initialized")

# Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("[OK] Supabase initialized")

# Embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("[OK] Embedding model loaded")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    source: str
    num_docs_found: int

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "SFSU CS Chatbot API",
        "version": "2.0.0",
        "features": ["RAG", "Groq LLM", "Supabase"]
    }

@app.get("/health")
async def health():
    # Test database connection
    try:
        result = supabase.table("documents").select("id", count="exact").limit(1).execute()
        doc_count = result.count
    except:
        doc_count = 0

    return {
        "status": "healthy",
        "database_connected": doc_count > 0,
        "documents_in_db": doc_count,
        "groq_ready": True,
        "embeddings_ready": True
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Generate embedding for query
        query_embedding = embedding_model.encode(request.query).tolist()

        # 2. Search Supabase
        result = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.4,
                "match_count": 3
            }
        ).execute()

        docs = result.data if result.data else []

        # 3. Create context
        if docs:
            context = "\n\n".join([doc["content"][:500] for doc in docs])
        else:
            context = "No relevant information found."

        # 4. Generate response with Groq
        prompt = f"""You are a helpful assistant for the Computer Science Department at San Francisco State University (SFSU).

Context:
{context}

Question: {request.query}

Answer (be concise and helpful):"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512
        )

        answer = response.choices[0].message.content.strip()

        return ChatResponse(
            response=answer,
            source="rag",
            num_docs_found=len(docs)
        )

    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            source="error",
            num_docs_found=0
        )

if __name__ == "__main__":
    import uvicorn
    print("\n[SUCCESS] Starting SFSU CS Chatbot API...")
    print("[*] Server will run on http://localhost:8001")
    print("[*] Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8001)
