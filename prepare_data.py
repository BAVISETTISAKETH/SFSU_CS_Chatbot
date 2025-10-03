import json
import os
import re
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from html import unescape

# Suppress XML warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Define paths
JSON_DIR = "./data"
DB_DIR = "./vector_db"

def clean_html(html_content):
    """Clean HTML content by removing tags and formatting the text."""
    if not html_content or not isinstance(html_content, str):
        return ""
    
    # Use BeautifulSoup to parse and clean HTML
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text and unescape HTML entities
        text = unescape(soup.get_text(separator=' ', strip=True))
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"Error cleaning HTML: {e}")
        return html_content  # Return original if parsing fails

def json_to_text(json_obj):
    """Convert a JSON object to text with improved HTML cleaning."""
    if isinstance(json_obj, dict):
        text_parts = []
        
        # Handle special cases for different data types
        if "content" in json_obj and isinstance(json_obj["content"], str):
            # This looks like a document with HTML content
            content = clean_html(json_obj["content"])
            if "title" in json_obj:
                text_parts.append(f"Title: {json_obj['title']}")
            if "url" in json_obj:
                text_parts.append(f"URL: {json_obj['url']}")
            text_parts.append(f"Content: {content}")
        else:
            # Process regular dictionary
            for key, value in json_obj.items():
                if key.lower() in ['html', 'content', 'body', 'text'] and isinstance(value, str):
                    # Clean HTML content
                    value = clean_html(value)
                elif isinstance(value, (dict, list)):
                    # Recursively process nested objects
                    value = json_to_text(value)
                
                text_parts.append(f"{key}: {value}")
        
        return "\n".join(text_parts)
    
    elif isinstance(json_obj, list):
        # For lists, process each item
        text_parts = []
        for item in json_obj:
            item_text = json_to_text(item)
            text_parts.append(item_text)
        return "\n\n".join(text_parts)
    
    else:
        return str(json_obj)

def load_json_files():
    all_data = []
    for filename in os.listdir(JSON_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(JSON_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    all_data.append((filename, data))
                    print(f"Successfully loaded: {filename}")
            except json.JSONDecodeError as e:
                print(f"Error loading {filename}: {str(e)}")
                print(f"Please check the JSON formatting in this file")
    return all_data

def process_json_to_documents(json_data):
    documents = []
    total_files = len(json_data)
    
    for idx, (filename, data) in enumerate(json_data):
        print(f"Processing file {idx+1}/{total_files}: {filename}")
        
        # Process each JSON file
        if isinstance(data, list):
            # If the JSON is a list of objects
            for item_idx, item in enumerate(data):
                if item_idx % 100 == 0:
                    print(f"  Processing item {item_idx}/{len(data)}")
                text = json_to_text(item)
                doc = Document(
                    page_content=text,
                    metadata={"source": filename}
                )
                documents.append(doc)
        else:
            # If the JSON is a single object
            text = json_to_text(data)
            doc = Document(
                page_content=text,
                metadata={"source": filename}
            )
            documents.append(doc)
    
    return documents

def split_documents(documents):
    print(f"Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks

class SentenceTransformerEmbeddings:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self, texts):
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
        
    def embed_query(self, text):
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

def create_vector_db(chunks):
    print(f"Creating vector database with {len(chunks)} chunks...")
    
    # Use SentenceTransformer embeddings (GPU-accelerated)
    embeddings = SentenceTransformerEmbeddings()
    
    # Process in batches
    batch_size = 1000
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    # Create initial vectorstore with first batch
    print(f"Processing batch 1/{total_batches}")
    first_batch = chunks[:batch_size]
    vectordb = Chroma.from_documents(
        documents=first_batch,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    # Process remaining batches
    for i in range(1, total_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(chunks))
        batch = chunks[start_idx:end_idx]
        
        print(f"Processing batch {i+1}/{total_batches}")
        vectordb.add_documents(batch)
    
    print("Vector database creation complete")
    return vectordb

def main():
    # Create directories if they don't exist
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    
    print("Loading JSON files...")
    json_data = load_json_files()
    
    print("Processing JSON to documents...")
    documents = process_json_to_documents(json_data)
    
    print(f"Total documents: {len(documents)}")
    
    # Process ALL documents (not just a subset)
    chunks = split_documents(documents)
    vectordb = create_vector_db(chunks)
    
    print(f"Vector database created and saved to {DB_DIR}")

if __name__ == "__main__":
    main()