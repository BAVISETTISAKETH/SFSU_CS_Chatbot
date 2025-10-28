"""
Improved Web Search Service - Multi-Provider Support
Supports Tavily, Perplexity, Brave Search, and SerpAPI (fallback)
Optimized for LLM consumption with clean, structured data
"""

import os
import requests
from typing import Optional, List, Dict
from serpapi import GoogleSearch
from bs4 import BeautifulSoup


class ImprovedWebSearchService:
    """
    Production-ready web search with multiple provider support.
    Automatically selects best available API based on environment variables.
    """

    def __init__(self):
        """Initialize with best available search provider."""
        self.provider = self._detect_best_provider()
        self.ready = True

        print(f"[WEB SEARCH] Initialized with provider: {self.provider}")

    def _detect_best_provider(self) -> str:
        """
        Detect which search API to use based on available keys.
        Priority: Tavily > Perplexity > Brave > SerpAPI
        """
        if os.getenv("TAVILY_API_KEY"):
            return "tavily"
        elif os.getenv("PERPLEXITY_API_KEY"):
            return "perplexity"
        elif os.getenv("BRAVE_API_KEY"):
            return "brave"
        elif os.getenv("SERPAPI_KEY"):
            return "serpapi"
        else:
            print("[WARNING] No web search API key found. Web search will be disabled.")
            return "none"

    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready and self.provider != "none"

    async def search(self, query: str, num_results: int = 3) -> str:
        """
        Search the web using best available provider.
        Returns formatted, LLM-optimized results.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Formatted search results ready for LLM consumption
        """
        if self.provider == "none":
            return ""

        # Enhance query with SFSU context
        enhanced_query = f"San Francisco State University {query}"

        try:
            if self.provider == "tavily":
                return await self._search_tavily(enhanced_query, num_results)
            elif self.provider == "perplexity":
                return await self._search_perplexity(enhanced_query, num_results)
            elif self.provider == "brave":
                return await self._search_brave(enhanced_query, num_results)
            else:  # serpapi fallback
                return await self._search_serpapi(enhanced_query, num_results)

        except Exception as e:
            print(f"[ERROR] Web search error ({self.provider}): {e}")
            return ""

    # ========================================================================
    # TAVILY SEARCH (Best for LLMs - returns clean, structured data)
    # ========================================================================

    async def _search_tavily(self, query: str, num_results: int) -> str:
        """
        Search using Tavily API - optimized for AI/LLM consumption.
        Free tier: 1000 requests/month
        """
        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

            # Tavily returns clean, structured results perfect for LLMs
            response = client.search(
                query=query,
                max_results=num_results,
                include_answer=True,  # Tavily provides AI-generated summary
                include_raw_content=False,  # We want clean content, not raw HTML
                search_depth="advanced"  # More thorough search
            )

            formatted_results = []

            # Add Tavily's AI-generated answer if available
            if response.get("answer"):
                formatted_results.append(
                    f"[AI-Generated Summary]\n{response['answer']}\n"
                )

            # Add search results
            for i, result in enumerate(response.get("results", [])[:num_results]):
                formatted_results.append(
                    f"[Web Result {i+1}]\n"
                    f"Title: {result.get('title', '')}\n"
                    f"URL: {result.get('url', '')}\n"
                    f"Content: {result.get('content', '')}\n"
                    f"Relevance Score: {result.get('score', 0):.2f}\n"
                )

            return "\n".join(formatted_results)

        except ImportError:
            print("[ERROR] Tavily not installed. Run: pip install tavily-python")
            return ""
        except Exception as e:
            print(f"[ERROR] Tavily search failed: {e}")
            return ""

    # ========================================================================
    # PERPLEXITY SEARCH (AI-native search with built-in citations)
    # ========================================================================

    async def _search_perplexity(self, query: str, num_results: int) -> str:
        """
        Search using Perplexity API - AI-native search with citations.
        Check if free with student account (Comet browser enrollment).
        """
        try:
            api_key = os.getenv("PERPLEXITY_API_KEY")

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-medium-online",  # Online model with search
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Provide accurate information about SFSU with citations."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "return_citations": True,
                    "return_images": False
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Perplexity returns AI-generated answer with citations
                answer = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])

                formatted_result = f"[Perplexity AI Search]\n{answer}\n\n"

                if citations:
                    formatted_result += "Sources:\n"
                    for i, url in enumerate(citations[:num_results], 1):
                        formatted_result += f"{i}. {url}\n"

                return formatted_result
            else:
                print(f"[ERROR] Perplexity API error: {response.status_code}")
                return ""

        except Exception as e:
            print(f"[ERROR] Perplexity search failed: {e}")
            return ""

    # ========================================================================
    # BRAVE SEARCH (Free tier: 2000 requests/month, no CC required)
    # ========================================================================

    async def _search_brave(self, query: str, num_results: int) -> str:
        """
        Search using Brave Search API - generous free tier.
        """
        try:
            api_key = os.getenv("BRAVE_API_KEY")

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": api_key
                },
                params={
                    "q": query,
                    "count": num_results
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                formatted_results = []

                for i, result in enumerate(data.get("web", {}).get("results", [])[:num_results], 1):
                    formatted_results.append(
                        f"[Web Result {i}]\n"
                        f"Title: {result.get('title', '')}\n"
                        f"URL: {result.get('url', '')}\n"
                        f"Description: {result.get('description', '')}\n"
                    )

                    # Fetch full content if URL is available
                    if result.get("url"):
                        full_content = self._fetch_webpage_content(result["url"])
                        if full_content:
                            formatted_results[-1] += f"Full Content: {full_content}\n"

                return "\n".join(formatted_results)
            else:
                print(f"[ERROR] Brave API error: {response.status_code}")
                return ""

        except Exception as e:
            print(f"[ERROR] Brave search failed: {e}")
            return ""

    # ========================================================================
    # SERPAPI (Fallback - requires existing key)
    # ========================================================================

    async def _search_serpapi(self, query: str, num_results: int) -> str:
        """
        Search using SerpAPI (fallback option).
        Uses existing web_search.py logic.
        """
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": os.getenv("SERPAPI_KEY"),
                "num": num_results
            })

            results = search.get_dict()
            formatted_results = []

            if "organic_results" in results:
                for i, result in enumerate(results["organic_results"][:num_results], 1):
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")

                    # Fetch full content
                    print(f"[INFO] Fetching content from: {link}")
                    full_content = self._fetch_webpage_content(link, max_length=5000)

                    if full_content:
                        formatted_results.append(
                            f"[Web Result {i}]\n"
                            f"Title: {title}\n"
                            f"URL: {link}\n"
                            f"Content: {full_content}\n"
                        )
                    else:
                        formatted_results.append(
                            f"[Web Result {i}]\n"
                            f"Title: {title}\n"
                            f"Snippet: {snippet}\n"
                            f"URL: {link}\n"
                        )

                return "\n".join(formatted_results)

            return ""

        except Exception as e:
            print(f"[ERROR] SerpAPI search failed: {e}")
            return ""

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _fetch_webpage_content(self, url: str, max_length: int = 3000) -> str:
        """
        Fetch and extract text content from a webpage.
        Used when search API doesn't provide full content.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # Get text
            text = soup.get_text(separator=' ', strip=True)

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit length
            if len(text) > max_length:
                text = text[:max_length] + "..."

            return text

        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return ""


# ============================================================================
# USAGE INSTRUCTIONS
# ============================================================================

"""
To use improved web search, set ONE of these environment variables in .env:

1. TAVILY_API_KEY (RECOMMENDED - best for LLMs)
   - Get free API key at: https://tavily.com/
   - Free tier: 1000 requests/month
   - Install: pip install tavily-python

2. PERPLEXITY_API_KEY (if you have student access via Comet)
   - Check if included with your Comet browser student enrollment
   - AI-native search with built-in citations

3. BRAVE_API_KEY (Good free tier - no credit card)
   - Get free API key at: https://brave.com/search/api/
   - Free tier: 2000 requests/month
   - No credit card required

4. SERPAPI_KEY (Fallback - if you already have it)
   - Uses existing SerpAPI subscription

Priority: Tavily > Perplexity > Brave > SerpAPI

Example .env:
```
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

Then update main.py to use this service instead of WebSearchService.
"""
