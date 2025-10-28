"""
Strict Response Validator - Zero Hallucination Enforcement
Validates LLM responses against provided context to prevent hallucinations
"""

from typing import Dict, List, Tuple
import re


class ResponseValidator:
    """
    Strict validation layer that REJECTS responses that don't meet criteria.
    Unlike the validation in llm.py that only warns, this ENFORCES rules.
    """

    def __init__(self):
        """Initialize validator with strict rules."""
        self.min_citation_count = 1  # Minimum citations required
        self.max_retries = 2  # Maximum regeneration attempts

    def validate_response(
        self,
        response: str,
        context: str,
        query: str,
        is_dual_source: bool = True
    ) -> Dict:
        """
        Strictly validate response against context.
        Returns validation result with pass/fail and reasons.

        Args:
            response: Generated LLM response
            context: Provided context (from vector DB and/or web search)
            query: Original user query
            is_dual_source: Whether dual-source mode is being used

        Returns:
            Dict with validation results
        """
        validation_errors = []
        validation_warnings = []

        print(f"\n[VALIDATOR] Starting strict validation...")

        # ====================================================================
        # CRITICAL VALIDATIONS (Must pass - will reject response if failed)
        # ====================================================================

        # 1. Check for minimum response length
        if len(response.strip()) < 20:
            validation_errors.append("Response too short (< 20 chars)")

        # 2. Check for error messages (malformed response)
        if self._is_error_response(response):
            validation_errors.append("Response contains error message")

        # 3. For dual-source mode: MUST have citations
        if is_dual_source:
            citation_check = self._check_citations(response)

            if not citation_check['has_citations']:
                validation_errors.append("CRITICAL: No source citations found ([Local] or [Web] required)")

            if citation_check['citation_count'] < self.min_citation_count:
                validation_errors.append(
                    f"CRITICAL: Insufficient citations "
                    f"(found {citation_check['citation_count']}, minimum {self.min_citation_count})"
                )

        # 4. Check for forbidden phrases that indicate hallucination
        forbidden_check = self._check_forbidden_phrases(response)
        if forbidden_check['has_forbidden']:
            for phrase in forbidden_check['found_phrases']:
                validation_errors.append(f"Contains forbidden phrase: '{phrase}'")

        # 5. Check for made-up URLs (not in context)
        url_check = self._check_urls(response, context)
        if url_check['has_invalid_urls']:
            for url in url_check['invalid_urls']:
                validation_errors.append(f"URL not found in context: {url}")

        # ====================================================================
        # WARNING VALIDATIONS (Should pass but not critical)
        # ====================================================================

        # 6. Check if response admits lack of information appropriately
        admission_check = self._check_admission_of_ignorance(response, context)
        if admission_check['should_admit'] and not admission_check['admits']:
            validation_warnings.append(
                "Context lacks information but response doesn't admit it"
            )

        # 7. Check response length compared to context
        length_check = self._check_response_length(response, context)
        if length_check['suspiciously_long']:
            validation_warnings.append(
                f"Response is suspiciously long compared to context "
                f"(response: {length_check['response_length']}, context: {length_check['context_length']})"
            )

        # 8. Check for speculation words
        speculation_check = self._check_speculation(response)
        if speculation_check['has_speculation']:
            validation_warnings.append(
                f"Response contains speculation words: {speculation_check['speculation_words']}"
            )

        # ====================================================================
        # FINAL VALIDATION RESULT
        # ====================================================================

        is_valid = len(validation_errors) == 0

        print(f"[VALIDATOR] Validation Result: {'✅ PASS' if is_valid else '❌ FAIL'}")
        if validation_errors:
            print(f"[VALIDATOR] Errors ({len(validation_errors)}):")
            for error in validation_errors:
                print(f"  - {error}")
        if validation_warnings:
            print(f"[VALIDATOR] Warnings ({len(validation_warnings)}):")
            for warning in validation_warnings:
                print(f"  - {warning}")

        return {
            'is_valid': is_valid,
            'errors': validation_errors,
            'warnings': validation_warnings,
            'can_retry': is_valid or len(validation_errors) <= 2,
            'metadata': {
                'citation_count': self._check_citations(response)['citation_count'],
                'has_urls': url_check['has_urls'],
                'response_length': len(response),
                'context_length': len(context)
            }
        }

    # ========================================================================
    # VALIDATION CHECK METHODS
    # ========================================================================

    def _is_error_response(self, response: str) -> bool:
        """Check if response is an error message."""
        error_phrases = [
            "error processing",
            "trouble generating",
            "try again",
            "malformed",
            "corrupted"
        ]
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in error_phrases)

    def _check_citations(self, response: str) -> Dict:
        """Check for source citations."""
        local_citations = response.count('[Local]') + response.count('[local]')
        web_citations = response.count('[Web]') + response.count('[web]')
        total_citations = local_citations + web_citations

        has_citations = total_citations > 0

        return {
            'has_citations': has_citations,
            'citation_count': total_citations,
            'local_citations': local_citations,
            'web_citations': web_citations
        }

    def _check_forbidden_phrases(self, response: str) -> Dict:
        """Check for phrases that indicate hallucination or improper sourcing."""
        forbidden_phrases = [
            "according to the context",
            "the context states",
            "the context mentions",
            "based on my knowledge",
            "from my knowledge",
            "i know that",
            "from what i know",
            "i believe",
            "i think",
            "probably",
            "might be",
            "could be",
            "it seems"
        ]

        response_lower = response.lower()
        found_phrases = [phrase for phrase in forbidden_phrases if phrase in response_lower]

        return {
            'has_forbidden': len(found_phrases) > 0,
            'found_phrases': found_phrases
        }

    def _check_urls(self, response: str, context: str) -> Dict:
        """
        Check if all URLs in response are present in context.
        This prevents the LLM from making up URLs.
        """
        # Extract URLs from response
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        response_urls = set(re.findall(url_pattern, response))

        # Extract URLs from context
        context_urls = set(re.findall(url_pattern, context))

        # Find URLs in response that aren't in context
        invalid_urls = response_urls - context_urls

        return {
            'has_urls': len(response_urls) > 0,
            'has_invalid_urls': len(invalid_urls) > 0,
            'invalid_urls': list(invalid_urls),
            'valid_urls': list(response_urls & context_urls),
            'total_urls': len(response_urls)
        }

    def _check_admission_of_ignorance(self, response: str, context: str) -> Dict:
        """
        Check if response appropriately admits when information is not available.
        """
        # Check if context is empty or very short
        should_admit = len(context.strip()) < 100

        # Check if response admits lack of information
        admission_phrases = [
            "don't have that information",
            "don't have that specific information",
            "not available",
            "couldn't find",
            "no information about",
            "i don't know",
            "i'm not sure"
        ]

        response_lower = response.lower()
        admits = any(phrase in response_lower for phrase in admission_phrases)

        return {
            'should_admit': should_admit,
            'admits': admits
        }

    def _check_response_length(self, response: str, context: str) -> Dict:
        """
        Check if response length is reasonable compared to context.
        Suspiciously long responses might contain hallucinations.
        """
        response_length = len(response)
        context_length = len(context)

        # Response shouldn't be much longer than context
        # (unless context is very short)
        suspiciously_long = (
            response_length > context_length * 1.5 and context_length > 500
        )

        return {
            'suspiciously_long': suspiciously_long,
            'response_length': response_length,
            'context_length': context_length,
            'ratio': response_length / context_length if context_length > 0 else 0
        }

    def _check_speculation(self, response: str) -> Dict:
        """Check for speculation words that indicate uncertainty."""
        speculation_words = [
            'probably', 'likely', 'perhaps', 'maybe', 'might',
            'could be', 'possibly', 'i think', 'i believe',
            'it seems', 'appears to be'
        ]

        response_lower = response.lower()
        found_speculation = [word for word in speculation_words if word in response_lower]

        return {
            'has_speculation': len(found_speculation) > 0,
            'speculation_words': found_speculation
        }

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def should_regenerate(self, validation_result: Dict, attempt_number: int) -> bool:
        """
        Decide if response should be regenerated based on validation.

        Args:
            validation_result: Result from validate_response()
            attempt_number: Current attempt number (1-indexed)

        Returns:
            True if should retry generation
        """
        # Don't retry if already at max attempts
        if attempt_number >= self.max_retries:
            return False

        # Retry if validation failed and it's retriable
        if not validation_result['is_valid']:
            return validation_result.get('can_retry', False)

        return False

    def get_fallback_response(self, validation_result: Dict, query: str) -> str:
        """
        Generate a safe fallback response when validation fails repeatedly.

        Args:
            validation_result: Failed validation result
            query: Original user query

        Returns:
            Safe fallback response
        """
        return (
            "I apologize, but I'm unable to provide a reliable answer to your question "
            "based on the information I have available. This could mean:\n\n"
            "1. The information isn't in my knowledge base\n"
            "2. The current web search didn't return relevant results\n"
            "3. I need more context to answer accurately\n\n"
            "I'd recommend:\n"
            "- Rephrasing your question with more details\n"
            "- Contacting the relevant SFSU office directly\n"
            "- Checking the official SFSU website at https://sfsu.edu\n\n"
            "Would you like to try asking in a different way?"
        )


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
# In main.py or llm.py:

from services.response_validator import ResponseValidator

validator = ResponseValidator()

# After LLM generates response:
validation_result = validator.validate_response(
    response=llm_response,
    context=combined_context,
    query=user_query,
    is_dual_source=True
)

if not validation_result['is_valid']:
    if validator.should_regenerate(validation_result, attempt=1):
        # Regenerate with stricter prompt
        llm_response = regenerate_with_stricter_prompt()
    else:
        # Use fallback response
        llm_response = validator.get_fallback_response(validation_result, user_query)
"""
