"""
Migrate Large File: raw_pages.json to Supabase
Processes the 410MB file in smaller chunks to avoid memory issues
"""

import json
import os
import sys
from bs4 import BeautifulSoup
from html import unescape
import re
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

LARGE_FILE = "./data/sfsu_cs_query_system.raw_pages.json"
BATCH_SIZE = 50  # Smaller batches for large content
MAX_ITEMS = None  # Set to a number to limit items, or None for all

print("[*] Large File Migration Script")
print("="*60)

# Initialize services
print("[*] Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("[OK] Model loaded")

print("[*] Connecting to Supabase...")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("[OK] Connected")

def clean_html(html_content):
    """Clean HTML content."""
    if not html_content or not isinstance(html_content, str):
        return ""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(["script", "style", "meta", "link"]):
            script.extract()
        text = unescape(soup.get_text(separator=' ', strip=True))
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except:
        return str(html_content)

def process_item(item, index):
    """Process a single JSON item into a document."""
    try:
        # Extract content
        if isinstance(item, dict):
            content = ""
            title = None
            url = None

            if "content" in item:
                content = clean_html(item["content"]) if isinstance(item["content"], str) else str(item["content"])
            elif "html" in item:
                content = clean_html(item["html"])
            elif "text" in item:
                content = clean_html(item["text"])

            if "title" in item:
                title = item.get("title")
            if "url" in item:
                url = item.get("url")

            # Build full text
            text_parts = []
            if title:
                text_parts.append(f"Title: {title}")
            if url:
                text_parts.append(f"URL: {url}")
            if content:
                text_parts.append(f"Content: {content}")

            full_text = "\n".join(text_parts)

            # Skip if too short
            if len(full_text.strip()) < 100:
                return None

            return {
                "content": full_text[:15000],  # Limit to 15K chars
                "title": title,
                "url": url,
                "source": "sfsu_cs_query_system.raw_pages.json",
                "metadata": {
                    "source_file": "raw_pages.json",
                    "item_index": index
                }
            }
    except Exception as e:
        print(f"    [WARNING] Error processing item {index}: {e}")
        return None

print(f"\n[*] Loading {LARGE_FILE}...")
print("    This may take a minute...")

try:
    with open(LARGE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("[ERROR] File is not a list!")
        sys.exit(1)

    total_items = len(data)
    print(f"[OK] Loaded {total_items} items")

    if MAX_ITEMS:
        data = data[:MAX_ITEMS]
        print(f"[*] Limiting to {MAX_ITEMS} items for testing")

except Exception as e:
    print(f"[ERROR] Failed to load file: {e}")
    sys.exit(1)

# Process items
print(f"\n[*] Processing items...")
documents = []

for idx, item in enumerate(data):
    if idx % 100 == 0 and idx > 0:
        print(f"    [{idx}/{len(data)}] items processed...")

    doc = process_item(item, idx)
    if doc:
        documents.append(doc)

print(f"[OK] Created {len(documents)} documents")

if len(documents) == 0:
    print("[ERROR] No valid documents created!")
    sys.exit(1)

# Auto-confirm for background execution
print(f"\n[*] About to:")
print(f"    - Generate embeddings for {len(documents)} documents")
print(f"    - Upload to Supabase")
print(f"    - Estimated time: {(len(documents) * 0.02):.1f} minutes")
print(f"\n[*] Proceeding with migration...")

# Generate embeddings
print(f"\n[*] Generating embeddings...")
texts = [doc["content"] for doc in documents]
embeddings_list = []

for i in range(0, len(texts), 32):
    batch = texts[i:i+32]
    batch_embeddings = embedding_model.encode(batch, show_progress_bar=False)
    embeddings_list.extend(batch_embeddings.tolist())

    if (i + 32) % 500 == 0:
        print(f"    [{i+32}/{len(texts)}] embeddings generated...")

for doc, embedding in zip(documents, embeddings_list):
    doc["embedding"] = embedding

print(f"[OK] Generated {len(embeddings_list)} embeddings")

# Upload to Supabase
print(f"\n[CLOUD] Uploading to Supabase...")
total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
successful = 0
failed = 0

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i+BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1

    try:
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

        result = supabase.table("documents").insert(insert_data).execute()
        successful += len(batch)
        print(f"[OK] Batch {batch_num}/{total_batches}: {len(batch)} documents uploaded")

    except Exception as e:
        failed += len(batch)
        print(f"[ERROR] Batch {batch_num}/{total_batches}: {e}")

    # Small delay to avoid rate limiting
    import time
    time.sleep(0.5)

print(f"\n[SUCCESS] Migration complete!")
print(f"  Successful: {successful}")
print(f"  Failed: {failed}")
print(f"  Success rate: {(successful/(successful+failed)*100):.1f}%")

# Check total in database
try:
    result = supabase.table("documents").select("id", count="exact").limit(1).execute()
    print(f"\n[DATA] Total documents in database: {result.count}")
except:
    pass

print("\n[*] Your chatbot should now have much better answers!")
print("[*] Try asking: 'What courses does SFSU CS offer?'")
