"""
Complete Migration Script for SFSU CS Chatbot (Alli)
Migrates all data sources to Supabase with vector embeddings
"""

import os
import json
import glob
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from typing import List, Dict

# Load environment
load_dotenv()

class CompleteMigration:
    """Complete migration to Supabase."""

    def __init__(self):
        """Initialize services."""
        print("[*] Initializing migration...")

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

    def migrate_all(self):
        """Migrate all data sources."""
        total_docs = 0

        # 1. Migrate scraped web data
        print("\n" + "=" * 60)
        print("[1] Migrating SFSU CS scraped web data...")
        print("=" * 60)
        web_count = self.migrate_scraped_data()
        total_docs += web_count

        # 2. Migrate course data
        print("\n" + "=" * 60)
        print("[2] Migrating CS courses...")
        print("=" * 60)
        course_count = self.migrate_courses()
        total_docs += course_count

        # 3. Migrate any existing JSON files from data folder
        print("\n" + "=" * 60)
        print("[3] Migrating existing JSON data files...")
        print("=" * 60)
        json_count = self.migrate_json_files()
        total_docs += json_count

        # Summary
        print("\n" + "=" * 60)
        print("[SUCCESS] Migration Complete!")
        print(f"   Total documents migrated: {total_docs}")
        print(f"   - Web scraped: {web_count}")
        print(f"   - Courses: {course_count}")
        print(f"   - JSON files: {json_count}")
        print("=" * 60)

        return total_docs

    def migrate_scraped_data(self):
        """Migrate scraped SFSU data."""
        filename = "data/sfsu_cs_scraped.json"

        if not os.path.exists(filename):
            print(f"[SKIP] {filename} not found")
            return 0

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"[*] Found {len(data)} scraped documents")

        count = 0
        for doc in data:
            try:
                # Generate embedding
                embedding = self.model.encode(doc['content']).tolist()

                # Insert to database
                self.supabase.table("documents").insert({
                    "content": doc['content'],
                    "source": doc.get('url', doc['source']),
                    "category": doc.get('category', 'web'),
                    "title": doc.get('title', ''),
                    "embedding": embedding
                }).execute()

                count += 1
                if count % 5 == 0:
                    print(f"   [+] Migrated {count}/{len(data)}...")

            except Exception as e:
                print(f"   [-] Error: {e}")

        print(f"[OK] Migrated {count} web documents")
        return count

    def migrate_courses(self):
        """Migrate course data."""
        filename = "data/sfsu_cs_courses.json"

        if not os.path.exists(filename):
            print(f"[SKIP] {filename} not found")
            return 0

        with open(filename, 'r', encoding='utf-8') as f:
            courses = json.load(f)

        print(f"[*] Found {len(courses)} courses")

        count = 0
        for course in courses:
            try:
                # Create comprehensive course description
                content = f"""Course: {course['code']} - {course['title']}

Description: {course['description']}

Units: {course['units']}

Course Code: {course['code']}
"""

                # Generate embedding
                embedding = self.model.encode(content).tolist()

                # Insert to database
                self.supabase.table("documents").insert({
                    "content": content,
                    "source": f"Course Catalog - {course['code']}",
                    "category": "course",
                    "title": f"{course['code']} - {course['title']}",
                    "embedding": embedding
                }).execute()

                count += 1
                print(f"   [+] Migrated: {course['code']}")

            except Exception as e:
                print(f"   [-] Error migrating {course['code']}: {e}")

        print(f"[OK] Migrated {count} courses")
        return count

    def migrate_json_files(self):
        """Migrate any other JSON files in data folder."""
        pattern = "data/*.json"
        json_files = glob.glob(pattern)

        # Exclude files we've already processed
        exclude = ['sfsu_cs_scraped.json', 'sfsu_cs_courses.json']
        json_files = [f for f in json_files if os.path.basename(f) not in exclude]

        if not json_files:
            print("[SKIP] No additional JSON files found")
            return 0

        total_count = 0

        for filepath in json_files:
            print(f"\n[*] Processing: {filepath}")

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, list):
                    count = self._migrate_json_list(data, filepath)
                elif isinstance(data, dict):
                    count = self._migrate_json_dict(data, filepath)
                else:
                    print(f"   [SKIP] Unsupported format")
                    continue

                total_count += count
                print(f"   [OK] Migrated {count} items from {os.path.basename(filepath)}")

            except Exception as e:
                print(f"   [-] Error processing {filepath}: {e}")

        return total_count

    def _migrate_json_list(self, data: List, filepath: str):
        """Migrate JSON list data."""
        count = 0

        for item in data:
            try:
                # Try to extract content intelligently
                content = item.get('content') or item.get('text') or item.get('description') or str(item)
                source = item.get('source') or filepath
                category = item.get('category') or 'general'
                title = item.get('title') or item.get('name') or ''

                if len(content) < 50:  # Skip very short entries
                    continue

                # Generate embedding
                embedding = self.model.encode(content).tolist()

                # Insert
                self.supabase.table("documents").insert({
                    "content": content,
                    "source": source,
                    "category": category,
                    "title": title,
                    "embedding": embedding
                }).execute()

                count += 1

            except Exception as e:
                print(f"   [-] Error on item: {e}")

        return count

    def _migrate_json_dict(self, data: Dict, filepath: str):
        """Migrate JSON dict data."""
        # Convert dict to single document
        try:
            content = json.dumps(data, indent=2)

            if len(content) < 50:
                return 0

            embedding = self.model.encode(content).tolist()

            self.supabase.table("documents").insert({
                "content": content,
                "source": filepath,
                "category": "general",
                "title": os.path.basename(filepath),
                "embedding": embedding
            }).execute()

            return 1

        except Exception as e:
            print(f"   [-] Error: {e}")
            return 0


def main():
    """Main migration function."""
    print("=" * 60)
    print("SFSU CS Chatbot (Alli) - Complete Data Migration")
    print("=" * 60)

    migration = CompleteMigration()
    migration.migrate_all()


if __name__ == "__main__":
    main()
