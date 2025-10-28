"""
Generate Q&A Training Data using Local LLMs via Ollama
NO RATE LIMITS - Completely Free & Fast

Setup:
1. Install Ollama: https://ollama.com/download
2. Run: ollama pull llama3.2
3. Run this script: python generate_qa_with_ollama.py

Advantages:
- No API costs
- No rate limits
- Fast (runs on your GPU/CPU)
- Works offline
- Privacy (data stays local)
"""

import json
import os
from dotenv import load_dotenv
import time
import requests

load_dotenv()

def call_ollama(prompt, model='llama3.2', temperature=0.7):
    """
    Call local Ollama model.

    Models to try:
    - llama3.2 (3B) - Fast, good quality
    - llama3.2:3b - Same as above
    - mistral - Very good quality
    - phi3 - Microsoft's model, very fast
    """

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 4000,  # Increased to allow more Q&A pairs per response
            "num_thread": 0  # Auto-detect optimal threads for CPU
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['response'].strip()
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama not running. Start it with: ollama serve")
    except Exception as e:
        raise Exception(f"Ollama error: {e}")

def extract_qa_pairs(page, model='llama3.2'):
    """
    Use local LLM to extract Q&A pairs from a scraped page.
    """

    # Get data from scraped page
    url = page.get('url', '')
    title = page.get('title', 'No Title')
    full_text = page.get('full_text', '')
    domain = page.get('domain', '')

    # Skip if no content
    if not full_text or len(full_text) < 200:
        return []

    # Determine category from domain
    if 'cs.sfsu.edu' in domain:
        category = 'cs_general'
    elif 'grad.sfsu.edu' in domain:
        category = 'graduate_programs'
    elif 'bulletin.sfsu.edu' in domain:
        category = 'courses_catalog'
    elif 'oip.sfsu.edu' in domain or 'international' in domain:
        category = 'international_students'
    elif 'financial' in domain:
        category = 'financial_aid'
    elif 'housing' in domain:
        category = 'housing'
    elif 'registrar' in domain:
        category = 'registration'
    elif 'career' in domain:
        category = 'career_services'
    else:
        category = 'general'

    # Split long content into chunks to extract more Q&A pairs
    chunk_size = 2500
    chunks = []

    if len(full_text) > chunk_size:
        # Split into overlapping chunks to not miss context
        for i in range(0, len(full_text), chunk_size - 200):  # 200 char overlap
            chunk = full_text[i:i + chunk_size]
            if len(chunk) > 300:  # Only process substantial chunks
                chunks.append(chunk)
    else:
        chunks = [full_text]

    all_qa_pairs = []

    for chunk_idx, chunk in enumerate(chunks):
        prompt = f"""You are creating training data for an SFSU chatbot. Extract AS MANY natural questions and comprehensive answers as possible from this content.

URL: {url}
Title: {title}
Category: {category}
Chunk: {chunk_idx + 1}/{len(chunks)}

Content:
{chunk}

Instructions:
- Extract EVERY possible question a student might ask about this content
- Include questions about: facts, procedures, requirements, deadlines, eligibility, programs, resources, etc.
- Create detailed answers with ALL relevant information
- Extract AT LEAST 5-10 Q&A pairs if content is substantial
- More is better! Extract everything useful.

Output ONLY valid JSON array:
[
  {{
    "question": "Natural student question?",
    "answer": "Comprehensive answer with specific details",
    "category": "{category}",
    "source_url": "{url}"
  }}
]

JSON:"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = call_ollama(prompt, model)

                # Extract JSON
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0].strip()
                elif '```' in result:
                    result = result.split('```')[1].split('```')[0].strip()

                # Try to parse JSON
                qa_pairs = json.loads(result)

                # Validate structure
                if isinstance(qa_pairs, list) and len(qa_pairs) > 0:
                    # Ensure all required fields exist
                    valid_pairs = []
                    for pair in qa_pairs:
                        if isinstance(pair, dict) and 'question' in pair and 'answer' in pair:
                            # Add missing fields
                            if 'category' not in pair:
                                pair['category'] = category
                            if 'source_url' not in pair:
                                pair['source_url'] = url
                            valid_pairs.append(pair)

                    if valid_pairs:
                        all_qa_pairs.extend(valid_pairs)
                        break  # Success, move to next chunk

                # If we get here, the response was not valid - retry
                if attempt < max_retries - 1:
                    print(f"   [RETRY chunk {chunk_idx+1}] Attempt {attempt + 2}/{max_retries}")
                    continue

            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    print(f"   [JSON ERROR chunk {chunk_idx+1}] Retry {attempt + 2}/{max_retries}")
                    # Try with more explicit prompt
                    if attempt == 1:
                        prompt += "\n\nIMPORTANT: Return ONLY valid JSON array, no other text."
                    continue
                else:
                    print(f"   [ERROR] Chunk {chunk_idx+1} failed after {max_retries} attempts")
            except Exception as e:
                print(f"   [ERROR chunk {chunk_idx+1}] {str(e)[:100]}")
                break

    return all_qa_pairs

def process_with_ollama(input_file="data/comprehensive_sfsu_crawl.json",
                        output_file="data/qa_training_data.json",
                        model='llama3.2',
                        max_pages=None,
                        resume=True):
    """
    Process comprehensive scraped data using local Ollama models.

    Args:
        input_file: Path to comprehensive scrape JSON
        output_file: Path to save Q&A pairs
        model: Ollama model name (llama3.2, mistral, phi3)
        max_pages: Maximum pages to process (None = all)
        resume: Continue from existing output file
    """

    print("="*70)
    print("Local LLM Q&A Generator for SFSU Chatbot (via Ollama)")
    print("="*70)
    print(f"[MODEL] Using: {model}")
    print(f"[INFO] No rate limits - Unlimited generation!")
    print()

    # Test Ollama connection
    try:
        test = call_ollama("Say 'OK'", model)
        print(f"[TEST] Ollama connection: OK")
        print(f"[TEST] Model response: {test[:50]}")
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n[SETUP INSTRUCTIONS]")
        print("1. Download Ollama: https://ollama.com/download")
        print("2. Install and start Ollama")
        print(f"3. Run: ollama pull {model}")
        print("4. Run this script again")
        return []

    # Load existing Q&A pairs if resuming
    existing_qa_pairs = []
    processed_urls = set()

    if resume and os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_qa_pairs = json.load(f)
            processed_urls = {qa.get('source_url') for qa in existing_qa_pairs}
        print(f"[RESUME] Found {len(existing_qa_pairs)} existing Q&A pairs from {len(processed_urls)} pages")
        print()

    # Load scraped data
    print(f"[LOAD] Loading scraped data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    print(f"[DATA] Loaded {len(pages)} scraped pages")

    # Filter to successful pages with content
    valid_pages = [p for p in pages if p.get('status') == 'success' and
                   p.get('full_text') and len(p.get('full_text', '')) > 200 and
                   p.get('url') not in processed_urls]

    print(f"[FILTER] {len(valid_pages)} pages available for processing")

    if max_pages and max_pages < len(valid_pages):
        valid_pages = valid_pages[:max_pages]
        print(f"[LIMIT] Processing first {len(valid_pages)} pages")

    # Process pages
    all_qa_pairs = existing_qa_pairs.copy()
    errors = 0

    print(f"\n[PROCESS] Generating Q&A pairs from {len(valid_pages)} pages...")
    # With Ollama on GPU: ~5 seconds per page, ~3 minutes for 100 pages
    if len(valid_pages) > 0:
        estimated_mins = (len(valid_pages) * 5) / 60
        print(f"[INFO] Estimated time: {estimated_mins:.0f} minutes (with GPU)")
    print()

    start_time = time.time()

    for i, page in enumerate(valid_pages, 1):
        title = page.get('title', 'Untitled')[:60]

        print(f"[{i}/{len(valid_pages)}] {title}...")

        try:
            qa_pairs = extract_qa_pairs(page, model)

            if qa_pairs:
                all_qa_pairs.extend(qa_pairs)
                print(f"   [OK] +{len(qa_pairs)} Q&A pairs (Total: {len(all_qa_pairs)})")
            else:
                errors += 1
                print(f"   [SKIP] No pairs extracted")

        except Exception as e:
            errors += 1
            print(f"   [ERROR] {str(e)[:100]}")

        # Auto-save every 10 pages
        if i % 10 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (len(valid_pages) - i) / rate if rate > 0 else 0

            print(f"\n[SAVE] Progress checkpoint: {len(all_qa_pairs)} Q&A pairs")
            print(f"[SPEED] {rate:.1f} pages/sec | ETA: {remaining/60:.0f} minutes")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
            print()

    # Final save
    print(f"\n{'='*70}")
    print("COMPLETE!")
    print("="*70)
    print(f"[SUCCESS] Generated {len(all_qa_pairs)} Q&A pairs total")
    print(f"[STATS] Success rate: {((len(valid_pages)-errors)/len(valid_pages)*100):.1f}%")
    print(f"[TIME] Total time: {(time.time()-start_time)/60:.1f} minutes")
    print(f"[SAVE] Saving to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)

    # Show samples
    if all_qa_pairs:
        print(f"\n[SAMPLES] Recent Q&A pairs:")
        for qa in all_qa_pairs[-3:]:
            print(f"\nQ: {qa['question']}")
            print(f"A: {qa['answer'][:150]}...")
            print(f"Category: {qa['category']}")

    return all_qa_pairs

if __name__ == "__main__":
    # Process with local Ollama model
    qa_pairs = process_with_ollama(
        input_file="data/comprehensive_sfsu_crawl.json",
        output_file="data/qa_training_data.json",
        model='llama3.2',  # Fast and good quality
        max_pages=None,  # Process ALL pages (no limits!)
        resume=True  # Continue from where we left off
    )

    print(f"\n{'='*70}")
    print(f"[FINAL] Total Q&A pairs: {len(qa_pairs)}")
    print(f"[FILE] Saved to: data/qa_training_data.json")
    print(f"\n[NEXT STEPS]:")
    print(f"1. Review Q&A pairs: data/qa_training_data.json")
    print(f"2. Upload to Supabase: python upload_qa_training_data.py")
    print("="*70)
