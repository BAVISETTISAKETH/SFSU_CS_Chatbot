"""
Web Search Service - SerpAPI Integration
Provides current web information when RAG confidence is low
Fetches full webpage content for detailed answers
"""

import os
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from typing import Optional, List, Dict

class WebSearchService:
    """Service for web search using SerpAPI."""

    def __init__(self):
        """Initialize SerpAPI client."""
        api_key = os.getenv("SERPAPI_KEY")

        if not api_key:
            print("[WARNING]  Warning: SERPAPI_KEY not set. Web search will be disabled.")
            self.enabled = False
        else:
            self.api_key = api_key
            self.enabled = True

        self.ready = True

    def is_ready(self) -> bool:
        """Check if service is ready."""
        return self.ready

    def _fetch_webpage_content(self, url: str, max_length: int = 3000) -> str:
        """
        Fetch and extract text content from a webpage.

        Args:
            url: URL to fetch
            max_length: Maximum characters to return

        Returns:
            Cleaned text content from webpage
        """
        try:
            # Set timeout and headers
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

    async def search(self, query: str, num_results: int = 3) -> str:
        """
        Search the web, fetch full page content, and return formatted results.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Formatted search results with full page content
        """
        if not self.enabled:
            return ""

        try:
            # Enhance query with SFSU context
            enhanced_query = f"San Francisco State University {query}"

            # Perform search
            search = GoogleSearch({
                "q": enhanced_query,
                "api_key": self.api_key,
                "num": num_results
            })

            results = search.get_dict()

            # Format results with full content
            if "organic_results" in results:
                formatted_results = []

                for i, result in enumerate(results["organic_results"][:num_results]):
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")

                    # Fetch full webpage content (increased to 5000 chars for more detail)
                    print(f"[INFO] Fetching content from: {link}")
                    full_content = self._fetch_webpage_content(link, max_length=5000)

                    if full_content:
                        # Use full content if available
                        formatted_results.append(
                            f"[Web Result {i+1}]\n"
                            f"Title: {title}\n"
                            f"URL: {link}\n"
                            f"Content: {full_content}\n"
                        )
                    else:
                        # Fallback to snippet if fetch fails
                        formatted_results.append(
                            f"[Web Result {i+1}]\n"
                            f"Title: {title}\n"
                            f"Snippet: {snippet}\n"
                            f"URL: {link}\n"
                        )

                return "\n".join(formatted_results)

            return ""

        except Exception as e:
            print(f"[ERROR] Web search error: {e}")
            return ""
