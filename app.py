from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
import torch
from langchain.prompts import PromptTemplate
import os

app = FastAPI(title="SFSU CS Department Chatbot")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for chat request
class ChatRequest(BaseModel):
    query: str

# Model for chat response
class ChatResponse(BaseModel):
    response: str

# Global variables
DB_DIR = "./vector_db"
vectorstore = None
llm = None
embeddings = None

# Custom prompt template
template = """You are a helpful assistant for the Computer Science Department at San Francisco State University (SFSU).
You provide accurate, concise information to students, faculty, and visitors.

Use the following pieces of context to answer the user's question.
If the information is not found in the context, simply say "I don't have that specific information in my database" rather than making up an answer.

FORMAT GUIDELINES:
- For course listings: Present in a structured format with course codes, titles, and descriptions clearly separated
- For faculty information: List name, title, contact information, and research areas if available
- For requirements: Use bullet points for clarity
- Keep answers concise and directly relevant to the question
- Provide specific information from the context rather than general statements

Context:
{context}

Question: {question}
Answer:"""

PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

class SentenceTransformerEmbeddings:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")
            print("Sentence Transformer moved to GPU")
        
    def embed_documents(self, texts):
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
        
    def embed_query(self, text):
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

@app.on_event("startup")
async def startup_db_client():
    global vectorstore, llm, embeddings
    
    print("Loading vector database...")
    embeddings = SentenceTransformerEmbeddings()
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    print("Loading language model...")
    try:
        # Use Ollama with Deepseek-R1 model
        llm = Ollama(model="deepseek:r1")
        print("Using Deepseek-R1 model via Ollama")
    except Exception as e:
        print(f"Error loading model: {e}")
        # Define a simple completion function as fallback
        def simple_completion(prompt):
            return "I'm currently unable to process your request due to a model loading issue. Please try again later."
        
        llm = simple_completion

@app.get("/")
async def root():
    return {"message": "Welcome to the SFSU CS Department Chatbot API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not vectorstore:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        # Retrieve relevant documents
        docs = vectorstore.similarity_search(request.query, k=4)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Format the prompt
        prompt = PROMPT.format(context=context, question=request.query)
        
        # Get response from LLM
        if callable(llm):
            # For the simple_completion fallback
            response = llm(prompt)
        else:
            # For the Ollama model
            response = llm.invoke(prompt)
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files if frontend directory exists
frontend_dir = "./frontend"
if os.path.exists(frontend_dir) and os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)