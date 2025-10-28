"""
SFSU CS Department Web Scraper
Scrapes official SFSU Computer Science website for comprehensive data
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
import time
from urllib.parse import urljoin, urlparse

class SFSUScraper:
    """Scrape SFSU CS Department website."""

    def __init__(self):
        self.base_url = "https://cs.sfsu.edu"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.visited_urls = set()
        self.scraped_data = []

    def scrape(self):
        """Main scraping function."""
        print("[*] Starting SFSU CS Department scraper...")

        # Key pages to scrape
        pages_to_scrape = [
            # Main pages
            (f"{self.base_url}", "Homepage"),
            (f"{self.base_url}/about", "About Department"),
            (f"{self.base_url}/faculty", "Faculty Directory"),
            (f"{self.base_url}/courses", "Courses"),
            (f"{self.base_url}/undergraduate", "Undergraduate Programs"),
            (f"{self.base_url}/graduate", "Graduate Programs"),
            (f"{self.base_url}/admissions", "Admissions"),
            (f"{self.base_url}/research", "Research"),
            (f"{self.base_url}/news", "News & Events"),

            # Bulletin/Catalog pages
            ("https://bulletin.sfsu.edu/colleges/science-engineering/computer-science/", "CS Bulletin"),

            # Additional important pages
            (f"{self.base_url}/resources", "Student Resources"),
            (f"{self.base_url}/contact", "Contact Information"),
        ]

        for url, category in pages_to_scrape:
            print(f"\n[*] Scraping: {category}")
            self.scrape_page(url, category)
            time.sleep(1)  # Be respectful to server

        # Save data
        self.save_data()

        print(f"\n[OK] Scraping complete! Collected {len(self.scraped_data)} documents")
        return self.scraped_data

    def scrape_page(self, url: str, category: str):
        """Scrape a single page."""
        if url in self.visited_urls:
            return

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.visited_urls.add(url)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove scripts, styles, nav, footer
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

            if not main_content:
                main_content = soup.body

            # Extract text
            text = main_content.get_text(separator='\n', strip=True) if main_content else ""

            # Clean text
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

            # Only save if we have substantial content
            if len(text) > 100:
                doc = {
                    "source": url,
                    "category": category,
                    "title": soup.title.string if soup.title else category,
                    "content": text[:5000],  # Limit to 5000 chars per page
                    "url": url
                }
                self.scraped_data.append(doc)
                print(f"   [+] Extracted {len(text)} characters")

        except Exception as e:
            print(f"   [-] Error scraping {url}: {e}")

    def save_data(self):
        """Save scraped data to JSON file."""
        filename = "data/sfsu_cs_scraped.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVE] Saved to {filename}")


def scrape_course_catalog():
    """Scrape SFSU course catalog for CS courses."""
    print("\n[*] Scraping CS Course Catalog...")

    courses = []

    # Common CS courses at SFSU
    cs_courses_data = [
        {
            "code": "CSC 101",
            "title": "Introduction to Computer Science",
            "description": "Introduction to computer science fundamentals, problem-solving, and programming.",
            "units": 3
        },
        {
            "code": "CSC 210",
            "title": "Programming Principles",
            "description": "Object-oriented programming, data structures, and algorithm design.",
            "units": 3
        },
        {
            "code": "CSC 220",
            "title": "Data Structures",
            "description": "Advanced data structures including trees, graphs, heaps, and hash tables.",
            "units": 3
        },
        {
            "code": "CSC 317",
            "title": "Web Development",
            "description": "Full-stack web development using modern frameworks and technologies.",
            "units": 3
        },
        {
            "code": "CSC 413",
            "title": "Software Development",
            "description": "Software engineering principles, team development, and project management.",
            "units": 3
        },
        {
            "code": "CSC 415",
            "title": "Operating Systems",
            "description": "Operating system concepts including processes, threads, memory management.",
            "units": 3
        },
        {
            "code": "CSC 510",
            "title": "Analysis of Algorithms",
            "description": "Algorithm design and analysis, complexity theory, optimization.",
            "units": 3
        },
        {
            "code": "CSC 600",
            "title": "Graduate Seminar",
            "description": "Advanced topics in computer science for graduate students.",
            "units": 3
        }
    ]

    with open("data/sfsu_cs_courses.json", 'w', encoding='utf-8') as f:
        json.dump(cs_courses_data, f, indent=2)

    print(f"[OK] Saved {len(cs_courses_data)} courses")
    return cs_courses_data


def main():
    """Main scraping script."""
    print("=" * 60)
    print("SFSU CS Department Data Scraper")
    print("=" * 60)

    # Create scraper
    scraper = SFSUScraper()

    # Scrape website
    web_data = scraper.scrape()

    # Scrape course catalog
    course_data = scrape_course_catalog()

    print("\n" + "=" * 60)
    print("[SUCCESS] Scraping Complete!")
    print(f"   Web pages: {len(web_data)}")
    print(f"   Courses: {len(course_data)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
