"""
Test script to verify the complete correction workflow:
1. Student flags response
2. Professor reviews and approves/corrects
3. Verified fact is stored
4. Next query retrieves verified fact
"""

import asyncio
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.database import DatabaseService
from backend.services.rag import RAGService

async def test_workflow():
    print("=" * 80)
    print("TESTING CORRECTION WORKFLOW")
    print("=" * 80)

    db_service = DatabaseService()
    rag_service = RAGService()

    # Test query
    test_query = "What is the deadline for CSC 648 project submission?"
    test_response = "The deadline is December 15th, 2024"

    print(f"\n1. Creating a correction for query: '{test_query}'")
    try:
        correction_id = await db_service.create_correction(
            query=test_query,
            response=test_response,
            category="Student flagged: Incorrect deadline"
        )
        print(f"   ✅ Correction created with ID: {correction_id}")
    except Exception as e:
        print(f"   ❌ Error creating correction: {e}")
        return

    print(f"\n2. Retrieving the correction")
    try:
        correction = await db_service.get_correction(correction_id)
        print(f"   ✅ Found correction:")
        print(f"      Query: {correction['student_query']}")
        print(f"      Response: {correction['rag_response']}")
        print(f"      Status: {correction['status']}")
    except Exception as e:
        print(f"   ❌ Error retrieving correction: {e}")
        return

    print(f"\n3. Adding verified fact (simulating professor approval)")
    corrected_answer = "The deadline for CSC 648 project submission is December 20th, 2024 at 11:59 PM PST."
    try:
        await db_service.add_verified_fact(
            question=test_query,
            answer=corrected_answer,
            verified_by="professor@sfsu.edu",
            category="Course Deadlines"
        )
        print(f"   ✅ Verified fact added")
    except Exception as e:
        print(f"   ❌ Error adding verified fact: {e}")
        return

    print(f"\n4. Updating correction status to 'approved'")
    try:
        await db_service.update_correction(
            correction_id=correction_id,
            status='approved',
            correction_text=corrected_answer,
            reviewed_by="professor@sfsu.edu"
        )
        print(f"   ✅ Correction updated to approved")
    except Exception as e:
        print(f"   ❌ Error updating correction: {e}")
        return

    print(f"\n5. Searching for verified fact with similar query")
    similar_queries = [
        "What is the deadline for CSC 648 project submission?",
        "When is the CSC 648 project due?",
        "CSC 648 project deadline"
    ]

    for query in similar_queries:
        print(f"\n   Testing query: '{query}'")
        try:
            result = await rag_service.search_verified_facts(query)
            if result:
                print(f"   ✅ Found verified fact!")
                print(f"      Question: {result['question']}")
                print(f"      Answer: {result['answer']}")
                print(f"      Confidence: {result['confidence']:.2f}")
                print(f"      Verified by: {result.get('verified_by', 'Unknown')}")
            else:
                print(f"   ⚠️  No verified fact found (confidence too low)")
        except Exception as e:
            print(f"   ❌ Error searching verified facts: {e}")

    print("\n" + "=" * 80)
    print("WORKFLOW TEST COMPLETE")
    print("=" * 80)

    # Cleanup (optional)
    print("\n6. Cleanup (deleting test data)")
    try:
        db_service.client.table("corrections").delete().eq("id", correction_id).execute()
        db_service.client.table("verified_facts").delete().eq("question", test_query).execute()
        print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ⚠️  Error cleaning up: {e}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
