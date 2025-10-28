"""
Delete old database data that is no longer needed
Removes documents with 'sfsu_cs_query_system' in the source
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
import sys
# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
load_dotenv()

def delete_old_data():
    """Delete old documents from the database."""

    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("[ERROR] SUPABASE_URL or SUPABASE_KEY not found in environment variables")
        return

    supabase: Client = create_client(supabase_url, supabase_key)

    print("="*80)
    print("DELETE OLD DATABASE DATA")
    print("="*80)

    # First, count how many documents will be deleted
    print("\n[1] Counting old documents...")
    try:
        old_docs = supabase.table("documents").select("id", count="exact").like("source", "%sfsu_cs_query_system%").execute()
        old_count = old_docs.count
        print(f"[OK] Found {old_count} old documents to delete")
    except Exception as e:
        print(f"[ERROR] Failed to count old documents: {e}")
        return

    if old_count == 0:
        print("\n[OK] No old documents found. Database is already clean!")
        return

    # Ask for confirmation
    print(f"\n[WARNING] This will DELETE {old_count} documents from the database.")
    print("[WARNING] This action cannot be undone!")
    confirm = input("\nType 'DELETE' to confirm: ")

    if confirm != "DELETE":
        print("\n[CANCELLED] Deletion cancelled.")
        return

    # Delete in batches to avoid timeout
    print(f"\n[2] Deleting old documents in batches...")
    batch_size = 1000
    total_deleted = 0

    try:
        while True:
            # Get a batch of IDs to delete
            batch = supabase.table("documents").select("id").like("source", "%sfsu_cs_query_system%").limit(batch_size).execute()

            if not batch.data:
                break

            # Extract IDs
            ids_to_delete = [doc['id'] for doc in batch.data]

            # Delete the batch
            supabase.table("documents").delete().in_("id", ids_to_delete).execute()

            total_deleted += len(ids_to_delete)
            print(f"[OK] Deleted batch of {len(ids_to_delete)} documents (Total: {total_deleted}/{old_count})")

            if len(ids_to_delete) < batch_size:
                break

        print(f"\n[SUCCESS] Deleted {total_deleted} old documents!")

    except Exception as e:
        print(f"\n[ERROR] Failed to delete documents: {e}")
        print(f"[INFO] Deleted {total_deleted} documents before error occurred")
        return

    # Verify deletion
    print("\n[3] Verifying deletion...")
    try:
        remaining = supabase.table("documents").select("id", count="exact").like("source", "%sfsu_cs_query_system%").execute()
        remaining_count = remaining.count

        if remaining_count == 0:
            print("[OK] All old documents successfully deleted!")
        else:
            print(f"[WARNING] {remaining_count} old documents still remain")
    except Exception as e:
        print(f"[ERROR] Failed to verify deletion: {e}")

    # Count remaining documents
    print("\n[4] Counting remaining documents...")
    try:
        total_docs = supabase.table("documents").select("id", count="exact").execute()
        print(f"[OK] Total documents remaining: {total_docs.count}")
        print(f"[OK] Database cleaned successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to count remaining documents: {e}")

    print("\n" + "="*80)
    print("CLEANUP COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    delete_old_data()
