"""
AGGRESSIVE SFSU Web Scraper
Crawls the ENTIRE cs.sfsu.edu domain and related SFSU pages
Gets ACTUAL content, not just URLs
"""

import requests
from bs4 import BeautifulSoup
from typing import Set, List, Dict
import json
import time
from urllib.parse import urljoin, urlparse
import re

class AggressiveSFSUScraper:
    """Aggressive web crawler for SFSU."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        self.to_visit: Set[str] = set()
        self.max_pages = 200  # Scrape up to 200 pages

        # Seed URLs
        self.seed_urls = [
            "https://cs.sfsu.edu/",
            "https://bulletin.sfsu.edu/colleges/science-engineering/computer-science/",
            "https://bulletin.sfsu.edu/courses/csc/",
        ]

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for scraping."""
        parsed = urlparse(url)

        # Must be SFSU domain
        if not any(domain in parsed.netloc for domain in ['cs.sfsu.edu', 'bulletin.sfsu.edu']):
            return False

        # Skip common non-content URLs
        skip_patterns = [
            r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$',
            r'\.zip$', r'\.doc$', r'\.ppt$',
            r'/login', r'/admin', r'/wp-admin',
            r'/wp-content', r'/wp-includes',
            r'#', r'javascript:', r'mailto:',
        ]

        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all valid links from page."""
        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)

            if self.is_valid_url(full_url):
                links.add(full_url)

        return links

    def scrape_page(self, url: str) -> bool:
        """Scrape a single page and extract links."""
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return False

        try:
            print(f"[{len(self.visited_urls)+1}/{self.max_pages}] {url}")

            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            self.visited_urls.add(url)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract new links to visit
            new_links = self.extract_links(soup, url)
            self.to_visit.update(new_links - self.visited_urls)

            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                tag.decompose()

            # Get main content
            main = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', class_=re.compile('content|main|body')) or
                soup.find('div', id=re.compile('content|main|body'))
            )

            content_area = main if main else soup.body

            if not content_area:
                return False

            # Extract text
            text = content_area.get_text(separator='\n', strip=True)
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

            # Only save if substantial content
            if len(text) > 200:
                # Determine category
                category = self.categorize_url(url)

                doc = {
                    "source": url,
                    "category": category,
                    "title": soup.title.string if soup.title else self.extract_title(soup),
                    "content": text[:15000],  # Keep more content
                    "url": url
                }
                self.scraped_data.append(doc)
                print(f"   [+] {len(text)} chars - {category}")
                time.sleep(0.3)  # Be respectful
                return True

        except Exception as e:
            print(f"   [-] Error: {str(e)[:60]}")

        return False

    def categorize_url(self, url: str) -> str:
        """Categorize URL by content type."""
        url_lower = url.lower()

        if '/courses/csc' in url_lower or 'course' in url_lower:
            return 'courses'
        elif '/faculty' in url_lower or '/people' in url_lower or '/staff' in url_lower:
            return 'faculty'
        elif 'bulletin.sfsu.edu' in url_lower:
            return 'bulletin'
        elif '/undergraduate' in url_lower or '/bs-' in url_lower:
            return 'undergraduate'
        elif '/graduate' in url_lower or '/ms-' in url_lower:
            return 'graduate'
        elif '/research' in url_lower or '/lab' in url_lower:
            return 'research'
        elif '/admission' in url_lower or '/apply' in url_lower:
            return 'admissions'
        elif '/event' in url_lower or '/news' in url_lower:
            return 'news_events'
        else:
            return 'general'

    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from h1 or title tag."""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        title = soup.find('title')
        if title:
            return title.get_text(strip=True)

        return "Unknown"

    def crawl(self):
        """Main crawling function."""
        print("=" * 70)
        print("AGGRESSIVE SFSU WEB CRAWLER")
        print(f"Target: {self.max_pages} pages")
        print("=" * 70)

        # Add seed URLs
        self.to_visit.update(self.seed_urls)

        # Crawl until we hit the limit or run out of URLs
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.pop()
            self.scrape_page(url)

        # Save data
        self.save_data()

        print("\n" + "=" * 70)
        print(f"[SUCCESS] Crawled {len(self.visited_urls)} pages")
        print(f"[SUCCESS] Collected {len(self.scraped_data)} documents")
        print("=" * 70)

        return self.scraped_data

    def save_data(self):
        """Save all scraped data."""
        # Save main file
        with open("data/sfsu_aggressive_crawl.json", 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVE] Saved to data/sfsu_aggressive_crawl.json")

        # Save by category
        categories = {}
        for doc in self.scraped_data:
            cat = doc['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(doc)

        for cat, docs in categories.items():
            filename = f"data/aggressive_{cat}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] {len(docs)} {cat} docs -> {filename}")


def main():
    """Main function."""
    scraper = AggressiveSFSUScraper()
    scraper.crawl()


if __name__ == "__main__":
    main()
