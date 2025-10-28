"""
Test what context the LLM is actually receiving
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.rag import RAGService
from services.web_search import WebSearchService
from services.llm import LLMService

load_dotenv()

async def test_llm_with_context():
    """Test the full flow to see what context LLM receives."""
    print("="*80)
    print("LLM CONTEXT TEST")
    print("="*80)

    # Test queries
    test_queries = [
        "What CS courses does SFSU offer?",
        "How do I apply for financial aid?",
        "Where is the computer science department?"
    ]

    rag = RAGService()
    web_search = WebSearchService()
    llm = LLMService()

    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"TESTING QUERY: {query}")
        print(f"{'='*80}")

        # Step 1: RAG search
        print("\n[STEP 1] RAG Search...")
        rag_result = await rag.search(query, k=20)
        print(f"  Confidence: {rag_result['confidence']:.2f}")
        print(f"  Documents: {len(rag_result.get('sources', []))}")
        print(f"  Context length: {len(rag_result['context'])} chars")
        print(f"\n  RAG Context Preview:")
        print(f"  {'-'*76}")
        print(f"  {rag_result['context'][:400]}...")
        print(f"  {'-'*76}")

        # Step 2: Web search
        print("\n[STEP 2] Web Search...")
        web_results = await web_search.search(query, num_results=3)
        if web_results:
            print(f"  Web search returned {len(web_results)} chars")
            print(f"\n  Web Context Preview:")
            print(f"  {'-'*76}")
            print(f"  {web_results[:400]}...")
            print(f"  {'-'*76}")
        else:
            print(f"  [WARNING] Web search returned EMPTY!")

        # Step 3: Combined context (like in main.py)
        combined_context = f"""=== LIVE WEB SEARCH RESULTS (MOST CURRENT - USE THIS FIRST) ===
{web_results}

=== STORED DATABASE CONTEXT (BACKGROUND INFORMATION) ===
{rag_result['context']}

IMPORTANT: Prioritize information from the LIVE WEB SEARCH RESULTS above, as they contain the most current and accurate information from official SFSU websites."""

        print(f"\n[STEP 3] Combined Context")
        print(f"  Total length: {len(combined_context)} chars")

        # Step 4: LLM response
        print(f"\n[STEP 4] Generating LLM response...")
        response = await llm.generate_response(
            query=query,
            context=combined_context,
            use_web_context=True
        )

        print(f"\n  LLM Response:")
        print(f"  {'='*76}")
        print(f"  {response}")
        print(f"  {'='*76}")

        # Check if response seems random/unrelated
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = query_words & response_words
        print(f"\n  [ANALYSIS]")
        print(f"    Query words in response: {overlap}")
        if len(overlap) < 2:
            print(f"    [WARNING] Response seems unrelated to query!")
        else:
            print(f"    [OK] Response seems related to query")

        print(f"\n  [PAUSE - Press Enter to continue to next query...]")
        input()

if __name__ == "__main__":
    asyncio.run(test_llm_with_context())
