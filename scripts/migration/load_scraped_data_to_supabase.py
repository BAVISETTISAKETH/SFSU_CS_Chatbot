"""
Load scraped SFSU data directly into Supabase vector database
NO Q&A GENERATION NEEDED - Just load and go!
"""

import json
import os
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
import time

load_dotenv()

# Initialize
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Load embedding model (same as your backend uses)
print("Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("[OK] Model loaded!")

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split long text into chunks"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

def load_scraped_data(input_file="data/comprehensive_sfsu_crawl.json", max_docs=None):
    """Load scraped data directly into Supabase"""

    print("\n" + "="*70)
    print("Loading Scraped Data to Supabase Vector Database")
    print("="*70)

    # Load data
    print(f"\n[1/4] Loading scraped data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    print(f"   Loaded {len(pages)} pages")

    # Filter valid pages
    valid_pages = [p for p in pages
                   if p.get('status') == 'success'
                   and p.get('full_text')
                   and len(p.get('full_text', '')) > 200]

    print(f"   Valid pages: {len(valid_pages)}")

    if max_docs:
        valid_pages = valid_pages[:max_docs]
        print(f"   Processing first {max_docs} pages (for testing)")

    # Check existing data
    print(f"\n[2/4] Checking existing documents in database...")
    try:
        result = supabase.table('documents').select('url', count='exact').execute()
        existing_urls = {doc['url'] for doc in result.data}
        print(f"   Found {len(existing_urls)} existing documents")
    except:
        existing_urls = set()
        print(f"   No existing documents found")

    # Process pages
    print(f"\n[3/4] Processing and uploading documents...")
    uploaded = 0
    skipped = 0
    errors = 0

    for i, page in enumerate(valid_pages, 1):
        url = page.get('url', '')
        title = page.get('title', 'No Title')
        full_text = page.get('full_text', '')
        domain = page.get('domain', '')

        # Skip if already exists
        if url in existing_urls:
            skipped += 1
            if i % 100 == 0:
                print(f"   [{i}/{len(valid_pages)}] Skipped: {skipped}, Uploaded: {uploaded}, Errors: {errors}")
            continue

        # Determine category
        if 'cs.sfsu.edu' in domain:
            category = 'cs_general'
        elif 'grad.sfsu.edu' in domain:
            category = 'graduate_programs'
        elif 'bulletin.sfsu.edu' in domain:
            category = 'courses_catalog'
        else:
            category = 'general'

        try:
            # Chunk long texts
            chunks = chunk_text(full_text, chunk_size=1000)

            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = model.encode(chunk).tolist()

                # Create document
                doc = {
                    'content': chunk,
                    'embedding': embedding,
                    'metadata': {
                        'title': title,
                        'category': category,
                        'domain': domain,
                        'chunk_index': chunk_idx,
                        'total_chunks': len(chunks)
                    },
                    'source': 'web_scrape',
                    'url': f"{url}#chunk{chunk_idx}" if len(chunks) > 1 else url,
                    'title': title
                }

                # Upload to Supabase
                supabase.table('documents').insert(doc).execute()
                uploaded += 1

            if i % 100 == 0:
                print(f"   [{i}/{len(valid_pages)}] Uploaded: {uploaded}, Skipped: {skipped}, Errors: {errors}")

        except Exception as e:
            errors += 1
            if i % 100 == 0:
                print(f"   [{i}/{len(valid_pages)}] Error: {str(e)[:50]}")

        # Rate limiting
        if i % 10 == 0:
            time.sleep(0.5)  # Brief pause every 10 pages

    print(f"\n[4/4] Upload complete!")
    print(f"   [OK] Uploaded: {uploaded} documents")
    print(f"   - Skipped: {skipped} (already exist)")
    print(f"   - Errors: {errors}")

    print("\n" + "="*70)
    print("SUCCESS! Your chatbot is ready to use!")
    print("="*70)
    print("\n[NEXT STEPS]:")
    print("1. Start your backend: cd backend && uvicorn main:app --reload")
    print("2. Start your frontend: cd frontend && npm run dev")
    print("3. Test your chatbot!")
    print("\nNo Q&A generation needed - RAG works with raw documents!")

if __name__ == "__main__":
    # Load all data (or set max_docs=100 for testing)
    load_scraped_data(
        input_file="data/comprehensive_sfsu_crawl.json",
        max_docs=None  # Set to 100 for quick test, None for all data
    )
