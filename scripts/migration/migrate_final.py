"""
Final Migration Script - Upload ALL scraped SFSU data to Supabase
Works with your existing database schema (no 'category' column)
"""

import os
import json
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from typing import List, Dict
import glob

# Load environment
load_dotenv()

class FinalMigration:
    """Final comprehensive migration."""

    def __init__(self):
        """Initialize services."""
        print("[*] Initializing final migration...")

        # Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

        self.supabase = create_client(supabase_url, supabase_key)

        # Embedding model
        print("[*] Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[OK] Model loaded (384 dimensions)")

        # Test connection
        self.test_connection()

    def test_connection(self):
        """Test Supabase connection."""
        try:
            result = self.supabase.table("documents").select("id", count="exact").limit(1).execute()
            print(f"[OK] Connected to Supabase! Current documents: {result.count}")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            raise

    def migrate_ultimate_data(self):
        """Migrate the ultimate scraped data."""
        total_docs = 0

        # Find the ultimate crawl data
        ultimate_file = "data/sfsu_ultimate_crawl.json"

        if not os.path.exists(ultimate_file):
            print(f"[SKIP] {ultimate_file} not found - waiting for scraper to finish")
            return 0

        with open(ultimate_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n[*] Found {len(data)} documents from ultimate crawl")

        count = 0
        errors = 0

        for i, doc in enumerate(data):
            try:
                # Create comprehensive content with metadata
                content_with_meta = f"""Title: {doc.get('title', 'Unknown')}
Category: {doc.get('category', 'general')}
Source: {doc.get('url', doc.get('source', 'Unknown'))}

{doc['content']}"""

                # Generate embedding
                embedding = self.model.encode(content_with_meta).tolist()

                # Insert to database (without 'category' column)
                self.supabase.table("documents").insert({
                    "content": content_with_meta,
                    "source": doc.get('url', doc.get('source', 'Unknown')),
                    "title": doc.get('title', '')[:200],  # Limit title length
                    "embedding": embedding
                }).execute()

                count += 1

                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"   [+] Migrated {count}/{len(data)} documents...")

            except Exception as e:
                errors += 1
                if errors < 10:  # Only show first 10 errors
                    print(f"   [-] Error on doc {i+1}: {str(e)[:80]}")

        print(f"[OK] Migrated {count} ultimate crawl documents ({errors} errors)")
        return count

    def migrate_aggressive_data(self):
        """Migrate the aggressive crawl data."""
        aggressive_file = "data/sfsu_aggressive_crawl.json"

        if not os.path.exists(aggressive_file):
            print(f"[SKIP] {aggressive_file} not found")
            return 0

        with open(aggressive_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\n[*] Found {len(data)} documents from aggressive crawl")

        count = 0
        errors = 0

        for i, doc in enumerate(data):
            try:
                content_with_meta = f"""Title: {doc.get('title', 'Unknown')}
Category: {doc.get('category', 'general')}
Source: {doc.get('url', doc.get('source', 'Unknown'))}

{doc['content']}"""

                embedding = self.model.encode(content_with_meta).tolist()

                self.supabase.table("documents").insert({
                    "content": content_with_meta,
                    "source": doc.get('url', doc.get('source', 'Unknown')),
                    "title": doc.get('title', '')[:200],
                    "embedding": embedding
                }).execute()

                count += 1

                if (i + 1) % 20 == 0:
                    print(f"   [+] Migrated {count}/{len(data)} documents...")

            except Exception as e:
                errors += 1
                if errors < 5:
                    print(f"   [-] Error: {str(e)[:60]}")

        print(f"[OK] Migrated {count} aggressive crawl documents ({errors} errors)")
        return count

    def migrate_all(self):
        """Migrate all available data."""
        total_docs = 0

        print("\n" + "=" * 70)
        print("[1] Migrating ULTIMATE SFSU crawl data...")
        print("=" * 70)
        ultimate_count = self.migrate_ultimate_data()
        total_docs += ultimate_count

        print("\n" + "=" * 70)
        print("[2] Migrating AGGRESSIVE crawl data...")
        print("=" * 70)
        aggressive_count = self.migrate_aggressive_data()
        total_docs += aggressive_count

        # Summary
        print("\n" + "=" * 70)
        print("[SUCCESS] Migration Complete!")
        print(f"   Total documents migrated: {total_docs}")
        print(f"   - Ultimate crawl: {ultimate_count}")
        print(f"   - Aggressive crawl: {aggressive_count}")
        print("=" * 70)

        return total_docs


def main():
    """Main migration function."""
    print("=" * 70)
    print("FINAL SFSU DATA MIGRATION - ALL SCRAPED DATA")
    print("=" * 70)

    migration = FinalMigration()
    migration.migrate_all()


if __name__ == "__main__":
    main()
