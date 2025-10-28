"""
Generate Q&A Training Data from Comprehensive SFSU Scrape
Supports multiple LLM providers: Groq (free), OpenAI, Anthropic
"""

import json
import os
from dotenv import load_dotenv
import time
import random

load_dotenv()

# Try to import available providers
GROQ_AVAILABLE = False
OPENAI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False
GEMINI_AVAILABLE = False

try:
    from groq import Groq
    if os.getenv("GROQ_API_KEY"):
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        GROQ_AVAILABLE = True
except:
    pass

try:
    from openai import OpenAI
    if os.getenv("OPENAI_API_KEY"):
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        OPENAI_AVAILABLE = True
except:
    pass

try:
    from anthropic import Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        ANTHROPIC_AVAILABLE = True
except:
    pass

try:
    import google.generativeai as genai
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Latest free model
        GEMINI_AVAILABLE = True
except:
    pass

def call_llm(prompt, provider='auto'):
    """
    Call LLM with automatic provider selection.

    Args:
        prompt: The prompt to send
        provider: 'groq', 'openai', 'anthropic', or 'auto' (default)
    """

    # Auto-select provider
    if provider == 'auto':
        if GEMINI_AVAILABLE:
            provider = 'gemini'
            print("   [API] Using Google Gemini (free tier)")
        elif OPENAI_AVAILABLE:
            provider = 'openai'
            print("   [API] Using OpenAI")
        elif ANTHROPIC_AVAILABLE:
            provider = 'anthropic'
            print("   [API] Using Anthropic")
        elif GROQ_AVAILABLE:
            provider = 'groq'
            print("   [API] Using Groq (free tier)")
        else:
            raise Exception("No LLM provider available. Please configure API keys.")

    # Call appropriate provider
    try:
        if provider == 'groq' and GROQ_AVAILABLE:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,  # Increased for more Q&A pairs
                timeout=60
            )
            return response.choices[0].message.content.strip()

        elif provider == 'openai' and OPENAI_AVAILABLE:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper and faster than gpt-4
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000  # Increased for more Q&A pairs
            )
            return response.choices[0].message.content.strip()

        elif provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            response = anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",  # Cheaper and faster
                max_tokens=4000,  # Increased for more Q&A pairs
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        elif provider == 'gemini' and GEMINI_AVAILABLE:
            response = gemini_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 4000,  # Increased for more Q&A pairs
                }
            )
            return response.text.strip()

        else:
            raise Exception(f"Provider {provider} not available")

    except Exception as e:
        error_str = str(e).lower()
        if "429" in str(e) or "rate_limit" in error_str:
            # Print full error for debugging
            print(f"   [RATE LIMIT DETAILS] {str(e)[:200]}")
            raise Exception("RATE_LIMIT")
        raise e

