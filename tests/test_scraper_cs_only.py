"""
Test Scraper - CS Department Only
Quick test to estimate full scrape size and validate scraper
"""

from scrape_comprehensive_sfsu import ComprehensiveSFSUScraper

if __name__ == "__main__":
    print("=" * 70)
    print("TEST SCRAPER - CS DEPARTMENT ONLY")
    print("=" * 70)
    print("This will scrape ONLY cs.sfsu.edu to estimate full scale")
    print("Expected: 500-1,500 pages from CS department alone")
    print("Duration: ~10-20 minutes")
    print("=" * 70)

    # Initialize scraper with ONLY CS department
    scraper = ComprehensiveSFSUScraper(
        start_urls=["https://cs.sfsu.edu/"],
        max_depth=4  # 4 levels deep
    )

    # Override allowed domains to ONLY cs.sfsu.edu
    scraper.allowed_domains = ['cs.sfsu.edu']

    # Override output file
    scraper.output_file = "data/test_cs_only_crawl.json"
    scraper.progress_file = "data/test_cs_only_progress.json"

    # Run the scraper
    scraped_data = scraper.run()

    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)
    print(f"CS Department Pages: {len(scraped_data)}")
    print(f"\nEstimated FULL scrape (8 domains):")
    print(f"  Conservative: {len(scraped_data) * 8:,} pages")
    print(f"  Realistic: {len(scraped_data) * 12:,} pages")
    print(f"  If bulletin.sfsu.edu is large: {len(scraped_data) * 20:,}+ pages")
    print("=" * 70)
