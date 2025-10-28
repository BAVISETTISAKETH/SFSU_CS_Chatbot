"""
Test script for Gator Guide chatbot
Tests various types of questions to ensure quality
"""

import requests
import json
import time
from typing import List, Dict

# Backend URL
API_URL = "http://localhost:8000/chat"

# Test questions from CONTINUE_TOMORROW.md
TEST_QUESTIONS = [
    # CS Department
    {
        "query": "What is the CS department?",
        "category": "CS Department"
    },
    {
        "query": "What CS courses are required?",
        "category": "CS Department"
    },
    {
        "query": "Tell me about CSC 317",
        "category": "CS Department"
    },

    # International Students
    {
        "query": "What is CPT?",
        "category": "International Students"
    },
    {
        "query": "How do I apply for OPT?",
        "category": "International Students"
    },
    {
        "query": "When can I apply for OPT if graduating in December?",
        "category": "International Students"
    },

    # Financial Aid
    {
        "query": "Tell me about financial aid at SFSU",
        "category": "Financial Aid"
    },
    {
        "query": "What scholarships are available?",
        "category": "Financial Aid"
    },

    # Housing
    {
        "query": "What housing options are available?",
        "category": "Housing"
    },
    {
        "query": "How much does on-campus housing cost?",
        "category": "Housing"
    },

    # Graduate Programs
    {
        "query": "How do I apply for graduate programs?",
        "category": "Graduate Programs"
    },
]

def test_query(query: str, category: str) -> Dict:
    """Test a single query and return results."""
    print(f"\n{'='*80}")
    print(f"Category: {category}")
    print(f"Question: {query}")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            timeout=30
        )

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()

            print(f"\n[OK] Status: SUCCESS")
            print(f"[OK] Response Time: {elapsed_time:.2f}s (API: {data.get('response_time_ms', 0)}ms)")
            print(f"[OK] Source: {data.get('source', 'unknown')}")
            print(f"[OK] Confidence: {data.get('confidence', 0):.2f}")
            print(f"\nResponse:\n{data.get('response', 'No response')[:500]}...")

            # Check for sources
            sources = data.get('sources', [])
            if sources:
                print(f"\nSources ({len(sources)}):")
                for i, source in enumerate(sources[:3], 1):
                    print(f"  {i}. {source.get('source', 'Unknown')[:80]}")

            return {
                "success": True,
                "category": category,
                "query": query,
                "source": data.get('source'),
                "confidence": data.get('confidence'),
                "response_time": elapsed_time,
                "has_sources": len(sources) > 0
            }
        else:
            print(f"\n[ERROR] Status: ERROR {response.status_code}")
            print(f"[ERROR] Message: {response.text}")

            return {
                "success": False,
                "category": category,
                "query": query,
                "error": response.text
            }

    except Exception as e:
        print(f"\n[ERROR] Exception: {str(e)}")
        return {
            "success": False,
            "category": category,
            "query": query,
            "error": str(e)
        }

def run_tests():
    """Run all tests and generate report."""
    print("="*80)
    print("GATOR GUIDE (ALLI) - CHATBOT TEST SUITE")
    print("="*80)

    results = []

    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\nTest {i}/{len(TEST_QUESTIONS)}")
        result = test_query(test_case["query"], test_case["category"])
        results.append(result)

        # Wait between requests to avoid rate limiting
        if i < len(TEST_QUESTIONS):
            print("\nWaiting 3 seconds before next test...")
            time.sleep(3)

    # Generate summary report
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\nTotal Tests: {len(results)}")
    print(f"[OK] Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"[ERROR] Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")

    if successful:
        # Source breakdown
        sources = {}
        for r in successful:
            source = r.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

        print(f"\nSource Breakdown:")
        for source, count in sources.items():
            print(f"  {source}: {count} ({count/len(successful)*100:.1f}%)")

        # Average response time
        avg_time = sum(r.get('response_time', 0) for r in successful) / len(successful)
        print(f"\nAverage Response Time: {avg_time:.2f}s")

        # Average confidence
        avg_conf = sum(r.get('confidence', 0) for r in successful) / len(successful)
        print(f"Average Confidence: {avg_conf:.2f}")

    if failed:
        print(f"\nFailed Tests:")
        for r in failed:
            print(f"  - {r['category']}: {r['query'][:50]}...")
            print(f"    Error: {r.get('error', 'Unknown error')[:100]}")

    print("\n" + "="*80)
    print("TEST COMPLETE!")
    print("="*80)

    return results

if __name__ == "__main__":
    run_tests()
