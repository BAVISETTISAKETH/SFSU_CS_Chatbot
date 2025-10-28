"""
Response Relevance Checker - Ensures LLM answers the EXACT question asked
Prevents tangential or irrelevant responses even when they're factually correct
"""

from typing import Dict, List
import re


class RelevanceChecker:
    """
    Checks if the LLM response actually answers the specific question asked.
    Prevents the common hallucination where LLM talks about related topics
    instead of answering the exact question.
    """

    def __init__(self):
        """Initialize relevance checker."""
        pass

    def check_relevance(self, query: str, response: str, context: str) -> Dict:
        """
        Check if response is relevant to the specific question.

        Args:
            query: User's question
            response: LLM's response
            context: Context that was provided

        Returns:
            Dict with relevance analysis
        """
        issues = []
        is_relevant = True

        # Check 1: Does response admit lack of information?
        admits_missing = self._admits_missing_info(response)

        if admits_missing:
            # If it admits it doesn't know, that's acceptable
            return {
                'is_relevant': True,
                'admits_missing': True,
                'issues': [],
                'confidence': 1.0
            }

        # Check 2: Extract key question type
        question_type = self._extract_question_type(query)

        # Check 3: Does response answer the question type?
        answers_question_type = self._answers_question_type(
            query, response, question_type
        )

        if not answers_question_type:
            is_relevant = False
            issues.append(
                f"Response doesn't answer '{question_type}' question. "
                f"Query asks: '{query}', but response provides general information."
            )

        # Check 4: For specific entity questions, check if entity is mentioned
        if question_type in ['who', 'what specific']:
            entity_mentioned = self._check_entity_mentioned(query, response)
            if not entity_mentioned:
                is_relevant = False
                issues.append(
                    "Query asks for specific entity/person, but response doesn't provide it"
                )

        # Check 5: Detect tangential responses (talking about related topics)
        is_tangential = self._is_tangential_response(query, response)
        if is_tangential:
            is_relevant = False
            issues.append(
                "Response provides related information but doesn't answer the specific question"
            )

        return {
            'is_relevant': is_relevant,
            'admits_missing': admits_missing,
            'issues': issues,
            'question_type': question_type,
            'confidence': 1.0 if is_relevant else 0.0
        }

    def _admits_missing_info(self, response: str) -> bool:
        """Check if response admits not having the information."""
        admission_phrases = [
            "don't have that information",
            "don't have that specific information",
            "don't have information about",
            "i don't have",
            "not available",
            "couldn't find",
            "no information about",
            "unable to find"
        ]

        response_lower = response.lower()
        return any(phrase in response_lower for phrase in admission_phrases)

    def _extract_question_type(self, query: str) -> str:
        """
        Extract the type of question being asked.

        Returns: 'who', 'what', 'when', 'where', 'why', 'how', 'what specific', etc.
        """
        query_lower = query.lower().strip()

        # Check for question words
        if query_lower.startswith('who is') or query_lower.startswith('who '):
            return 'who'
        elif query_lower.startswith('what is') and ('department chair' in query_lower or 'director' in query_lower or 'head' in query_lower):
            return 'who'  # "What is the department chair" is asking for a person
        elif query_lower.startswith('when is') or query_lower.startswith('when '):
            return 'when'
        elif query_lower.startswith('where is') or query_lower.startswith('where '):
            return 'where'
        elif query_lower.startswith('why is') or query_lower.startswith('why '):
            return 'why'
        elif query_lower.startswith('how do') or query_lower.startswith('how to') or query_lower.startswith('how '):
            return 'how'
        elif query_lower.startswith('what is the') or query_lower.startswith('what are the'):
            # Check if asking for specific thing
            if any(word in query_lower for word in ['deadline', 'date', 'time', 'cost', 'price', 'requirements', 'chair', 'director', 'head']):
                return 'what specific'
            return 'what'
        else:
            return 'general'

    def _answers_question_type(self, query: str, response: str, question_type: str) -> bool:
        """
        Check if response actually answers the type of question asked.
        """
        response_lower = response.lower()

        if question_type == 'who':
            # Should mention a person's name or role
            # Check for name patterns: "Dr. X", "Professor X", capitalized names
            has_person = bool(re.search(r'\b(Dr\.|Professor|Dr)\s+[A-Z][a-z]+', response))
            has_role_holder = any(word in response_lower for word in ['chair', 'director', 'head', 'dean', 'coordinator'])

            # If neither person nor role holder mentioned, likely not answering "who"
            if not has_person and not has_role_holder:
                # Unless it admits not knowing
                return self._admits_missing_info(response)

            return True

        elif question_type == 'when':
            # Should mention a date or time
            has_date = bool(re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December|\d{1,2}/\d{1,2}|\d{4})', response))
            has_time_word = any(word in response_lower for word in ['deadline', 'date', 'semester', 'year', 'month', 'day'])

            if not has_date and not has_time_word:
                return self._admits_missing_info(response)

            return True

        elif question_type == 'where':
            # Should mention a location
            has_location = any(word in response_lower for word in ['building', 'room', 'office', 'floor', 'campus', 'location', 'address'])

            if not has_location:
                return self._admits_missing_info(response)

            return True

        elif question_type == 'what specific':
            # Should provide the specific thing asked for, not general info
            # This is handled by tangential check
            return True

        # For other types, less strict
        return True

    def _check_entity_mentioned(self, query: str, response: str) -> bool:
        """
        For questions asking about specific entities (people, things),
        check if the entity is mentioned in the response.
        """
        # Extract what's being asked about
        query_lower = query.lower()

        # Common patterns: "who is the [X]", "what is the [X]"
        patterns = [
            r'who is the ([^?]+)',
            r'what is the ([^?]+)',
            r'who are the ([^?]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                entity = match.group(1).strip()

                # Check if response mentions this entity or provides a specific answer
                # If it just talks about related topics, that's tangential
                if entity in response.lower():
                    return True

                # Or if it provides a specific name/value
                has_specific_info = bool(re.search(r'\b(Dr\.|Professor|[A-Z][a-z]+\s+[A-Z][a-z]+)', response))
                return has_specific_info

        # If we can't determine, assume it's okay
        return True

    def _is_tangential_response(self, query: str, response: str) -> bool:
        """
        Detect if response is providing related information instead of
        answering the specific question.

        Classic hallucination: "Who is the chair?" → "The CS department offers many courses..."
        """
        # If response admits not knowing, it's not tangential
        if self._admits_missing_info(response):
            return False

        # Check for vague/general starts that often indicate tangential responses
        response_lower = response.lower().strip()

        tangential_starts = [
            'the cs department',
            'the computer science department',
            'the department offers',
            'the department provides',
            'the program includes',
            'there are many',
            'sfsu offers',
            'students can',
            'the university has'
        ]

        # If response starts with general department info, it might be tangential
        for start in tangential_starts:
            if response_lower.startswith(start):
                # Check if this is actually answering a "what does the department do" type question
                query_lower = query.lower()
                if any(word in query_lower for word in ['offers', 'provides', 'has', 'courses', 'programs']):
                    # Query is about what department offers, so response is relevant
                    return False
                else:
                    # Query is about something specific, but response is general
                    return True

        return False


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
# In llm_ollama.py, after generating response:

from services.relevance_checker import RelevanceChecker

relevance_checker = RelevanceChecker()

# After LLM generates response:
relevance = relevance_checker.check_relevance(query, answer, context)

if not relevance['is_relevant']:
    print(f"[RELEVANCE WARNING] Response not relevant: {relevance['issues']}")

    # Option 1: Regenerate with stricter prompt
    # Option 2: Use fallback response
    answer = "I don't have that specific information in my knowledge base. Please contact the relevant SFSU office for accurate details."
"""
