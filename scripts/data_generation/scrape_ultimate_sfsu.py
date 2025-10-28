"""
ULTIMATE SFSU Web Scraper
Scrapes ALL websites related to San Francisco State University
NO LIMITS - Gets everything: CS, International Office, Admissions, Financial Aid, etc.
"""

import requests
from bs4 import BeautifulSoup
from typing import Set, List, Dict
import json
import time
from urllib.parse import urljoin, urlparse
import re
from collections import defaultdict

class UltimateSFSUScraper:
    """Ultimate comprehensive SFSU web crawler - NO LIMITS."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        self.to_visit: Set[str] = set()
        self.max_pages = 3000  # Optimal limit - comprehensive coverage
        self.errors = defaultdict(int)

        # Comprehensive seed URLs - ALL major SFSU domains
        self.seed_urls = [
            # CS Department
            "https://cs.sfsu.edu/",

            # Academic Bulletin
            "https://bulletin.sfsu.edu/",
            "https://bulletin.sfsu.edu/colleges/science-engineering/computer-science/",
            "https://bulletin.sfsu.edu/courses/csc/",

            # International Office
            "https://oip.sfsu.edu/",
            "https://oip.sfsu.edu/employment",
            "https://oip.sfsu.edu/cpt",
            "https://oip.sfsu.edu/opt",
            "https://international.sfsu.edu/",

            # Admissions
            "https://admissions.sfsu.edu/",
            "https://grad.sfsu.edu/",

            # Registrar
            "https://registrar.sfsu.edu/",
            "https://registrar.sfsu.edu/schedule-classes",

            # Financial Aid
            "https://financialaid.sfsu.edu/",

            # Student Services
            "https://studentsuccess.sfsu.edu/",
            "https://housing.sfsu.edu/",
            "https://career.sfsu.edu/",

            # Main SFSU
            "https://www.sfsu.edu/",

            # Libraries
            "https://library.sfsu.edu/",
            "https://libguides.sfsu.edu/",

            # Science & Engineering
            "https://science.sfsu.edu/",

            # Graduate Division
            "https://grad.sfsu.edu/",

            # Undergraduate Studies
            "https://undergrad.sfsu.edu/",
        ]

    def is_valid_sfsu_url(self, url: str) -> bool:
        """Check if URL is a valid SFSU domain."""
        parsed = urlparse(url)

        # Must be SFSU domain or subdomain
        valid_domains = [
            'sfsu.edu',
            '.sfsu.edu',
        ]

        if not any(domain in parsed.netloc for domain in valid_domains):
            return False

        # Skip non-content files
        skip_patterns = [
            r'\.(pdf|jpg|jpeg|png|gif|svg|ico)$',
            r'\.(zip|tar|gz|rar|doc|docx|ppt|pptx|xls|xlsx)$',
            r'\.(mp3|mp4|avi|mov|wmv)$',
            r'/wp-admin', r'/wp-content', r'/wp-includes',
            r'javascript:', r'mailto:', r'tel:',
            r'#$',  # Just hash fragments
        ]

        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all valid SFSU links from page."""
        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            # Skip empty or invalid hrefs
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue

            full_url = urljoin(base_url, href)

            # Remove URL fragments
            full_url = full_url.split('#')[0]

            if self.is_valid_sfsu_url(full_url):
                links.add(full_url)

        return links

    def categorize_url(self, url: str) -> str:
        """Categorize URL by content type."""
        url_lower = url.lower()

        # CS Department
        if 'cs.sfsu.edu' in url_lower:
            if '/course' in url_lower:
                return 'cs_courses'
            elif '/faculty' in url_lower or '/people' in url_lower:
                return 'cs_faculty'
            elif '/graduate' in url_lower or '/grad' in url_lower:
                return 'cs_graduate'
            elif '/undergraduate' in url_lower or '/undergrad' in url_lower:
                return 'cs_undergraduate'
            elif '/research' in url_lower:
                return 'cs_research'
            else:
                return 'cs_general'

        # International Office
        if 'oip.sfsu.edu' in url_lower or 'international.sfsu.edu' in url_lower:
            if '/cpt' in url_lower:
                return 'international_cpt'
            elif '/opt' in url_lower:
                return 'international_opt'
            elif '/employment' in url_lower or '/work' in url_lower:
                return 'international_employment'
            elif '/visa' in url_lower:
                return 'international_visa'
            else:
                return 'international_general'

        # Academic Bulletin
        if 'bulletin.sfsu.edu' in url_lower:
            if '/courses/csc' in url_lower:
                return 'bulletin_cs_courses'
            elif '/courses/' in url_lower:
                return 'bulletin_courses'
            elif '/computer-science' in url_lower:
                return 'bulletin_cs'
            else:
                return 'bulletin_general'

        # Admissions
        if 'admission' in url_lower:
            if 'graduate' in url_lower or 'grad' in url_lower:
                return 'admissions_graduate'
            else:
                return 'admissions_undergraduate'

        # Registrar
        if 'registrar' in url_lower:
            if 'schedule' in url_lower:
                return 'registrar_schedule'
            elif 'calendar' in url_lower:
                return 'registrar_calendar'
            else:
                return 'registrar_general'

        # Financial Aid
        if 'financial' in url_lower or 'scholarship' in url_lower:
            return 'financial_aid'

        # Student Services
        if 'housing' in url_lower:
            return 'student_housing'
        if 'career' in url_lower:
            return 'student_career'
        if 'counseling' in url_lower or 'health' in url_lower:
            return 'student_health'

        # Library
        if 'library' in url_lower or 'libguide' in url_lower:
            return 'library'

        # Graduate Division
        if 'grad.sfsu.edu' in url_lower:
            return 'graduate_division'

        return 'general'

    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]

        # Remove duplicate consecutive lines
        cleaned = []
        prev = None
        for line in lines:
            if line != prev:
                cleaned.append(line)
            prev = line

        return '\n'.join(cleaned)

    def scrape_page(self, url: str) -> bool:
        """Scrape a single page."""
        if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
            return False

        try:
            response = self.session.get(url, timeout=20, allow_redirects=True)
            response.raise_for_status()

            # Skip non-HTML content
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                return False

            self.visited_urls.add(url)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract new links first
            new_links = self.extract_links(soup, url)
            self.to_visit.update(new_links - self.visited_urls)

            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'header',
                           'aside', 'iframe', 'noscript', 'meta', 'link']):
                tag.decompose()

            # Get main content
            main = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', {'id': re.compile('content|main', re.I)}) or
                soup.find('div', {'class': re.compile('content|main|body', re.I)})
            )

            content_area = main if main else soup.body

            if not content_area:
                return False

            # Extract text
            text = content_area.get_text(separator='\n', strip=True)
            text = self.clean_text(text)

            # Only save if substantial content
            if len(text) > 150:
                category = self.categorize_url(url)

                # Extract title
                title = None
                if soup.title:
                    title = soup.title.string
                elif soup.find('h1'):
                    title = soup.find('h1').get_text(strip=True)
                else:
                    title = category.replace('_', ' ').title()

                doc = {
                    "source": url,
                    "category": category,
                    "title": title[:200] if title else "Unknown",
                    "content": text[:20000],  # Keep substantial content
                    "url": url,
                    "domain": urlparse(url).netloc
                }

                self.scraped_data.append(doc)

                # Progress indicator
                print(f"[{len(self.visited_urls)}] {category:30s} | {len(text):6d} chars | {url[:80]}")

                time.sleep(0.05)  # Faster scraping - 4x speed increase
                return True

        except requests.exceptions.RequestException as e:
            self.errors[type(e).__name__] += 1
            if len(self.visited_urls) % 50 == 0:  # Only print occasional errors
                print(f"   [ERROR] {type(e).__name__}: {str(e)[:60]}")
        except Exception as e:
            self.errors['Other'] += 1

        return False

    def crawl(self):
        """Main crawling function."""
        print("=" * 100)
        print("ULTIMATE SFSU WEB CRAWLER - 3000 PAGE TARGET")
        print("Comprehensive coverage of ALL SFSU domains")
        print("Speed: 0.05s delay (4x faster)")
        print("=" * 100)
        print()

        # Add seed URLs
        self.to_visit.update(self.seed_urls)

        # Crawl until we hit the limit or run out of URLs
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.pop()
            self.scrape_page(url)

            # Progress update every 100 pages
            if len(self.visited_urls) % 100 == 0:
                print()
                print(f"Progress: {len(self.visited_urls)} pages scraped, {len(self.scraped_data)} documents collected, {len(self.to_visit)} URLs queued")
                print()

        # Save data
        self.save_data()
        self.print_summary()

        return self.scraped_data

    def save_data(self):
        """Save all scraped data."""
        print("\n" + "=" * 100)
        print("SAVING DATA...")
        print("=" * 100)

        # Save main file
        with open("data/sfsu_ultimate_crawl.json", 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Main file: data/sfsu_ultimate_crawl.json ({len(self.scraped_data)} documents)")

        # Save by category
        categories = defaultdict(list)
        for doc in self.scraped_data:
            categories[doc['category']].append(doc)

        for cat, docs in sorted(categories.items()):
            filename = f"data/ultimate_{cat}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] {len(docs):4d} docs -> {filename}")

        # Save by domain
        domains = defaultdict(list)
        for doc in self.scraped_data:
            domains[doc['domain']].append(doc)

        print("\n[SAVE] By Domain:")
        for domain, docs in sorted(domains.items()):
            filename = f"data/domain_{domain.replace('.', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            print(f"       {len(docs):4d} docs from {domain}")

    def print_summary(self):
        """Print crawl summary."""
        print("\n" + "=" * 100)
        print("CRAWL COMPLETE!")
        print("=" * 100)
        print(f"Total Pages Visited: {len(self.visited_urls)}")
        print(f"Total Documents Saved: {len(self.scraped_data)}")
        print(f"URLs Still Queued: {len(self.to_visit)}")

        if self.errors:
            print(f"\nErrors Encountered:")
            for error_type, count in sorted(self.errors.items()):
                print(f"  {error_type}: {count}")

        # Category breakdown
        categories = defaultdict(int)
        for doc in self.scraped_data:
            categories[doc['category']] += 1

        print(f"\nDocuments by Category:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat:30s}: {count:4d}")

        # Domain breakdown
        domains = defaultdict(int)
        for doc in self.scraped_data:
            domains[doc['domain']] += 1

        print(f"\nDocuments by Domain:")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"  {domain:40s}: {count:4d}")

        print("=" * 100)


def main():
    """Main function."""
    scraper = UltimateSFSUScraper()
    scraper.crawl()


if __name__ == "__main__":
    main()
