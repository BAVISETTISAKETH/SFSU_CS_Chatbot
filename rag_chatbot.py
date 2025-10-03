import gradio as gr
import os
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
import torch
from langchain.prompts import PromptTemplate

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

# Setup function
def setup():
    global vectorstore, llm, embeddings
    
    print("Loading vector database...")
    embeddings = SentenceTransformerEmbeddings()
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    print("Loading language model...")
    try:
        # Use Ollama with Deepseek-R1 model
        llm = Ollama(model="Deepseek-R1")
        print("Using Deepseek-R1 model via Ollama")
    except Exception as e:
        print(f"Error loading model: {e}")
        # Define a simple completion function as fallback
        def simple_completion(prompt):
            return "I'm currently unable to process your request due to a model loading issue. Please try again later."
        
        llm = simple_completion

# Initialize everything
setup()

# Chat function for Gradio
def chat_with_rag(message, history):
    try:
        # Show retrieved docs in console for debugging
        docs = vectorstore.similarity_search(message, k=4)
        print(f"\nRetrieved documents for: '{message}'")
        for i, doc in enumerate(docs):
            print(f"Document {i+1} (Source: {doc.metadata.get('source', 'unknown')}):")
            print(f"{doc.page_content[:200]}...")
        
        # Create context from docs
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Format the prompt
        prompt = PROMPT.format(context=context, question=message)
        print(f"Sending prompt to LLM: {prompt[:100]}...")
        
        # Get response from LLM
        if callable(llm) and not hasattr(llm, 'invoke'):
            # For the simple_completion fallback
            response = llm(prompt)
        else:
            # For the Ollama model
            response = llm.invoke(prompt)
            # The response might be an object, so make sure we get a string
            if hasattr(response, 'content'):
                response = response.content
            elif not isinstance(response, str):
                response = str(response)
        
        print(f"Raw response from LLM: {response[:100]}...")
        
        # Strip out the thinking part if present
        if "<think>" in response and "</think>" in response:
            response = response.split("</think>")[-1].strip()
        
        return response
    except Exception as e:
        print(f"Error in chat_with_rag: {str(e)}")
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="SFSU CS Department Chatbot") as demo:
    gr.Markdown("# SFSU CS Department Chatbot")
    gr.Markdown("Ask questions about courses, faculty, requirements, and more!")
    
    chatbot = gr.Chatbot(height=500, type="messages")
    msg = gr.Textbox(label="Ask a question", placeholder="e.g., What are the prerequisites for CSC 413?")
    clear = gr.Button("Clear")
    
    # Example questions
    gr.Examples(
        examples=[
            "What are the prerequisites for CSC 413?",
            "Who are the faculty members in the CS department?",
            "What courses are required for the CS major?",
            "When are office hours for CS faculty?",
            "How can I apply to the master's program?"
        ],
        inputs=msg
    )
    
    # Improved respond function with better debugging
    def respond(message, chat_history):
        bot_message = chat_with_rag(message, chat_history)
        
        # Debug: Print the response to console to verify it's working
        print(f"Model response: {bot_message}")
        
        # Make sure we're getting a non-empty response
        if not bot_message or bot_message.strip() == "":
            bot_message = "I'm sorry, I couldn't generate a response for that query. Please try a different question."
        
        # Explicitly append to chat history with the updated format
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot, queue=False)

# Run Gradio app
if __name__ == "__main__":
    demo.launch()