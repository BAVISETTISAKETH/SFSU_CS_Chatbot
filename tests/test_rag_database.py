"""
Test script to diagnose RAG and database issues
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.database import DatabaseService
from services.rag import RAGService
from services.web_search import WebSearchService

load_dotenv()

async def test_database_connection():
    """Test if database is connected and has documents."""
    print("\n" + "="*80)
    print("TEST 1: Database Connection & Document Count")
    print("="*80)

    try:
        db = DatabaseService()

        # Count total documents
        result = db.client.table("documents").select("id", count="exact").execute()
        total_docs = result.count

        print(f"[OK] Database connected successfully")
        print(f"[INFO] Total documents in database: {total_docs}")

        if total_docs == 0:
            print("[WARNING] Database has 0 documents! You need to load data first.")
            return False

        # Get a sample document
        sample = db.client.table("documents").select("*").limit(1).execute()
        if sample.data:
            doc = sample.data[0]
            print(f"\n[SAMPLE] Sample document:")
            print(f"   ID: {doc.get('id')}")
            print(f"   Source: {doc.get('source', 'N/A')[:80]}...")
            print(f"   Content length: {len(doc.get('content', ''))} chars")
            print(f"   Has embedding: {doc.get('embedding') is not None}")

        return True

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rag_search():
    """Test if RAG search is returning relevant documents."""
    print("\n" + "="*80)
    print("TEST 2: RAG Search Functionality")
    print("="*80)

    test_queries = [
        "What are the CS course requirements?",
        "How do I apply for financial aid?",
        "Where is the computer science department located?"
    ]

    try:
        rag = RAGService()

        for query in test_queries:
            print(f"\n[SEARCH] Testing query: '{query}'")
            result = await rag.search(query, k=5)

            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Documents found: {len(result.get('sources', []))}")
            print(f"   Context length: {len(result['context'])} chars")

            if result['confidence'] == 0.0:
                print(f"   [WARNING] No documents found for this query!")
            else:
                print(f"   [OK] Documents retrieved successfully")
                # Show first source
                if result.get('sources'):
                    first_source = result['sources'][0]
                    print(f"   Top match: {first_source.get('source', 'N/A')[:60]}... (similarity: {first_source.get('similarity', 0):.3f})")

        return True

    except Exception as e:
        print(f"[ERROR] RAG search error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_web_search():
    """Test if web search is working."""
    print("\n" + "="*80)
    print("TEST 3: Web Search Functionality")
    print("="*80)

    try:
        web_search = WebSearchService()

        if not web_search.enabled:
            print("[WARNING] Web search is DISABLED (no SERPAPI_KEY)")
            return False

        print("[OK] Web search is enabled")

        query = "SFSU computer science courses"
        print(f"\n[SEARCH] Testing query: '{query}'")

        result = await web_search.search(query, num_results=2)

        if result:
            print(f"   [OK] Web search returned results ({len(result)} chars)")
            print(f"   Preview: {result[:200]}...")
        else:
            print(f"   [WARNING] Web search returned empty results!")

        return bool(result)

    except Exception as e:
        print(f"[ERROR] Web search error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chat_endpoint():
    """Test the actual chat endpoint."""
    print("\n" + "="*80)
    print("TEST 4: Chat Endpoint Test")
    print("="*80)

    import requests

    try:
        query = "What CS courses does SFSU offer?"

        print(f"[SEARCH] Testing chat endpoint with: '{query}'")

        response = requests.post(
            "http://localhost:8000/chat",
            json={"query": query},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] Chat endpoint responded successfully")
            print(f"   Source: {data.get('source')}")
            print(f"   Confidence: {data.get('confidence'):.2f}")
            print(f"   Response length: {len(data.get('response', ''))} chars")
            print(f"\n[RESPONSE] Response preview:")
            print(f"   {data.get('response', '')[:300]}...")

            if data.get('source') == 'error':
                print(f"\n   [WARNING] Response source is 'error'!")
                return False

            return True
        else:
            print(f"[ERROR] Chat endpoint error: {response.status_code}")
            print(f"   {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n" + "="* 80)
    print("SFSU CS Chatbot - Diagnostic Test Suite")
    print("=" * 80)

    results = {
        "Database Connection": await test_database_connection(),
        "RAG Search": await test_rag_search(),
        "Web Search": await test_web_search(),
        "Chat Endpoint": await test_chat_endpoint()
    }

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n[SUCCESS] All tests passed! The system appears to be working correctly.")
    else:
        print("\n[WARNING] Some tests failed. Check the output above for details.")

    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
