"""
Diagnose why some pages fail to generate Q&A pairs
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

# Load processed pages
with open('data/qa_training_data.json', 'r', encoding='utf-8') as f:
    qa_pairs = json.load(f)

processed_urls = {qa['source_url'] for qa in qa_pairs}

# Load scraped data
with open('data/comprehensive_sfsu_crawl.json', 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Find pages that should have worked but didn't
valid_pages = [p for p in pages if p.get('status') == 'success' and
               p.get('full_text') and len(p.get('full_text', '')) > 200]

# Separate by processing status
processed_pages = [p for p in valid_pages if p.get('url') in processed_urls]
unprocessed_pages = [p for p in valid_pages if p.get('url') not in processed_urls]

print("="*70)
print("Q&A Extraction Diagnostic Report")
print("="*70)

print(f"\n[SCRAPED DATA]")
print(f"  Total pages scraped: {len(pages)}")
print(f"  Valid pages (success + content>200 chars): {len(valid_pages)}")

print(f"\n[PROCESSING STATUS]")
print(f"  Successfully processed: {len(processed_pages)} pages")
print(f"  Generated Q&A pairs: {len(qa_pairs)}")
print(f"  Avg Q&A per page: {len(qa_pairs)/len(processed_pages):.2f}")

print(f"\n[FAILURES]")
print(f"  Unprocessed valid pages: {len(unprocessed_pages)}")

# Analyze unprocessed pages by content length
content_lengths = [len(p.get('full_text', '')) for p in unprocessed_pages]
if content_lengths:
    print(f"\n[UNPROCESSED CONTENT ANALYSIS]")
    print(f"  Min length: {min(content_lengths)} chars")
    print(f"  Max length: {max(content_lengths)} chars")
    print(f"  Avg length: {sum(content_lengths)/len(content_lengths):.0f} chars")

    short = len([l for l in content_lengths if l < 500])
    medium = len([l for l in content_lengths if 500 <= l < 2000])
    long = len([l for l in content_lengths if l >= 2000])

    print(f"\n  Short (<500 chars): {short} ({short/len(content_lengths)*100:.1f}%)")
    print(f"  Medium (500-2000): {medium} ({medium/len(content_lengths)*100:.1f}%)")
    print(f"  Long (>2000): {long} ({long/len(content_lengths)*100:.1f}%)")

# Show sample unprocessed pages
print(f"\n[SAMPLE UNPROCESSED PAGES]")
for i, page in enumerate(unprocessed_pages[:5], 1):
    print(f"\n{i}. {page.get('title', 'No title')[:60]}")
    print(f"   URL: {page.get('url', '')[:70]}")
    print(f"   Length: {len(page.get('full_text', ''))} chars")
    print(f"   Preview: {page.get('full_text', '')[:150]}...")

# Content quality issues
print(f"\n[COMMON ISSUES]")

# Find redirect pages
redirects = [p for p in unprocessed_pages if 'redirect' in p.get('full_text', '').lower()[:200]]
print(f"  Redirects/empty pages: {len(redirects)}")

# Find very repetitive content
navigation_heavy = [p for p in unprocessed_pages if
                   p.get('full_text', '').count('Skip to') > 5 or
                   p.get('full_text', '').count('Menu') > 5]
print(f"  Navigation-heavy pages: {len(navigation_heavy)}")

# Find pages with mostly links
link_heavy = [p for p in unprocessed_pages if p.get('full_text', '').count('http') > 20]
print(f"  Link-heavy pages: {len(link_heavy)}")

print(f"\n[RECOMMENDATION]")
if len(unprocessed_pages) > len(processed_pages) * 0.3:
    print("  ⚠️  High failure rate - Consider improving extraction logic")
    print("  Solutions:")
    print("    1. Increase minimum content length threshold (currently 200)")
    print("    2. Add content quality filters (remove navigation, links)")
    print("    3. Improve JSON parsing with retry logic")
    print("    4. Use more reliable models (Ollama for local retries)")
else:
    print("  ✓ Acceptable failure rate - mostly low-quality pages filtered out")

print("\n" + "="*70)
