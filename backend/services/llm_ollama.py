"""
LLM Service - Ollama DeepSeek Integration
Uses DeepSeek-R1 for high-quality responses with NO rate limits
"""

import re
import requests
from typing import Optional, List, Dict
from .relevance_checker import RelevanceChecker

class OllamaLLMService:
    """Service for interacting with Ollama (DeepSeek) API."""

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = "http://localhost:11434"
        self.model = "Deepseek-R1:7b"  # DeepSeek R1 7B - Reasoning-optimized with anti-hallucination system
        self.ready = self._check_ollama_ready()
        self.relevance_checker = RelevanceChecker()  # NEW: Check if responses answer the question

        # System prompt - Clean and simple
        self.system_prompt_rag = """You are Alli, an AI assistant for San Francisco State University.

=== ABSOLUTE RULES - VIOLATION = SYSTEM FAILURE ===

1. READ THE QUESTION CAREFULLY - Answer EXACTLY what is asked, nothing else
2. ONLY use information EXPLICITLY in the context below
3. If the EXACT answer to the question is NOT in the context, respond ONLY: "I don't have that specific information in my knowledge base. Please contact [relevant office] or visit sfsu.edu for accurate details."
4. DO NOT provide related information if it doesn't answer the exact question
5. DO NOT use general knowledge - CONTEXT ONLY
6. DO NOT say "I think", "probably", "might be", "it seems"
7. DO NOT make up names, dates, URLs, phone numbers, or any details

EXAMPLE:
Question: "Who is the department chair for CS?"
Context: "The CS department offers many courses..."
CORRECT Response: "I don't have information about the current department chair in my knowledge base. Please contact the CS department directly or visit cs.sfsu.edu."
WRONG Response: "The CS department offers many courses..." (This doesn't answer the question!)

CRITICAL: Answer the EXACT question asked. If you cannot answer it from the context, admit it. Do not provide tangential information."""

        self.system_prompt_dual_source = """You are Alli, an AI assistant for San Francisco State University.

=== ABSOLUTE RULES - VIOLATION = SYSTEM FAILURE ===

YOU HAVE TWO INFORMATION SOURCES:
1. [Local] = Local Knowledge Base (pre-scraped SFSU documents)
2. [Web] = Live Web Search (current SFSU websites)

CRITICAL INSTRUCTION:
1. READ THE QUESTION CAREFULLY - Answer EXACTLY what is asked
2. ONLY use information EXPLICITLY in the sources below
3. EVERY factual claim MUST cite [Local] or [Web]
4. If the EXACT answer is NOT in either source, respond: "I don't have that specific information in either my local knowledge base [Local] or current web results [Web]. Please contact [relevant office] or visit sfsu.edu."
5. DO NOT provide related/tangential information - answer the EXACT question or admit you don't have it
6. DO NOT use general knowledge
7. DO NOT make up names, dates, URLs, phone numbers, or details

EXAMPLE OF CORRECT BEHAVIOR:
Question: "Who is the department chair for CS?"
Sources: "The CS department offers many courses in AI, databases..." (no chair mentioned)
CORRECT: "I don't have information about the current CS department chair in either source [Local][Web]. Please contact the CS department at cs.sfsu.edu."
WRONG: "The CS department offers courses in AI and databases..." (Doesn't answer the question!)

MANDATORY CITATION FORMAT:
- "Dr. Jane Smith is the chair [Local]"
- "The deadline is May 1, 2025 [Web]"
- If both sources agree: "The program requires 30 units [Local][Web]"

CONFLICT HANDLING:
- If sources differ: "My local knowledge shows March 1 [Local], but current web results show April 1 [Web]. The web information is more recent."

FORBIDDEN:
- ❌ Answering a different question than asked
- ❌ Providing related info when exact answer is missing
- ❌ Inventing information
- ❌ Using phrases: "I think", "probably", "might be", "it seems"
- ❌ Responses without [Local] or [Web] citations

REMEMBER: Answer the EXACT question with EXACT information from sources, or admit you don't have it. No tangents."""

    def _check_ollama_ready(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                return self.model in model_names
            return False
        except:
            return False

    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text to avoid encoding issues."""
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

    async def generate_response(
        self,
        query: str,
        context: str,
        use_web_context: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using Ollama DeepSeek.

        Args:
            query: User's question
            context: Retrieved context (from RAG or web search)
            use_web_context: Whether context includes web search results
            conversation_history: Previous conversation turns

        Returns:
            Generated response text
        """
        try:
            # Choose appropriate system prompt
            system_prompt = self.system_prompt_web if use_web_context else self.system_prompt_rag

            # Build messages
            messages = []

            # Add system prompt
            messages.append({"role": "system", "content": system_prompt})

            # Add conversation history (last 3 exchanges)
            if conversation_history:
                messages.extend(conversation_history[-6:])

            # Truncate context if too long
            max_context_length = 15000  # Ollama can handle more context
            if len(context) > max_context_length:
                context = context[:max_context_length] + "\n\n[Context truncated - showing most relevant information]"

            # Build user prompt - STRICT and explicit
            user_prompt = f"""QUESTION TO ANSWER: {query}

CONTEXT (your ONLY source of information):
{context}

INSTRUCTIONS:
1. Read the question carefully: "{query}"
2. Search the context above for the EXACT answer to this specific question
3. If you find the exact answer → Provide it clearly with source citation
4. If you DO NOT find the exact answer → Say "I don't have that specific information in my knowledge base"
5. DO NOT provide related information that doesn't answer the question
6. DO NOT talk about general topics - answer THIS specific question only

YOUR RESPONSE (answer the question "{query}" or admit you don't have it):"""

            messages.append({"role": "user", "content": user_prompt})

            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # ZERO hallucination tolerance - deterministic responses only
                        "num_predict": 2000,  # Max tokens
                        "top_p": 0.9,  # Balanced
                        "repeat_penalty": 1.1  # Slight penalty for repetition
                    }
                },
                timeout=120  # 2 minute timeout
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get('message', {}).get('content', '').strip()

                # Clean up any thinking tags (DeepSeek-R1 uses these)
                if "<think>" in answer and "</think>" in answer:
                    # Remove thinking tags and everything between them
                    import re
                    answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()

                # Remove emojis
                answer = self._remove_emojis(answer)

                # CRITICAL: Check if response is relevant to the question
                relevance = self.relevance_checker.check_relevance(query, answer, context)

                if not relevance['is_relevant'] and not relevance['admits_missing']:
                    print(f"[RELEVANCE CHECK FAILED] Response doesn't answer the question!")
                    print(f"  Question: {query}")
                    print(f"  Issues: {relevance['issues']}")
                    print(f"  Replacing with admission of missing info...")

                    # Replace with honest "don't know" response
                    answer = "I don't have that specific information in my knowledge base. I'd recommend contacting the relevant SFSU office or checking sfsu.edu for accurate details."

                return answer
            else:
                print(f"[ERROR] Ollama API error: {response.status_code} - {response.text}")
                return "I'm having trouble generating a response. Please try again."

        except requests.Timeout:
            return "The request took too long to process. Please try asking in a simpler way."
        except Exception as e:
            print(f"[ERROR] Error generating response: {e}")
            return "I'm sorry, I'm having trouble generating a response right now. Please try again."

    async def generate_dual_source_response(
        self,
        query: str,
        combined_context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Generate response using dual-source context with ZERO hallucination tolerance.

        Args:
            query: User's question
            combined_context: Merged context from both sources (formatted by ContextMerger)
            conversation_history: Previous conversation turns

        Returns:
            Dict with response, validation results, and metadata
        """
        try:
            # Use dual-source system prompt
            system_prompt = self.system_prompt_dual_source

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history (last 3 exchanges)
            if conversation_history:
                messages.extend(conversation_history[-6:])

            # Truncate context if too long
            max_context_length = 30000
            if len(combined_context) > max_context_length:
                combined_context = combined_context[:max_context_length] + "\n\n[Context truncated]"

            # Dual-source prompt - STRICT
            user_prompt = f"""QUESTION TO ANSWER: {query}

{combined_context}

CRITICAL INSTRUCTIONS:
1. Read the question carefully: "{query}"
2. Search BOTH sources above for the EXACT answer to this specific question
3. If you find the exact answer → Provide it with [Local] or [Web] citation
4. If the exact answer is NOT in either source → Say "I don't have that specific information in either my local knowledge base [Local] or current web results [Web]"
5. DO NOT provide related/tangential information - answer THIS specific question only
6. Cite EVERY fact as [Local] or [Web]
7. If sources conflict, show both with citations

EXAMPLE:
Question: "Who is the department chair?"
If NOT in sources → "I don't have information about the current department chair [Local][Web]. Please contact the department directly."
If in sources → "Dr. Jane Smith is the department chair [Local]"

YOUR RESPONSE (answer "{query}" exactly, with [Local]/[Web] citations, or admit you don't have it):"""

            messages.append({"role": "user", "content": user_prompt})

            # Call Ollama API with temperature 0.0
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # ZERO hallucination tolerance
                        "num_predict": 2000,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get('message', {}).get('content', '').strip()

                # Clean up thinking tags
                if "<think>" in answer and "</think>" in answer:
                    import re
                    answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()

                # Remove emojis
                answer = self._remove_emojis(answer)

                # CRITICAL: Check if response is relevant to the question
                relevance = self.relevance_checker.check_relevance(query, answer, combined_context)

                if not relevance['is_relevant'] and not relevance['admits_missing']:
                    print(f"[RELEVANCE CHECK FAILED] Response doesn't answer the question!")
                    print(f"  Question: {query}")
                    print(f"  Issues: {relevance['issues']}")
                    print(f"  Replacing with admission of missing info...")

                    # Replace with honest "don't know" response
                    answer = "I don't have that specific information in either my local knowledge base [Local] or current web results [Web]. Please contact the relevant SFSU office or visit sfsu.edu for accurate details."

                # Basic validation
                has_local = '[Local]' in answer or '[local]' in answer
                has_web = '[Web]' in answer or '[web]' in answer
                citation_count = answer.count('[Local]') + answer.count('[local]') + answer.count('[Web]') + answer.count('[web]')

                return {
                    'response': answer,
                    'validated': has_local or has_web,
                    'has_citations': has_local or has_web,
                    'citation_count': citation_count,
                    'validation_warnings': [] if (has_local or has_web) else ['No source citations found'],
                    'relevance_check': relevance
                }
            else:
                print(f"[ERROR] Ollama API error: {response.status_code}")
                return {
                    'response': "I'm having trouble generating a response. Please try again.",
                    'validated': False,
                    'has_citations': False,
                    'citation_count': 0,
                    'error': f'API error: {response.status_code}'
                }

        except requests.Timeout:
            return {
                'response': "The request took too long to process. Please try asking in a simpler way.",
                'validated': False,
                'has_citations': False,
                'citation_count': 0,
                'error': 'timeout'
            }
        except Exception as e:
            print(f"[ERROR] Error generating dual-source response: {e}")
            return {
                'response': "I'm sorry, I'm having trouble generating a response right now. Please try again.",
                'validated': False,
                'has_citations': False,
                'citation_count': 0,
                'error': str(e)
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
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "num_predict": 512
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()

                # Clean up thinking tags
                if "<think>" in answer and "</think>" in answer:
                    import re
                    answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()

                return answer
            else:
                return "I'm sorry, I encountered an error processing your request."

        except Exception as e:
            print(f"[ERROR] Error generating simple response: {e}")
            return "I'm sorry, I encountered an error processing your request."
