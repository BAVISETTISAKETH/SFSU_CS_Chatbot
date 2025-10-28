"""
SFSU CS Chatbot - Gradio Interface (Cloud Version)
Uses Groq LLM + Supabase instead of local Ollama + ChromaDB
"""

import gradio as gr
import os
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client
from sentence_transformers import SentenceTransformer

# Load environment
load_dotenv()

# Initialize services
print("[*] Loading SFSU CS Chatbot (Cloud Version)...")

# Groq LLM
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("[OK] Groq LLM initialized")

# Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("[OK] Supabase connected")

# Embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("[OK] Embedding model loaded")

# Prompt template
SYSTEM_PROMPT = """You are a helpful assistant for the Computer Science Department at San Francisco State University (SFSU).
You provide accurate, concise information to students, faculty, and visitors.

Use the following pieces of context to answer the user's question.
If the information is not found in the context, simply say "I don't have that specific information in my database" rather than making up an answer.

FORMAT GUIDELINES:
- For course listings: Present in a structured format with course codes, titles, and descriptions clearly separated
- For faculty information: List name, title, contact information, and research areas if available
- For requirements: Use bullet points for clarity
- Keep answers concise and directly relevant to the question
- Provide specific information from the context rather than general statements"""

def chat_with_rag(message, history):
    """Chat function using Groq + Supabase RAG."""
    try:
        # 1. Generate embedding for the query
        query_embedding = embedding_model.encode(message).tolist()

        # 2. Search Supabase for similar documents
        result = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.4,
                "match_count": 4
            }
        ).execute()

        docs = result.data if result.data else []

        # Debug output
        print(f"\n[QUERY] {message}")
        print(f"[RETRIEVED] {len(docs)} documents")

        # 3. Create context from retrieved documents
        if docs:
            context_parts = []
            for i, doc in enumerate(docs):
                source = doc.get('source', 'unknown')
                content = doc['content'][:500]  # Limit length
                context_parts.append(f"[Source: {source}]\n{content}")
                print(f"  Doc {i+1}: {source} (similarity: {doc.get('similarity', 0):.2f})")

            context = "\n\n".join(context_parts)
        else:
            context = "No relevant information found in the database."
            print("  [WARNING] No documents retrieved!")

        # 4. Generate response with Groq
        prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {message}

Answer:"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024
        )

        answer = response.choices[0].message.content.strip()

        print(f"[RESPONSE] {answer[:100]}...")

        return answer

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return error_msg

# Create Gradio interface
with gr.Blocks(
    title="SFSU CS Department Chatbot",
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple"
    )
) as demo:

    gr.Markdown("""
    # SFSU CS Department Chatbot
    ### Powered by Groq LLM + Cloud RAG System
    Ask questions about courses, faculty, requirements, and more!
    """)

    # Status indicator
    with gr.Row():
        status_box = gr.Markdown("""
        **Status:** Online | **Model:** Llama 3.3 70B | **Database:** Supabase (17K+ documents)
        """)

    chatbot = gr.Chatbot(
        height=500,
        type="messages",
        label="Chat History",
        avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=chatbot")
    )

    with gr.Row():
        msg = gr.Textbox(
            label="Your Question",
            placeholder="e.g., What are the prerequisites for CSC 413?",
            scale=4
        )
        submit_btn = gr.Button("Send", variant="primary", scale=1)

    clear = gr.Button("Clear Chat")

    # Example questions
    gr.Examples(
        examples=[
            "What are the prerequisites for CSC 413?",
            "Who are the faculty members in the CS department?",
            "What courses are required for the CS major?",
            "When are office hours for CS faculty?",
            "How can I apply to the master's program?",
            "Tell me about the Software Engineering program",
            "What research areas does the department focus on?"
        ],
        inputs=msg,
        label="Example Questions"
    )

    # Footer
    gr.Markdown("""
    ---
    **Tip:** This chatbot searches through SFSU CS department data to answer your questions.
    If you get an error, the information might not be in the database yet.

    **Tech Stack:** Groq (Llama 3.3 70B) - Supabase PostgreSQL - pgvector - Sentence Transformers
    """)

    def respond(message, chat_history):
        """Handle user message and update chat."""
        if not message or message.strip() == "":
            return "", chat_history

        bot_message = chat_with_rag(message, chat_history)

        # Make sure we have a response
        if not bot_message or bot_message.strip() == "":
            bot_message = "I'm sorry, I couldn't generate a response. Please try again or rephrase your question."

        # Update chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})

        return "", chat_history

    # Event handlers
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit_btn.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    print("\n" + "="*60)
    print("[*] Starting SFSU CS Chatbot (Cloud Version)")
    print("="*60)
    print("[OK] All services initialized successfully!")
    print("[*] Opening Gradio interface...")
    print("="*60 + "\n")

    demo.launch(
        share=False,
        show_error=True,
        inbrowser=True
    )
