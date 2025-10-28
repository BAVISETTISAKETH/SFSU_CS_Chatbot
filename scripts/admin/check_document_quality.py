"""
Check the quality of documents in the database
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from backend.services.database import DatabaseService

load_dotenv()

def check_document_quality():
    """Check document content quality."""
    print("="*80)
    print("DOCUMENT QUALITY CHECK")
    print("="*80)

    db = DatabaseService()

    # Get random sample of 10 documents
    print("\n[INFO] Fetching random sample of 10 documents...")
    result = db.client.table("documents").select("*").limit(10).execute()

    if not result.data:
        print("[ERROR] No documents found!")
        return

    print(f"[OK] Found {len(result.data)} documents\n")

    for i, doc in enumerate(result.data, 1):
        print(f"\n{'='*80}")
        print(f"DOCUMENT {i}")
        print(f"{'='*80}")
        print(f"ID: {doc.get('id')}")
        print(f"Source: {doc.get('source', 'N/A')}")
        print(f"Category: {doc.get('category', 'N/A')}")
        print(f"Content length: {len(doc.get('content', ''))} chars")
        print(f"\nContent preview (first 500 chars):")
        print("-" * 80)
        content = doc.get('content', '')
        if content:
            print(content[:500])
            if len(content) > 500:
                print("\n... (truncated)")
        else:
            print("[WARNING] EMPTY CONTENT!")
        print("-" * 80)

    # Check for empty or very short content
    print("\n" + "="*80)
    print("CONTENT STATISTICS")
    print("="*80)

    all_docs = db.client.table("documents").select("id, content").execute()

    if all_docs.data:
        lengths = [len(doc.get('content', '')) for doc in all_docs.data]
        empty_count = sum(1 for length in lengths if length == 0)
        short_count = sum(1 for length in lengths if 0 < length < 100)
        medium_count = sum(1 for length in lengths if 100 <= length < 500)
        long_count = sum(1 for length in lengths if length >= 500)

        print(f"\nTotal documents: {len(all_docs.data)}")
        print(f"Empty (0 chars): {empty_count} ({empty_count/len(all_docs.data)*100:.1f}%)")
        print(f"Short (1-99 chars): {short_count} ({short_count/len(all_docs.data)*100:.1f}%)")
        print(f"Medium (100-499 chars): {medium_count} ({medium_count/len(all_docs.data)*100:.1f}%)")
        print(f"Long (500+ chars): {long_count} ({long_count/len(all_docs.data)*100:.1f}%)")

        if empty_count > 0 or short_count > len(all_docs.data) * 0.5:
            print("\n[WARNING] Many documents have empty or very short content!")
            print("This will cause poor search results.")

    # Test keyword search on content
    print("\n" + "="*80)
    print("KEYWORD SEARCH TEST")
    print("="*80)

    test_keywords = ["computer science", "CS", "course", "financial aid", "admission"]

    for keyword in test_keywords:
        result = db.client.table("documents").select("id").ilike("content", f"%{keyword}%").limit(5).execute()
        count = len(result.data) if result.data else 0
        print(f"'{keyword}': {count} documents found")

        if count > 0:
            print(f"  [OK] Keyword found in content")
        else:
            print(f"  [WARNING] Keyword NOT found in any content!")

if __name__ == "__main__":
    check_document_quality()
