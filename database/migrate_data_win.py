"""
Data Migration Script: JSON Files → Supabase PostgreSQL
Migrates all your SFSU CS data from JSON files to cloud database with vector embeddings
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
from html import unescape
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = "./data"
BATCH_SIZE = 100  # Process 100 documents at a time
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize embedding model
print("🔄 Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print(f"[OK] Loaded {EMBEDDING_MODEL} (384 dimensions)")


def clean_html(html_content: str) -> str:
    """Clean HTML content and extract readable text."""
    if not html_content or not isinstance(html_content, str):
        return ""

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.extract()

        # Get text and unescape HTML entities
        text = unescape(soup.get_text(separator=' ', strip=True))

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"[WARNING]  Warning: Error cleaning HTML: {e}")
        return str(html_content)


def json_to_text(json_obj: Any) -> str:
    """Convert JSON object to clean text format."""
    if isinstance(json_obj, dict):
        text_parts = []

        # Handle documents with content
        if "content" in json_obj:
            content = clean_html(json_obj["content"]) if isinstance(json_obj["content"], str) else str(json_obj["content"])
            if "title" in json_obj and json_obj["title"]:
                text_parts.append(f"Title: {json_obj['title']}")
            if "url" in json_obj and json_obj["url"]:
                text_parts.append(f"URL: {json_obj['url']}")
            text_parts.append(f"Content: {content}")
        else:
            # Process regular dictionary
            for key, value in json_obj.items():
                # Skip MongoDB IDs and internal fields
                if key in ['_id', 'discovered_at', 'processed_at', 'priority', 'processed', 'source_url']:
                    continue

                if key.lower() in ['html', 'body', 'text'] and isinstance(value, str):
                    value = clean_html(value)
                elif isinstance(value, (dict, list)):
                    value = json_to_text(value)

                text_parts.append(f"{key}: {value}")

        return "\n".join(text_parts)

    elif isinstance(json_obj, list):
        return "\n\n".join([json_to_text(item) for item in json_obj])

    else:
        return str(json_obj)


def load_json_files() -> List[tuple]:
    """Load all JSON files from data directory."""
    all_data = []
    json_files = list(Path(DATA_DIR).glob("*.json"))

    print(f"\n📂 Found {len(json_files)} JSON files in {DATA_DIR}/")

    for file_path in json_files:
        filename = file_path.name

        # Skip very large files for initial migration (can process separately)
        file_size_mb = file_path.stat().st_size / (1024 * 1024)

        if file_size_mb > 100:
            print(f"[SKIP]  Skipping {filename} ({file_size_mb:.1f}MB - too large for batch processing)")
            print(f"   💡 Process this file separately with: python migrate_data.py --file {filename}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.append((filename, data, file_size_mb))
                print(f"[OK] Loaded: {filename} ({file_size_mb:.1f}MB)")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error loading {filename}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error loading {filename}: {e}")

    return all_data


def process_json_to_documents(json_data: List[tuple]) -> List[Dict]:
    """Convert JSON data to document format."""
    documents = []
    total_files = len(json_data)

    print(f"\n🔄 Processing {total_files} files into documents...")

    for idx, (filename, data, file_size) in enumerate(json_data):
        print(f"\n📄 Processing file {idx+1}/{total_files}: {filename}")

        if isinstance(data, list):
            total_items = len(data)
            print(f"   📊 Contains {total_items} items")

            for item_idx, item in enumerate(data):
                if item_idx % 500 == 0 and item_idx > 0:
                    print(f"   [WAIT] Processed {item_idx}/{total_items} items...")

                try:
                    text = json_to_text(item)

                    # Skip empty documents
                    if not text or len(text.strip()) < 50:
                        continue

                    # Extract metadata
                    metadata = {
                        "source_file": filename,
                        "item_index": item_idx
                    }

                    # Extract URL if present
                    url = None
                    if isinstance(item, dict):
                        url = item.get('url') or item.get('link')
                        if 'title' in item:
                            metadata['title'] = item['title']

                    documents.append({
                        "content": text[:10000],  # Limit content to 10K chars
                        "source": filename,
                        "url": url,
                        "title": metadata.get('title'),
                        "metadata": metadata
                    })

                except Exception as e:
                    print(f"   [WARNING]  Error processing item {item_idx}: {e}")
                    continue

        else:
            # Single object
            text = json_to_text(data)
            if text and len(text.strip()) >= 50:
                documents.append({
                    "content": text[:10000],
                    "source": filename,
                    "url": None,
                    "title": None,
                    "metadata": {"source_file": filename}
                })

    print(f"\n[OK] Created {len(documents)} documents")
    return documents


def generate_embeddings(documents: List[Dict]) -> List[Dict]:
    """Generate vector embeddings for all documents."""
    print(f"\n🧮 Generating embeddings for {len(documents)} documents...")

    # Extract texts
    texts = [doc["content"] for doc in documents]

    # Generate embeddings in batches
    all_embeddings = []
    batch_size = 32

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embedding_model.encode(batch_texts, show_progress_bar=False)
        all_embeddings.extend(batch_embeddings.tolist())

        if (i + batch_size) % 500 == 0:
            print(f"   [WAIT] Generated {i+batch_size}/{len(texts)} embeddings...")

    # Add embeddings to documents
    for doc, embedding in zip(documents, all_embeddings):
        doc["embedding"] = embedding

    print(f"[OK] Generated all embeddings")
    return documents


def upload_to_supabase(documents: List[Dict]):
    """Upload documents to Supabase in batches."""
    print(f"\n[CLOUD]  Uploading {len(documents)} documents to Supabase...")

    total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
    successful = 0
    failed = 0

    for i in range(0, len(documents), BATCH_SIZE):
        batch = documents[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1

        try:
            # Prepare batch for insertion
            insert_data = []
            for doc in batch:
                insert_data.append({
                    "content": doc["content"],
                    "embedding": doc["embedding"],
                    "source": doc["source"],
                    "url": doc.get("url"),
                    "title": doc.get("title"),
                    "metadata": doc["metadata"]
                })

            # Insert batch
            result = supabase.table("documents").insert(insert_data).execute()
            successful += len(batch)
            print(f"   [OK] Batch {batch_num}/{total_batches}: Uploaded {len(batch)} documents")

        except Exception as e:
            failed += len(batch)
            print(f"   [ERROR] Batch {batch_num}/{total_batches}: Failed - {e}")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    print(f"\n📊 Upload complete:")
    print(f"   [OK] Successful: {successful}")
    print(f"   [ERROR] Failed: {failed}")
    print(f"   📈 Success rate: {(successful/(successful+failed)*100):.1f}%")


def check_database_connection():
    """Check if database connection works."""
    print("\n🔌 Testing Supabase connection...")
    try:
        # Try a simple query
        result = supabase.table("documents").select("count", count="exact").limit(1).execute()
        print(f"[OK] Connected! Current document count: {result.count}")
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\n💡 Make sure you:")
        print("   1. Created the database schema (run schema.sql in Supabase SQL Editor)")
        print("   2. Have correct SUPABASE_URL and SUPABASE_KEY in .env file")
        return False


def main():
    """Main migration process."""
    print("=" * 70)
    print("🚀 SFSU CS Chatbot - Data Migration to Supabase")
    print("=" * 70)

    # Check database connection
    if not check_database_connection():
        return

    # Load JSON files
    json_data = load_json_files()

    if not json_data:
        print("\n[ERROR] No JSON files found to process!")
        return

    # Process to documents
    documents = process_json_to_documents(json_data)

    if not documents:
        print("\n[ERROR] No documents created from JSON files!")
        return

    # Confirm before proceeding
    print(f"\n[WARNING]  About to:")
    print(f"   - Generate embeddings for {len(documents)} documents")
    print(f"   - Upload to Supabase database")
    print(f"   - Estimated time: {(len(documents) * 0.01):.1f} minutes")

    response = input("\n✋ Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("[ERROR] Migration cancelled")
        return

    # Generate embeddings
    documents_with_embeddings = generate_embeddings(documents)

    # Upload to Supabase
    upload_to_supabase(documents_with_embeddings)

    print("\n" + "=" * 70)
    print("🎉 Migration Complete!")
    print("=" * 70)
    print("\n[OK] Next steps:")
    print("   1. Verify data in Supabase dashboard")
    print("   2. Test the backend API: python backend/main.py")
    print("   3. Build and deploy frontend")


if __name__ == "__main__":
    main()
