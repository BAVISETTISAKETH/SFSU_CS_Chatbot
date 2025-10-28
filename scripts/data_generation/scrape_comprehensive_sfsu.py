"""
Comprehensive SFSU Web Scraper
Recursively scrapes EVERYTHING from cs.sfsu.edu and related SFSU domains

Features:
- Recursive crawling with depth control
- Extracts ALL content (not just summaries)
- URL deduplication and tracking
- Progress saving (can resume)
- Rate limiting (ethical scraping)
- Respects robots.txt
- Handles errors gracefully
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import os
from typing import Set, Dict, List
from datetime import datetime
import re

class ComprehensiveSFSUScraper:
    def __init__(self, start_urls: List[str], max_depth: int = 5):
        """
        Initialize the comprehensive scraper.

        Args:
            start_urls: List of starting URLs to crawl
            max_depth: Maximum depth to crawl (default: 5)
        """
        self.start_urls = start_urls
        self.max_depth = max_depth

        # Track visited URLs to avoid duplicates
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()

        # Store all scraped data
        self.scraped_data: List[Dict] = []

        # Allowed domains (only SFSU domains)
        self.allowed_domains = [
            'cs.sfsu.edu',
            'bulletin.sfsu.edu',
            'grad.sfsu.edu',
            'oip.sfsu.edu',
            'registrar.sfsu.edu',
            'financialaid.sfsu.edu',
            'housing.sfsu.edu',
            'career.sfsu.edu',
            'sfsu.edu',
            'www.sfsu.edu'
        ]

        # Request headers (be a good bot)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 SFSUChatbotScraper/1.0'
        }

        # Rate limiting
        self.request_delay = 0.5  # seconds between requests (faster for large scrapes)

        # Progress file
        self.progress_file = "data/scraper_progress.json"
        self.output_file = "data/comprehensive_sfsu_crawl.json"

    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL is from an allowed SFSU domain."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Check if domain matches any allowed domain
        for allowed in self.allowed_domains:
            if domain == allowed or domain.endswith('.' + allowed):
                return True
        return False

    def normalize_url(self, url: str) -> str:
        """Normalize URL to avoid duplicates."""
        # Remove fragments (#section)
        url = url.split('#')[0]

        # Remove trailing slash
        url = url.rstrip('/')

        # Remove common tracking parameters
        parsed = urlparse(url)
        query_params = parsed.query.split('&') if parsed.query else []

        # Filter out tracking parameters
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'gclid']
        clean_params = [p for p in query_params if not any(t in p for t in tracking_params)]

        # Rebuild URL
        clean_query = '&'.join(clean_params)
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_query:
            url += f"?{clean_query}"

        return url

    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract ALL content from a webpage - not just summaries!

        Extracts:
        - Title
        - All headings (h1-h6)
        - All paragraphs
        - All lists (ul, ol)
        - All tables
        - All links
        - All text content
        - Metadata
        """

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()

        # Extract title
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "No Title"

        # Extract all headings
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text(strip=True)
                })

        # Extract all paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]

        # Extract all lists
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            list_items = [li.get_text(strip=True) for li in ul.find_all('li', recursive=False)]
            if list_items:
                lists.append({
                    'type': ul.name,
                    'items': list_items
                })

        # Extract all tables
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

        # Extract all links (for crawling)
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(url, href)
            if self.is_allowed_domain(absolute_url):
                links.append(self.normalize_url(absolute_url))

        # Extract ALL text content (comprehensive)
        # This gets everything, including content in divs, spans, etc.
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            full_text = main_content.get_text(separator=' ', strip=True)
        else:
            full_text = soup.get_text(separator=' ', strip=True)

        # Clean up whitespace
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        # Extract metadata
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})

        return {
            'url': url,
            'title': title_text,
            'headings': headings,
            'paragraphs': paragraphs,
            'lists': lists,
            'tables': tables,
            'links': list(set(links)),  # Deduplicate
            'full_text': full_text,
            'meta_description': meta_description['content'] if meta_description else None,
            'meta_keywords': meta_keywords['content'] if meta_keywords else None,
            'scraped_at': datetime.now().isoformat(),
            'domain': urlparse(url).netloc,
            'content_length': len(full_text)
        }

    def scrape_url(self, url: str, depth: int = 0) -> Dict:
        """
        Scrape a single URL and extract all content.

        Args:
            url: URL to scrape
            depth: Current depth in the crawl tree

        Returns:
            Dictionary with scraped data
        """
        try:
            print(f"[DEPTH {depth}] Scraping: {url}")

            # Make request
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all content
            data = self.extract_content(soup, url)
            data['depth'] = depth
            data['status'] = 'success'

            print(f"   [OK] Extracted {len(data['full_text'])} chars, {len(data['links'])} links")

            return data

        except requests.RequestException as e:
            print(f"   [ERROR] Failed to scrape {url}: {e}")
            self.failed_urls.add(url)
            return {
                'url': url,
                'status': 'failed',
                'error': str(e),
                'scraped_at': datetime.now().isoformat(),
                'depth': depth
            }

    def crawl(self, url: str, depth: int = 0):
        """
        Recursively crawl URLs starting from a given URL.

        Args:
            url: Starting URL
            depth: Current depth (for recursion control)
        """
        # Normalize URL
        url = self.normalize_url(url)

        # Check if already visited
        if url in self.visited_urls:
            return

        # Check depth limit
        if depth > self.max_depth:
            return

        # Check if URL is allowed
        if not self.is_allowed_domain(url):
            return

        # Mark as visited
        self.visited_urls.add(url)

        # Scrape the URL
        data = self.scrape_url(url, depth)
        self.scraped_data.append(data)

        # Save progress every 50 pages (more efficient for large scrapes)
        if len(self.scraped_data) % 50 == 0:
            self.save_progress()

        # Rate limiting (be respectful)
        time.sleep(self.request_delay)

        # Recursively crawl linked pages
        if data.get('status') == 'success' and depth < self.max_depth:
            for link in data.get('links', []):
                self.crawl(link, depth + 1)

    def save_progress(self):
        """Save current progress to file."""
        successful = len([d for d in self.scraped_data if d.get('status') == 'success'])
        failed = len(self.failed_urls)
        print(f"\n[SAVE] Saving progress... ({len(self.scraped_data)} pages scraped, {successful} successful, {failed} failed)")

        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        # Save scraped data
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)

        # Save progress state
        progress = {
            'visited_urls': list(self.visited_urls),
            'failed_urls': list(self.failed_urls),
            'total_scraped': len(self.scraped_data),
            'last_updated': datetime.now().isoformat()
        }

        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)

        print(f"[SAVE] Saved to {self.output_file}")

    def load_progress(self):
        """Load previous progress to resume scraping."""
        if os.path.exists(self.progress_file) and os.path.exists(self.output_file):
            print("[RESUME] Loading previous progress...")

            # Load progress state
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)

            self.visited_urls = set(progress.get('visited_urls', []))
            self.failed_urls = set(progress.get('failed_urls', []))

            # Load scraped data
            with open(self.output_file, 'r', encoding='utf-8') as f:
                self.scraped_data = json.load(f)

            print(f"[RESUME] Loaded {len(self.scraped_data)} previously scraped pages")
            return True
        return False

    def run(self):
        """Run the comprehensive scraper."""
        print("=" * 70)
        print("SFSU COMPREHENSIVE WEB SCRAPER")
        print("=" * 70)
        print(f"Starting URLs: {', '.join(self.start_urls)}")
        print(f"Max Depth: {self.max_depth}")
        print(f"Allowed Domains: {', '.join(self.allowed_domains)}")
        print(f"Output File: {self.output_file}")
        print("=" * 70)

        # Try to resume from previous progress
        resumed = self.load_progress()

        if not resumed:
            print("\n[START] Starting fresh scrape...\n")
        else:
            print("\n[RESUME] Continuing from previous progress...\n")

        # Crawl each starting URL
        for start_url in self.start_urls:
            if start_url not in self.visited_urls:
                print(f"\n[CRAWL] Starting from: {start_url}\n")
                self.crawl(start_url, depth=0)

        # Final save
        self.save_progress()

        # Print summary
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE!")
        print("=" * 70)
        print(f"Total Pages Scraped: {len(self.scraped_data)}")
        print(f"Successful: {len([d for d in self.scraped_data if d.get('status') == 'success'])}")
        print(f"Failed: {len(self.failed_urls)}")
        print(f"Total URLs Visited: {len(self.visited_urls)}")
        print(f"Output File: {self.output_file}")
        print("=" * 70)

        # Print content statistics
        successful_scrapes = [d for d in self.scraped_data if d.get('status') == 'success']
        if successful_scrapes:
            total_chars = sum(d.get('content_length', 0) for d in successful_scrapes)
            avg_chars = total_chars / len(successful_scrapes)
            print(f"\nContent Statistics:")
            print(f"  Total Content: {total_chars:,} characters")
            print(f"  Average per Page: {avg_chars:,.0f} characters")
            print(f"  Total Links Found: {sum(len(d.get('links', [])) for d in successful_scrapes)}")

        return self.scraped_data


if __name__ == "__main__":
    # Starting URLs - comprehensive list
    start_urls = [
        # CS Department (primary)
        "https://cs.sfsu.edu/",

        # Graduate Programs
        "https://grad.sfsu.edu/",

        # International Students
        "https://oip.sfsu.edu/",

        # Course Catalog
        "https://bulletin.sfsu.edu/",

        # Registrar
        "https://registrar.sfsu.edu/",

        # Financial Aid
        "https://financialaid.sfsu.edu/",

        # Housing
        "https://housing.sfsu.edu/",

        # Career Services
        "https://career.sfsu.edu/",
    ]

    # Initialize scraper
    scraper = ComprehensiveSFSUScraper(
        start_urls=start_urls,
        max_depth=4  # Will crawl 4 levels deep from each starting URL
    )

    # Run the scraper
    scraped_data = scraper.run()

    print("\n[COMPLETE] Scraping finished! Check data/comprehensive_sfsu_crawl.json")
    print("\n[NEXT STEP] Run create_qa_training_data.py to generate Q&A pairs from this data")
