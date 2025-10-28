"""
Simple Data Migration Script - Windows Compatible
Migrates JSON data to Supabase without emoji characters
"""

import json
import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from html import unescape
import re
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

DATA_DIR = "./data"
BATCH_SIZE = 100

print("[*] Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("[OK] Model loaded (384 dimensions)")

print("[*] Connecting to Supabase...")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)
print("[OK] Connected to Supabase")

def clean_html(html_content):
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

def json_to_text(json_obj):
    if isinstance(json_obj, dict):
        text_parts = []
        if "content" in json_obj:
            content = clean_html(json_obj["content"]) if isinstance(json_obj["content"], str) else str(json_obj["content"])
            if "title" in json_obj and json_obj["title"]:
                text_parts.append(f"Title: {json_obj['title']}")
            if "url" in json_obj and json_obj["url"]:
                text_parts.append(f"URL: {json_obj['url']}")
            text_parts.append(f"Content: {content}")
        else:
            for key, value in json_obj.items():
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

print("\n[*] Loading JSON files from data/...")
json_files = list(Path(DATA_DIR).glob("*.json"))
print(f"[OK] Found {len(json_files)} JSON files")

all_documents = []

for file_path in json_files:
    filename = file_path.name
    file_size_mb = file_path.stat().st_size / (1024 * 1024)

    if file_size_mb > 100:
        print(f"[SKIP] {filename} ({file_size_mb:.1f}MB - too large)")
        continue

    print(f"[*] Loading {filename} ({file_size_mb:.1f}MB)...")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            print(f"    Processing {len(data)} items...")
            for idx, item in enumerate(data):
                if idx % 500 == 0 and idx > 0:
                    print(f"    [{idx}/{len(data)}]...")

                try:
                    text = json_to_text(item)
                    if not text or len(text.strip()) < 50:
                        continue

                    metadata = {"source_file": filename, "item_index": idx}
                    url = None
                    title = None

                    if isinstance(item, dict):
                        url = item.get('url') or item.get('link')
                        if 'title' in item:
                            title = item['title']
                            metadata['title'] = title

                    all_documents.append({
                        "content": text[:10000],
                        "source": filename,
                        "url": url,
                        "title": title,
                        "metadata": metadata
                    })
                except Exception as e:
                    print(f"    [WARNING] Error at item {idx}: {e}")
        else:
            text = json_to_text(data)
            if text and len(text.strip()) >= 50:
                all_documents.append({
                    "content": text[:10000],
                    "source": filename,
                    "url": None,
                    "title": None,
                    "metadata": {"source_file": filename}
                })

        print(f"[OK] {filename} processed")

    except Exception as e:
        print(f"[ERROR] Failed to load {filename}: {e}")

print(f"\n[DATA] Total documents created: {len(all_documents)}")

if len(all_documents) == 0:
    print("[ERROR] No documents to migrate!")
    sys.exit(1)

# Auto-confirm for background execution
print(f"\n[*] Proceeding with migration of {len(all_documents)} documents...")

print("\n[*] Generating embeddings...")
texts = [doc["content"] for doc in all_documents]
embeddings_list = []

for i in range(0, len(texts), 32):
    batch = texts[i:i+32]
    batch_embeddings = embedding_model.encode(batch, show_progress_bar=False)
    embeddings_list.extend(batch_embeddings.tolist())
    if (i + 32) % 500 == 0:
        print(f"    [{i+32}/{len(texts)}] embeddings generated...")

for doc, embedding in zip(all_documents, embeddings_list):
    doc["embedding"] = embedding

print(f"[OK] Generated {len(embeddings_list)} embeddings")

print("\n[CLOUD] Uploading to Supabase...")
total_batches = (len(all_documents) + BATCH_SIZE - 1) // BATCH_SIZE
successful = 0
failed = 0

for i in range(0, len(all_documents), BATCH_SIZE):
    batch = all_documents[i:i+BATCH_SIZE]
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

print(f"\n[SUCCESS] Migration complete!")
print(f"  Successful: {successful}")
print(f"  Failed: {failed}")
print(f"  Success rate: {(successful/(successful+failed)*100):.1f}%")
print("\nNext step: Start the backend server!")
