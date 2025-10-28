"""
Generate Q&A Training Data from Comprehensive SFSU Scrape
Processes the comprehensive_sfsu_crawl.json file (4000 pages)
"""

import json
import os
from groq import Groq
from dotenv import load_dotenv
import time
import random

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_qa_pairs(page, max_pairs=3):
    """
    Use LLM to extract Q&A pairs from a scraped page.
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

    # Truncate long content
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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500,
            timeout=30
        )

        result = response.choices[0].message.content.strip()

        # Extract JSON
        if '```json' in result:
            result = result.split('```json')[1].split('```')[0].strip()
        elif '```' in result:
            result = result.split('```')[1].split('```')[0].strip()

        qa_pairs = json.loads(result)
        return qa_pairs

    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"   [ERROR] {str(e)[:100]}")
        return []

def process_comprehensive_data(input_file="data/comprehensive_sfsu_crawl.json",
                               output_file="data/qa_training_data.json",
                               max_pages=None,
                               sample_strategy='diverse'):
    """
    Process comprehensive scraped data to generate Q&A pairs.

    Args:
        input_file: Path to comprehensive scrape JSON
        output_file: Path to save Q&A pairs
        max_pages: Maximum pages to process (None = all)
        sample_strategy: 'diverse' or 'sequential'
    """

    print("[AI] Comprehensive SFSU Q&A Generator")
    print("=" * 60)

    # Load scraped data
    print(f"[LOAD] Loading scraped data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        pages = json.load(f)

    print(f"[DATA] Loaded {len(pages)} scraped pages")

    # Filter to successful pages with content
    valid_pages = [p for p in pages if p.get('status') == 'success' and
                   p.get('full_text') and len(p.get('full_text', '')) > 200]

    print(f"[FILTER] {len(valid_pages)} pages have sufficient content")

    # Sample pages if needed
    if max_pages and max_pages < len(valid_pages):
        if sample_strategy == 'diverse':
            # Sample from different domains
            domains = {}
            for p in valid_pages:
                domain = p.get('domain', 'unknown')
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(p)

            # Sample proportionally from each domain
            sampled_pages = []
            per_domain = max_pages // len(domains)
            for domain, domain_pages in domains.items():
                sample_size = min(per_domain, len(domain_pages))
                sampled_pages.extend(random.sample(domain_pages, sample_size))

            valid_pages = sampled_pages[:max_pages]
            print(f"[SAMPLE] Selected {len(valid_pages)} diverse pages across domains")
        else:
            valid_pages = valid_pages[:max_pages]
            print(f"[SAMPLE] Processing first {len(valid_pages)} pages")

    # Process pages
    all_qa_pairs = []
    errors = 0

    print(f"\n[PROCESS] Generating Q&A pairs from {len(valid_pages)} pages...")
    print("[INFO] This will take approximately {:.0f} minutes".format(len(valid_pages) * 1.5 / 60))
    print()

    for i, page in enumerate(valid_pages, 1):
        title = page.get('title', 'Untitled')[:60]
        url = page.get('url', '')

        print(f"[{i}/{len(valid_pages)}] {title}...")

        qa_pairs = extract_qa_pairs(page)

        if qa_pairs:
            all_qa_pairs.extend(qa_pairs)
            print(f"   [OK] +{len(qa_pairs)} Q&A pairs (Total: {len(all_qa_pairs)})")
        else:
            errors += 1
            print(f"   [SKIP] No pairs extracted")

        # Rate limiting
        time.sleep(1.2)

        # Auto-save every 10 pages
        if i % 10 == 0:
            print(f"\n[SAVE] Progress checkpoint: {len(all_qa_pairs)} Q&A pairs")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
            print()

    # Final save
    print(f"\n[COMPLETE] Generated {len(all_qa_pairs)} Q&A pairs from {len(valid_pages)} pages")
    print(f"[STATS] Success rate: {((len(valid_pages)-errors)/len(valid_pages)*100):.1f}%")
    print(f"[SAVE] Saving to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)

    # Show samples
    if all_qa_pairs:
        print("\n[SAMPLES] Example Q&A pairs:")
        for qa in all_qa_pairs[:3]:
            print(f"\nQ: {qa['question']}")
            print(f"A: {qa['answer'][:150]}...")
            print(f"Source: {qa['source_url']}")

    return all_qa_pairs

if __name__ == "__main__":
    # Process a subset for testing or all pages
    # Start with 200 pages to test, then increase

    qa_pairs = process_comprehensive_data(
        input_file="data/comprehensive_sfsu_crawl.json",
        output_file="data/qa_training_data.json",
        max_pages=200,  # Process 200 pages first
        sample_strategy='diverse'  # Get diverse content
    )

    print(f"\n[SUCCESS] Created {len(qa_pairs)} Q&A training pairs")
    print("[FILE] Saved to: data/qa_training_data.json")
    print("\n[NEXT STEPS]:")
    print("1. Review the Q&A pairs in data/qa_training_data.json")
    print("2. If quality is good, increase max_pages to process more")
    print("3. Upload to Supabase: python upload_qa_training_data.py")
