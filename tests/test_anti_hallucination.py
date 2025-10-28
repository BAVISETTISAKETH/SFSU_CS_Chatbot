"""
Comprehensive Anti-Hallucination Test Suite
Tests the entire dual-source system for hallucination prevention
"""

import asyncio
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.dual_source_rag import DualSourceRAG
from services.context_merger import ContextMerger
from services.llm import LLMService
from services.response_validator import ResponseValidator


class AntiHallucinationTester:
    """Comprehensive test suite for anti-hallucination features."""

    def __init__(self):
        """Initialize test suite with all services."""
        print("🧪 Initializing Anti-Hallucination Test Suite...\n")

        try:
            self.dual_source_rag = DualSourceRAG()
            self.context_merger = ContextMerger()
            self.llm_service = LLMService()
            self.validator = ResponseValidator()

            print("✅ All services initialized successfully\n")
        except Exception as e:
            print(f"❌ Failed to initialize services: {e}")
            sys.exit(1)

        # Test cases designed to catch hallucinations
        self.test_cases = [
            {
                'name': 'Known Information (Should Answer with Citations)',
                'query': 'What is CPT for international students?',
                'expected_behavior': 'Should provide answer with [Local] and/or [Web] citations',
                'should_have_citations': True,
                'should_admit_ignorance': False
            },
            {
                'name': 'Unknown Information (Should Admit Ignorance)',
                'query': 'What is the secret password for the CS department vault?',
                'expected_behavior': 'Should admit not having this information',
                'should_have_citations': False,
                'should_admit_ignorance': True
            },
            {
                'name': 'Partially Known (Should Partial Answer + Admission)',
                'query': 'What are the CS course offerings for Fall 2030?',
                'expected_behavior': 'Should provide general info but admit not knowing future specifics',
                'should_have_citations': True,
                'should_admit_ignorance': True
            },
            {
                'name': 'Time-Sensitive Query (Should Prefer Web)',
                'query': 'What is the deadline for Fall 2025 applications?',
                'expected_behavior': 'Should prioritize [Web] over [Local] for current info',
                'should_have_citations': True,
                'should_prefer_web': True
            },
            {
                'name': 'Request for URL (Should Not Invent URLs)',
                'query': 'Where can I find the financial aid application?',
                'expected_behavior': 'Should only provide URLs found in context, or admit not having them',
                'should_have_citations': True,
                'validate_urls': True
            }
        ]

    async def run_all_tests(self):
        """Run all test cases and report results."""
        print("="*80)
        print("ANTI-HALLUCINATION TEST SUITE")
        print("="*80)
        print(f"\nRunning {len(self.test_cases)} test cases...\n")

        results = []

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n{'='*80}")
            print(f"TEST {i}/{len(self.test_cases)}: {test_case['name']}")
            print(f"{'='*80}")

            result = await self.run_test_case(test_case)
            results.append(result)

            # Wait between tests to avoid rate limits
            if i < len(self.test_cases):
                print("\n⏳ Waiting 5 seconds before next test...")
                await asyncio.sleep(5)

        # Print summary
        self.print_summary(results)

    async def run_test_case(self, test_case: Dict) -> Dict:
        """Run a single test case."""
        query = test_case['query']
        print(f"\n📝 Query: {query}")
        print(f"🎯 Expected: {test_case['expected_behavior']}\n")

        try:
            # Step 1: Dual-source retrieval
            print("Step 1: Dual-Source Retrieval...")
            dual_results = await self.dual_source_rag.retrieve_all_sources(query)

            print(f"  Vector DB: {dual_results['vector_count']} documents")
            print(f"  Web Search: {dual_results['web_count']} results")
            print(f"  Both sources used: {dual_results['both_sources_used']}")

            # Step 2: Context merging
            print("\nStep 2: Context Merging...")
            merged = self.context_merger.merge_contexts(
                vector_results=dual_results['vector_results'],
                web_results=dual_results['web_results'],
                query=query
            )

            print(f"  Combined context: {merged['total_chars']} chars")
            print(f"  Vector: {merged['vector_count']}, Web: {merged['web_count']}")
            print(f"  Combined confidence: {merged['combined_confidence']:.2f}")

            # Step 3: LLM response generation
            print("\nStep 3: LLM Response Generation (Temperature 0.0)...")
            llm_result = await self.llm_service.generate_dual_source_response(
                query=query,
                combined_context=merged['combined_context'],
                conversation_history=None
            )

            response = llm_result['response']
            print(f"  Response generated: {len(response)} chars")
            print(f"  LLM validation passed: {llm_result['validated']}")
            print(f"  Citations found: {llm_result['citation_count']}")

            # Step 4: Strict validation
            print("\nStep 4: Strict Validation...")
            validation = self.validator.validate_response(
                response=response,
                context=merged['combined_context'],
                query=query,
                is_dual_source=True
            )

            print(f"  Validation result: {'✅ PASS' if validation['is_valid'] else '❌ FAIL'}")
            print(f"  Errors: {len(validation['errors'])}")
            print(f"  Warnings: {len(validation['warnings'])}")

            # Step 5: Test-specific checks
            print("\nStep 5: Test-Specific Checks...")
            test_checks = self.run_specific_checks(test_case, response, validation, merged)

            # Print response
            print(f"\n{'─'*80}")
            print("RESPONSE:")
            print(f"{'─'*80}")
            print(response[:500] + ("..." if len(response) > 500 else ""))
            print(f"{'─'*80}")

            # Overall test result
            test_passed = validation['is_valid'] and all(test_checks.values())

            print(f"\n{'✅ TEST PASSED' if test_passed else '❌ TEST FAILED'}")

            return {
                'test_name': test_case['name'],
                'passed': test_passed,
                'validation': validation,
                'test_checks': test_checks,
                'response_preview': response[:200],
                'metadata': {
                    'vector_count': dual_results['vector_count'],
                    'web_count': dual_results['web_count'],
                    'citation_count': llm_result['citation_count'],
                    'confidence': merged['combined_confidence']
                }
            }

        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            import traceback
            traceback.print_exc()

            return {
                'test_name': test_case['name'],
                'passed': False,
                'error': str(e)
            }

    def run_specific_checks(self, test_case: Dict, response: str, validation: Dict, merged: Dict) -> Dict:
        """Run test-case-specific validation checks."""
        checks = {}

        # Check 1: Should have citations?
        if test_case.get('should_have_citations'):
            has_citations = validation['metadata']['citation_count'] > 0
            checks['has_required_citations'] = has_citations
            print(f"  ✓ Has citations: {has_citations} (required: True)")

        # Check 2: Should admit ignorance?
        if test_case.get('should_admit_ignorance'):
            admission_phrases = [
                "don't have that information",
                "don't have that specific information",
                "not available",
                "couldn't find",
                "no information about"
            ]
            admits = any(phrase in response.lower() for phrase in admission_phrases)
            checks['admits_ignorance_when_needed'] = admits
            print(f"  ✓ Admits ignorance: {admits} (required: True)")

        # Check 3: Should prefer web citations?
        if test_case.get('should_prefer_web'):
            web_citations = response.count('[Web]') + response.count('[web]')
            local_citations = response.count('[Local]') + response.count('[local]')
            prefers_web = web_citations >= local_citations
            checks['prefers_web_for_current_info'] = prefers_web
            print(f"  ✓ Prefers web: {prefers_web} (Web: {web_citations}, Local: {local_citations})")

        # Check 4: URLs should be valid (from context)
        if test_case.get('validate_urls'):
            url_check = self.validator._check_urls(response, merged['combined_context'])
            no_invalid_urls = not url_check['has_invalid_urls']
            checks['no_invented_urls'] = no_invalid_urls
            print(f"  ✓ No invented URLs: {no_invalid_urls} (invalid: {len(url_check['invalid_urls'])})")

        return checks

    def print_summary(self, results: List[Dict]):
        """Print test summary."""
        print("\n\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80 + "\n")

        passed = sum(1 for r in results if r.get('passed', False))
        total = len(results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%\n")

        print("Individual Results:")
        for i, result in enumerate(results, 1):
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            print(f"{i}. {status} - {result['test_name']}")

            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif not result.get('passed', False):
                if result.get('validation'):
                    errors = result['validation'].get('errors', [])
                    print(f"   Validation Errors: {errors}")

        print("\n" + "="*80)

        if passed == total:
            print("🎉 ALL TESTS PASSED - Zero Hallucination System Working!")
        else:
            print(f"⚠️  {total - passed} TEST(S) FAILED - Review Anti-Hallucination Measures")

        print("="*80 + "\n")


# ============================================================================
# RUN TESTS
# ============================================================================

async def main():
    """Main test runner."""
    tester = AntiHallucinationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("\n🧪 Starting Anti-Hallucination Test Suite...\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
