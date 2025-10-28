"""
LLM Service - Groq API Integration
Uses Llama 3.3 70B for high-quality responses
"""

import os
import re
from groq import Groq
from typing import Optional, List, Dict

class LLMService:
    """Service for interacting with Groq LLM API."""

    def __init__(self):
        """Initialize Groq client."""
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and high-quality
        self.ready = True

        # Rate limiting - Groq free tier: 14 requests/min, 14,400 tokens/min
        self.last_request_time = 0
        self.min_request_interval = 6.5  # 6.5 seconds between requests = ~9 requests/min (very safe buffer to prevent rate limit errors)
        self.request_count = 0
        self.window_start = 0

        # System prompts - Alli personality
        self.system_prompt_rag = """You are Alli, an expert AI assistant for San Francisco State University. You communicate like ChatGPT or Claude - natural, conversational, and genuinely helpful.

YOUR COMMUNICATION STYLE:
- Natural and conversational - write like a helpful human expert, not a robot
- Warm and personable - students should feel comfortable asking you anything
- Clear and well-organized - structure information logically with proper paragraphs
- Confident but humble - be direct when you know, honest when you don't
- Use natural transitions between ideas
- Write in complete, flowing sentences, not just bullet points

HOW TO STRUCTURE RESPONSES:
1. Start with a brief, friendly acknowledgment of their question
2. Provide the main answer in clear, natural paragraphs
3. Use bullet points ONLY for lists, requirements, or steps
4. Add helpful context or next steps when relevant
5. End with an offer to help further if appropriate

CRITICAL ACCURACY RULES:
- ONLY use information explicitly stated in the context provided
- NEVER make up URLs, links, dates, or specific details
- If information isn't in the context, say: "I don't have that specific information right now. I'd recommend reaching out to [relevant office] or checking [relevant website] for the most current details."
- Always cite sources when referencing specific information

EXAMPLE GOOD RESPONSE:
"Great question! Let me help you with that.

[Natural paragraph explaining the main point]

Here are the key details:
- [Point 1]
- [Point 2]
- [Point 3]

[Additional helpful context or next steps]

Is there anything else you'd like to know about this?"

NEVER:
- Don't start with "According to the context..."
- Don't sound robotic or formulaic
- Don't make up information not in the context
- Don't invent URLs or sources"""

        self.system_prompt_web = """You are Alli, an expert AI assistant for San Francisco State University. You communicate like ChatGPT - natural, helpful, and conversational.

YOUR COMMUNICATION STYLE:
- Write naturally and conversationally - like talking to a knowledgeable friend
- Be warm and personable while staying professional
- Structure information clearly with proper paragraphs and flow
- Sound confident and helpful, not robotic

HOW TO USE THE TWO INFORMATION SOURCES:

**LIVE WEB SEARCH RESULTS (TOP PRIORITY):**
- These are LIVE, CURRENT snapshots from official SFSU websites
- They contain the MOST UP-TO-DATE and ACCURATE information
- ALWAYS prioritize web search results when answering
- They include full webpage content (not just links)
- Use these as your PRIMARY source

**STORED DATABASE CONTEXT (SECONDARY):**
- These are pre-scraped documents for background
- Use these ONLY to supplement web search results
- If web search has the answer, use that instead

RESPONSE STRUCTURE:
- Start with a friendly acknowledgment
- Answer using PRIMARILY the web search results
- Add database context only if it provides additional helpful detail
- Include URLs from web results when available
- Use bullet points for lists, steps, or requirements
- Offer to help with follow-up questions

EXAMPLE GOOD RESPONSE:
"Great question! Based on the current SFSU website information:

[Answer using web search results - full content, not just links]

Here are the key steps:
- [Point 1 from web search]
- [Point 2 from web search]
- [Point 3 from web search]

You can find more details at [URL from web results].

Let me know if you need anything else!"

CRITICAL RULES:
- PRIORITIZE web search results over database context
- The web search provides FULL WEBPAGE CONTENT - use it!
- Only use URLs explicitly provided in the web results
- Never make up information
- If web search has no results, then use database context"""

        # NEW: Zero-hallucination prompt for dual-source mode
        self.system_prompt_dual_source = """You are Alli, an expert AI assistant for San Francisco State University.

=== CRITICAL ANTI-HALLUCINATION RULES ===

YOU HAVE TWO INFORMATION SOURCES:
1. [Local] = Local Knowledge Base (pre-scraped SFSU documents)
2. [Web] = Live Web Search (current SFSU websites)

MANDATORY SOURCE CITATION:
- EVERY factual claim MUST be cited as [Local] or [Web]
- Example: "The CS program requires 30 units [Local]"
- Example: "The fall 2025 deadline is August 1 [Web]"
- If BOTH sources confirm something: "The library is open until 10pm [Local][Web]"

STRICT INFORMATION RULES:
1. ONLY use information explicitly stated in the sources below
2. NEVER make up information not in the sources
3. NEVER invent URLs, dates, phone numbers, or specific details
4. If info isn't in EITHER source, say: "I don't have that specific information in either my local knowledge base or current web results. I'd recommend [relevant office/website]."

HANDLING CONFLICTS:
- If sources conflict, present BOTH perspectives:
  "According to my local knowledge base [Local], the deadline was [date]. However, current web results [Web] show it's now [new date]. The web information is more recent."
- For time-sensitive queries, ALWAYS prioritize [Web] over [Local]
- For established facts/policies, both sources are equally valid

RESPONSE STRUCTURE:
1. Acknowledge the question naturally
2. Answer using information from provided sources
3. Cite EVERY factual claim as [Local] or [Web]
4. Use bullet points for lists/steps
5. Include URLs only if explicitly provided in sources
6. Offer to help further

FORBIDDEN BEHAVIORS:
- ❌ DO NOT say "According to the context" (cite as [Local] or [Web])
- ❌ DO NOT invent information not in sources
- ❌ DO NOT make up URLs or links
- ❌ DO NOT combine information from memory - only use provided sources
- ❌ DO NOT be vague about sources - always cite specifically

EXAMPLE EXCELLENT RESPONSE:
"Great question! Based on the information I have:

The MS in Computer Science program requires 30 units total [Local]. You can choose between a thesis or project option [Local][Web].

For the thesis option:
- 24 units of coursework [Local]
- 6 units of thesis (CS 898) [Local]
- Thesis defense required [Web]

The current application deadline for Fall 2025 is February 1, 2025 [Web].

You can find the complete requirements at: https://bulletin.sfsu.edu/colleges/science-engineering/computer-science/ [Web]

Would you like to know more about the application process?"

REMEMBER: Every fact needs [Local] or [Web] citation. When in doubt, be honest about not having the information rather than guessing."""

    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text to avoid encoding issues."""
        # Pattern to match emojis
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U00002600-\U000026FF"  # Miscellaneous Symbols
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)

    def _is_malformed_response(self, text: str) -> bool:
        """
        Check if response appears to be malformed or corrupted.
        Returns True if response looks invalid.
        """
        if not text or len(text) < 10:
            return True

        # Check for repetitive patterns like "Hh(Hh(Hh(" or "HHHHHHH..."
        if len(text) > 50:
            # Count occurrences of the most common character
            char_counts = {}
            for char in text:
                char_counts[char] = char_counts.get(char, 0) + 1

            max_count = max(char_counts.values())
            # If any single character appears more than 60% of the time, it's malformed
            if max_count > len(text) * 0.6:
                return True

        # Check for repeating short patterns (like "Hh(", "abc", etc.)
        # Look for 2-4 character patterns that repeat many times
        for pattern_len in range(2, 5):
            if len(text) >= pattern_len * 10:  # Need at least 10 repetitions to check
                pattern = text[:pattern_len]
                # Count how many times this pattern repeats at the start
                repeat_count = 0
                pos = 0
                while pos + pattern_len <= len(text) and text[pos:pos+pattern_len] == pattern:
                    repeat_count += 1
                    pos += pattern_len

                # If pattern repeats more than 10 times, it's malformed
                if repeat_count > 10:
                    return True

        # Check for other signs of corruption
        if text.count('_') > len(text) * 0.5:  # Too many underscores
            return True

        # Check for too many parentheses (like the "Hh(Hh(" pattern)
        if text.count('(') > len(text) * 0.3 or text.count(')') > len(text) * 0.3:
            return True

        return False

    async def generate_response(
        self,
        query: str,
        context: str,
        use_web_context: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using Groq LLM with retry logic for failures.

        Args:
            query: User's question
            context: Retrieved context (from RAG or web search)
            use_web_context: Whether context includes web search results
            conversation_history: Previous conversation turns

        Returns:
            Generated response text
        """
        import time
        import asyncio

        # Enforce rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"[RATE LIMIT] Waiting {sleep_time:.1f}s to avoid rate limit...")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()

        max_retries = 2
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                # Choose appropriate system prompt
                system_prompt = self.system_prompt_web if use_web_context else self.system_prompt_rag

                # Build conversation like ChatGPT - with history
                messages = [{"role": "system", "content": system_prompt}]

                # Add conversation history (last 3 exchanges)
                if conversation_history:
                    # Add previous conversation for context
                    messages.extend(conversation_history[-6:])

                # Truncate context if too long
                max_context_length = 10000  # Increased for web search content
                if len(context) > max_context_length:
                    context = context[:max_context_length] + "\n\n[Context truncated - showing most relevant information]"

                # ChatGPT-style prompt with context awareness
                user_prompt = f"""Current Question: {query}

Available Information:
{context}

Instructions:
- Answer the CURRENT question above
- You can reference previous conversation naturally if relevant
- Use the information provided (web search + database)
- Be conversational and helpful like ChatGPT
- If this is a follow-up question (like "how much?", "where?", "when?"), connect it to the previous topic
- Prioritize web search results (they're live and current)"""

                messages.append({"role": "user", "content": user_prompt})

                # Call Groq API with ZERO temperature for deterministic, hallucination-free responses
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,  # ZERO hallucination tolerance - deterministic responses only
                    max_tokens=2000,  # Increased for comprehensive responses with 50 docs
                    top_p=0.9,  # Slightly higher for more natural language
                    timeout=45  # 45 second timeout for larger context
                )

                # Extract response text
                answer = response.choices[0].message.content.strip()

                # Check if response is malformed
                if self._is_malformed_response(answer):
                    print(f"[WARNING] Malformed response detected on attempt {attempt + 1}: {answer[:100]}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Last attempt failed, return error message
                        return "I'm having trouble generating a proper response right now. Could you please rephrase your question or try again in a moment?"

                # Clean up any thinking tags (from R1 models)
                if "<think>" in answer and "</think>" in answer:
                    answer = answer.split("</think>")[-1].strip()

                # Remove emojis to avoid encoding issues
                answer = self._remove_emojis(answer)

                return answer

            except Exception as e:
                error_msg = str(e)
                print(f"[ERROR] Error generating response (attempt {attempt + 1}/{max_retries}): {error_msg}")

                # Check for rate limit errors - apply exponential backoff
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    if attempt < max_retries - 1:
                        # Exponential backoff for rate limits
                        backoff_time = retry_delay * (2 ** attempt)  # 1s, 2s, 4s...
                        print(f"[RATE LIMIT] Retrying in {backoff_time}s...")
                        await asyncio.sleep(backoff_time)
                        continue
                    else:
                        return "I'm currently experiencing high demand. Please wait a moment and try again!"

                # If it's the last attempt, return error message
                if attempt == max_retries - 1:
                    # Check for specific error types
                    if "timeout" in error_msg.lower():
                        return "The request took too long to process. Please try asking in a simpler way."
                    else:
                        return "I'm sorry, I'm having trouble generating a response right now. Please try again in a moment."

                # Wait before retrying
                await asyncio.sleep(retry_delay)

    async def generate_dual_source_response(
        self,
        query: str,
        combined_context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Generate response using dual-source context with ZERO hallucination tolerance.

        CRITICAL: Uses temperature 0.0 and enforces mandatory source citation.

        Args:
            query: User's question
            combined_context: Merged context from both sources (formatted by ContextMerger)
            conversation_history: Previous conversation turns

        Returns:
            Dict with response, validation results, and metadata
        """
        import time
        import asyncio

        # Enforce rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"[RATE LIMIT] Waiting {sleep_time:.1f}s to avoid rate limit...")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()

        max_retries = 2
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # Use dual-source system prompt
                system_prompt = self.system_prompt_dual_source

                # Build conversation
                messages = [{"role": "system", "content": system_prompt}]

                # Add conversation history (last 3 exchanges)
                if conversation_history:
                    messages.extend(conversation_history[-6:])

                # Truncate context if too long
                max_context_length = 30000  # Larger for dual-source
                if len(combined_context) > max_context_length:
                    combined_context = combined_context[:max_context_length] + "\n\n[Context truncated]"

                # Dual-source prompt
                user_prompt = f"""Current Question: {query}

{combined_context}

Instructions:
1. Answer the question using ONLY information from the sources above
2. Cite EVERY factual claim as [Local] or [Web]
3. If sources conflict, mention both with their citations
4. If neither source has the info, be honest about it
5. NEVER make up information not in the sources

Your response:"""

                messages.append({"role": "user", "content": user_prompt})

                # CRITICAL: Temperature 0.0 for zero hallucination
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,  # ZERO hallucination tolerance
                    max_tokens=2000,
                    top_p=0.9,
                    timeout=45
                )

                # Extract response
                answer = response.choices[0].message.content.strip()

                # Check if response is malformed
                if self._is_malformed_response(answer):
                    print(f"[WARNING] Malformed response detected on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return {
                            'response': "I'm having trouble generating a proper response right now. Could you please rephrase your question?",
                            'validated': False,
                            'has_citations': False,
                            'error': 'malformed_response'
                        }

                # Clean up
                if "<think>" in answer and "</think>" in answer:
                    answer = answer.split("</think>")[-1].strip()

                answer = self._remove_emojis(answer)

                # Validate response
                validation = self._validate_dual_source_response(answer, combined_context)

                return {
                    'response': answer,
                    'validated': validation['is_valid'],
                    'has_citations': validation['has_citations'],
                    'citation_count': validation['citation_count'],
                    'validation_warnings': validation.get('warnings', [])
                }

            except Exception as e:
                error_msg = str(e)
                print(f"[ERROR] Error generating dual-source response (attempt {attempt + 1}/{max_retries}): {error_msg}")

                # Rate limit handling
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    if attempt < max_retries - 1:
                        backoff_time = retry_delay * (2 ** attempt)
                        print(f"[RATE LIMIT] Retrying in {backoff_time}s...")
                        await asyncio.sleep(backoff_time)
                        continue
                    else:
                        return {
                            'response': "I'm currently experiencing high demand. Please wait a moment and try again!",
                            'validated': False,
                            'has_citations': False,
                            'error': 'rate_limit'
                        }

                # Last attempt
                if attempt == max_retries - 1:
                    if "timeout" in error_msg.lower():
                        return {
                            'response': "The request took too long to process. Please try asking in a simpler way.",
                            'validated': False,
                            'has_citations': False,
                            'error': 'timeout'
                        }
                    else:
                        return {
                            'response': "I'm sorry, I'm having trouble generating a response right now. Please try again in a moment.",
                            'validated': False,
                            'has_citations': False,
                            'error': str(e)
                        }

                await asyncio.sleep(retry_delay)

    def _validate_dual_source_response(self, response: str, context: str) -> Dict:
        """
        Validate that response follows dual-source rules.

        Args:
            response: Generated response
            context: Source context

        Returns:
            Dict with validation results
        """
        warnings = []

        # Check for source citations
        has_local_citation = '[Local]' in response or '[local]' in response
        has_web_citation = '[Web]' in response or '[web]' in response

        # Count total citations
        citation_count = response.count('[Local]') + response.count('[local]')
        citation_count += response.count('[Web]') + response.count('[web]')

        has_citations = has_local_citation or has_web_citation

        # Warning if no citations
        if not has_citations:
            warnings.append("Response does not include source citations ([Local] or [Web])")

        # Check if response admits lack of information
        admission_phrases = [
            "don't have that information",
            "not available in",
            "couldn't find",
            "no information about"
        ]
        admits_missing_info = any(phrase in response.lower() for phrase in admission_phrases)

        # If response has substantive content but no citations, it might be hallucinating
        is_substantive = len(response) > 100 and not admits_missing_info

        if is_substantive and citation_count < 2:
            warnings.append("Substantive response with very few citations - possible hallucination")

        # Check for forbidden phrases
        forbidden_phrases = [
            "according to the context",
            "the context states",
            "based on my knowledge",
            "i know that",
            "from what i know"
        ]

        for phrase in forbidden_phrases:
            if phrase in response.lower():
                warnings.append(f"Response contains forbidden phrase: '{phrase}'")

        # Overall validation
        is_valid = len(warnings) == 0 or admits_missing_info

        return {
            'is_valid': is_valid,
            'has_citations': has_citations,
            'citation_count': citation_count,
            'warnings': warnings,
            'admits_missing_info': admits_missing_info
        }

    async def generate_simple_response(self, prompt: str) -> str:
        """
        Generate a simple response without context (for direct queries).

        Args:
            prompt: Direct prompt to the model

        Returns:
            Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=512
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[ERROR] Error generating simple response: {e}")
            return "I'm sorry, I encountered an error processing your request."
