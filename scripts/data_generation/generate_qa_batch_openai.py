"""
Generate Q&A Training Data using OpenAI Batch API
50% CHEAPER than regular API, processes overnight

Advantages:
- 50% discount on API costs
- No rate limits (batches process in 24 hours)
- Can process 1000s of pages at once
- Automatic retry on failures

Setup:
1. Add OpenAI credits: https://platform.openai.com/account/billing
2. Run: python generate_qa_batch_openai.py create
3. Wait 24 hours
4. Run: python generate_qa_batch_openai.py retrieve
"""

import json
import os
from dotenv import load_dotenv
import time
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_batch_job(input_file="data/comprehensive_sfsu_crawl.json",
                     output_file="batch_requests.jsonl",
                     max_pages=None,
                     resume=True):
    """
    Create batch job file for OpenAI Batch API.
    """

    print("="*70)
    print("OpenAI Batch API - Q&A Generator Setup")
    print("="*70)

    # Load existing Q&A pairs if resuming
    processed_urls = set()
    if resume and os.path.exists("data/qa_training_data.json"):
        with open("data/qa_training_data.json", 'r', encoding='utf-8') as f:
            existing_qa_pairs = json.load(f)
            processed_urls = {qa.get('source_url') for qa in existing_qa_pairs}
        print(f"[RESUME] Found {len(existing_qa_pairs)} existing pairs from {len(processed_urls)} pages")

    # Load scraped data
    print(f"[LOAD] Loading scraped data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    # Filter valid pages
    valid_pages = [p for p in pages if p.get('status') == 'success' and
                   p.get('full_text') and len(p.get('full_text', '')) > 200 and
                   p.get('url') not in processed_urls]

    if max_pages:
        valid_pages = valid_pages[:max_pages]

    print(f"[PAGES] Processing {len(valid_pages)} pages")

    # Create batch request file
    batch_requests = []

    for i, page in enumerate(valid_pages):
        url = page.get('url', '')
        title = page.get('title', 'No Title')
        full_text = page.get('full_text', '')
        domain = page.get('domain', '')

        # Determine category
        if 'cs.sfsu.edu' in domain:
            category = 'cs_general'
        elif 'grad.sfsu.edu' in domain:
            category = 'graduate_programs'
        elif 'bulletin.sfsu.edu' in domain:
            category = 'courses_catalog'
        else:
            category = 'general'

        # Truncate content
        if len(full_text) > 3000:
            full_text = full_text[:3000] + "..."

        prompt = f"""You are creating training data for an SFSU chatbot. Extract 2-3 natural questions and comprehensive answers from this content.

URL: {url}
Title: {title}
Category: {category}

Content:
{full_text}

Create realistic questions that SFSU students would ask, with detailed answers from the content.

Output ONLY valid JSON:
[
  {{
    "question": "Natural student question?",
    "answer": "Comprehensive answer with specific details",
    "category": "{category}",
    "source_url": "{url}"
  }}
]

JSON:"""

        # Create batch request
        request = {
            "custom_id": f"page-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
        }

        batch_requests.append(request)

    # Save batch file
    with open(output_file, 'w', encoding='utf-8') as f:
        for req in batch_requests:
            f.write(json.dumps(req) + '\n')

    print(f"[SAVED] Batch file: {output_file}")
    print(f"[COUNT] {len(batch_requests)} requests")

    # Upload batch file to OpenAI
    print("\n[UPLOAD] Uploading batch file to OpenAI...")
    with open(output_file, 'rb') as f:
        batch_input_file = client.files.create(file=f, purpose="batch")

    print(f"[FILE ID] {batch_input_file.id}")

    # Create batch job
    print("[BATCH] Creating batch job...")
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )

    print(f"\n{'='*70}")
    print("BATCH JOB CREATED!")
    print("="*70)
    print(f"[BATCH ID] {batch.id}")
    print(f"[STATUS] {batch.status}")
    print(f"[REQUESTS] {len(batch_requests)} pages")
    print(f"\nSave this batch ID: {batch.id}")
    print(f"\nCheck status:")
    print(f"  python generate_qa_batch_openai.py status {batch.id}")
    print(f"\nRetrieve results (after completion):")
    print(f"  python generate_qa_batch_openai.py retrieve {batch.id}")
    print("="*70)

    # Save batch ID
    with open("batch_id.txt", 'w') as f:
        f.write(batch.id)

    return batch.id

def check_status(batch_id):
    """Check batch job status."""
    batch = client.batches.retrieve(batch_id)

    print(f"[STATUS] {batch.status}")
    print(f"[REQUESTS] Total: {batch.request_counts.total}")
    print(f"[COMPLETED] {batch.request_counts.completed}")
    print(f"[FAILED] {batch.request_counts.failed}")

    if batch.status == "completed":
        print(f"\n[SUCCESS] Batch completed!")
        print(f"Retrieve results: python generate_qa_batch_openai.py retrieve {batch_id}")

    return batch

def retrieve_results(batch_id, output_file="data/qa_training_data.json"):
    """Retrieve and process batch results."""

    print("[RETRIEVE] Fetching batch results...")
    batch = client.batches.retrieve(batch_id)

    if batch.status != "completed":
        print(f"[ERROR] Batch not completed yet. Status: {batch.status}")
        return

    # Download results
    result_file_id = batch.output_file_id
    result = client.files.content(result_file_id)

    # Parse results
    all_qa_pairs = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            all_qa_pairs = json.load(f)

    print(f"[EXISTING] {len(all_qa_pairs)} Q&A pairs")

    # Process each result
    lines = result.text.strip().split('\n')
    for line in lines:
        try:
            result_obj = json.loads(line)
            content = result_obj['response']['body']['choices'][0]['message']['content']

            # Extract JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            qa_pairs = json.loads(content)
            all_qa_pairs.extend(qa_pairs)
        except Exception as e:
            print(f"[ERROR] Parsing result: {e}")

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Retrieved {len(all_qa_pairs)} total Q&A pairs")
    print(f"[SAVED] {output_file}")

    return all_qa_pairs

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Create batch:  python generate_qa_batch_openai.py create")
        print("  Check status:  python generate_qa_batch_openai.py status <batch_id>")
        print("  Get results:   python generate_qa_batch_openai.py retrieve <batch_id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        create_batch_job(max_pages=None)  # Process all pages

    elif command == "status":
        if len(sys.argv) < 3:
            # Try to load from file
            if os.path.exists("batch_id.txt"):
                with open("batch_id.txt") as f:
                    batch_id = f.read().strip()
            else:
                print("Error: Provide batch ID")
                sys.exit(1)
        else:
            batch_id = sys.argv[2]
        check_status(batch_id)

    elif command == "retrieve":
        if len(sys.argv) < 3:
            if os.path.exists("batch_id.txt"):
                with open("batch_id.txt") as f:
                    batch_id = f.read().strip()
            else:
                print("Error: Provide batch ID")
                sys.exit(1)
        else:
            batch_id = sys.argv[2]
        retrieve_results(batch_id)