def extract_qa_pairs(page, provider='auto'):
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

    # Process full content to extract maximum Q&A pairs
    prompt = f"""You are creating training data for an SFSU chatbot. Extract AS MANY natural questions and comprehensive answers as possible from this content.

URL: {url}
Title: {title}
Category: {category}

Content:
{full_text[:6000]}

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

    try:
        result = call_llm(prompt, provider)

        # Extract JSON
        if '```json' in result:
            result = result.split('```json')[1].split('```')[0].strip()
        elif '```' in result:
            result = result.split('```')[1].split('```')[0].strip()

        qa_pairs = json.loads(result)
        return qa_pairs

    except Exception as e:
        if "RATE_LIMIT" in str(e):
            raise e  # Re-raise rate limit errors
        print(f"   [ERROR] {str(e)[:100]}")
        return []

def process_comprehensive_data(input_file="data/comprehensive_sfsu_crawl.json",
                               output_file="data/qa_training_data.json",
                               max_pages=None,
                               sample_strategy='diverse',
                               provider='auto',
                               resume=True):
    """
    Process comprehensive scraped data to generate Q&A pairs.

    Args:
        input_file: Path to comprehensive scrape JSON
        output_file: Path to save Q&A pairs
        max_pages: Maximum pages to process (None = all)
        sample_strategy: 'diverse' or 'sequential'
        provider: 'groq', 'openai', 'anthropic', or 'auto'
        resume: Continue from existing output file
    """

    print("="*70)
    print("Multi-Provider Q&A Generator for SFSU Chatbot")
    print("="*70)
    print(f"[PROVIDERS] Available:")
    print(f"  - Gemini (free):    {'YES' if GEMINI_AVAILABLE else 'NO'}")
    print(f"  - Groq (free):      {'YES' if GROQ_AVAILABLE else 'NO'}")
    print(f"  - OpenAI (paid):    {'YES' if OPENAI_AVAILABLE else 'NO'}")
    print(f"  - Anthropic (paid): {'YES' if ANTHROPIC_AVAILABLE else 'NO'}")
    print()

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
                   p.get('url') not in processed_urls]  # Skip already processed

    print(f"[FILTER] {len(valid_pages)} pages available for processing (excluding already processed)")

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
    all_qa_pairs = existing_qa_pairs.copy()
    errors = 0
    rate_limit_hit = False

    # Build list of available providers for fallback
    available_providers = []
    if GEMINI_AVAILABLE:
        available_providers.append('gemini')
    if OPENAI_AVAILABLE:
        available_providers.append('openai')
    if GROQ_AVAILABLE:
        available_providers.append('groq')
    if ANTHROPIC_AVAILABLE:
        available_providers.append('anthropic')

    current_provider_index = 0
    exhausted_providers = set()

    print(f"\n[PROCESS] Generating Q&A pairs from {len(valid_pages)} pages...")
    if len(valid_pages) > 0:
        print(f"[INFO] Estimated time: {len(valid_pages) * 1.5 / 60:.0f} minutes")
    print()

    for i, page in enumerate(valid_pages, 1):
        title = page.get('title', 'Untitled')[:60]
        url = page.get('url', '')

        print(f"[{i}/{len(valid_pages)}] {title}...")

        # Try current provider, fallback to others if needed
        success = False
        for attempt in range(len(available_providers)):
            if current_provider_index >= len(available_providers):
                print(f"   [STOP] All providers exhausted")
                rate_limit_hit = True
                break

            current_provider = available_providers[current_provider_index]

            # Skip exhausted providers
            if current_provider in exhausted_providers:
                current_provider_index += 1
                continue

            try:
                qa_pairs = extract_qa_pairs(page, current_provider)

                if qa_pairs:
                    all_qa_pairs.extend(qa_pairs)
                    print(f"   [OK] +{len(qa_pairs)} Q&A pairs (Total: {len(all_qa_pairs)})")
                    success = True
                    break
                else:
                    errors += 1
                    print(f"   [SKIP] No pairs extracted")
                    success = True
                    break

            except Exception as e:
                if "RATE_LIMIT" in str(e):
                    print(f"   [RATE LIMIT] {current_provider} exhausted")
                    exhausted_providers.add(current_provider)
                    current_provider_index += 1

                    if current_provider_index < len(available_providers):
                        next_provider = available_providers[current_provider_index]
                        print(f"   [SWITCH] Trying {next_provider}...")
                        continue
                    else:
                        print(f"   [STOP] No more providers available")
                        rate_limit_hit = True
                        break
                else:
                    errors += 1
                    print(f"   [ERROR] {str(e)[:100]}")
                    success = True
                    break

        if rate_limit_hit:
            break

        # Rate limiting
        time.sleep(1.0)

        # Auto-save every 10 pages
        if i % 10 == 0:
            print(f"\n[SAVE] Progress checkpoint: {len(all_qa_pairs)} Q&A pairs")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
            print()

    # Final save
    print(f"\n{'='*70}")
    if rate_limit_hit:
        print("RATE LIMIT REACHED - Progress Saved")
        print("="*70)
        print(f"[PARTIAL] Generated {len(all_qa_pairs)} Q&A pairs (including previous)")
        print(f"[PROGRESS] Processed {i} new pages in this run")
        print(f"[REMAINING] {len(valid_pages) - i} pages remaining")
        print(f"\n[NEXT] Wait 24 hours for Groq limit reset, or:")
        print(f"  1. Add OpenAI API key to .env (paid)")
        print(f"  2. Add Anthropic API key to .env (paid)")
        print(f"  3. Run this script again tomorrow")
    else:
        print("COMPLETE!")
        print("="*70)
        print(f"[SUCCESS] Generated {len(all_qa_pairs)} Q&A pairs total")
        print(f"[STATS] Success rate: {((len(valid_pages)-errors)/len(valid_pages)*100):.1f}%")

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
    # Process with automatic provider selection and resume capability
    qa_pairs = process_comprehensive_data(
        input_file="data/comprehensive_sfsu_crawl.json",
        output_file="data/qa_training_data.json",
        max_pages=1000,  # Process up to 1000 pages (ready for tomorrow!)
        sample_strategy='diverse',
        provider='auto',  # Auto-select best available provider
        resume=True  # Continue from where we left off
    )

    print(f"\n{'='*70}")
    print(f"[FINAL] Total Q&A pairs: {len(qa_pairs)}")
    print(f"[FILE] Saved to: data/qa_training_data.json")
    print(f"\n[NEXT STEPS]:")
    print(f"1. Review Q&A pairs: data/qa_training_data.json")
    print(f"2. Create Supabase table (see RESUME_IN_3_HOURS.md)")
    print(f"3. Upload to Supabase: python upload_qa_training_data.py")
    print("="*70)
