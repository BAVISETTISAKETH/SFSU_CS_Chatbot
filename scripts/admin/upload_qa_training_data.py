"""
Upload Q&A Training Data to Supabase
Converts Q&A pairs into a separate high-quality training table
"""

import json
import os
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Initialize
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("[AI] Uploading Q&A Training Data to Supabase")
print("=" * 60)

# Load Q&A data
qa_file = "data/qa_training_data.json"

if not os.path.exists(qa_file):
    print(f"[ERROR] File not found: {qa_file}")
    print("[INFO] Run create_qa_training_data.py first!")
    exit(1)

with open(qa_file, 'r', encoding='utf-8') as f:
    qa_pairs = json.load(f)

print(f"[DATA] Loaded {len(qa_pairs)} Q&A pairs")
print(f"\nSample:")
print(f"Q: {qa_pairs[0]['question']}")
print(f"A: {qa_pairs[0]['answer'][:100]}...\n")

# First, create the table if it doesn't exist
print("[TABLE] Creating qa_training table...")

create_table_sql = """
CREATE TABLE IF NOT EXISTS qa_training (
    id BIGSERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category TEXT,
    source_url TEXT,
    question_embedding VECTOR(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector search
CREATE INDEX IF NOT EXISTS idx_qa_training_embedding
ON qa_training USING ivfflat (question_embedding vector_cosine_ops)
WITH (lists = 100);

-- Create text search index
CREATE INDEX IF NOT EXISTS idx_qa_training_question
ON qa_training USING gin(to_tsvector('english', question));
"""

print("[WARNING] Note: Run this SQL in Supabase Dashboard > SQL Editor:")
print("-" * 60)
print(create_table_sql)
print("-" * 60)

input("\nPress Enter after you've created the table in Supabase...")

# Upload Q&A pairs
print("\n[UPLOAD] Uploading Q&A pairs...")

batch_size = 50
success_count = 0
error_count = 0

for i in range(0, len(qa_pairs), batch_size):
    batch = qa_pairs[i:i+batch_size]

    print(f"\n[{i+1}-{min(i+batch_size, len(qa_pairs))}/{len(qa_pairs)}] Processing batch...")

    try:
        # Prepare data with embeddings
        records = []
        for qa in batch:
            # Generate embedding for the question
            embedding = embedding_model.encode(qa['question']).tolist()

            records.append({
                "question": qa['question'],
                "answer": qa['answer'],
                "category": qa.get('category', 'general'),
                "source_url": qa.get('source_url', ''),
                "question_embedding": embedding
            })

        # Insert batch
        result = supabase.table("qa_training").insert(records).execute()

        success_count += len(batch)
        print(f"   [OK] Uploaded {len(batch)} Q&A pairs")

    except Exception as e:
        error_count += len(batch)
        print(f"   [ERROR] Error: {e}")

print(f"\n{'='*60}")
print(f"[COMPLETE] Upload Complete!")
print(f"   Success: {success_count} Q&A pairs")
print(f"   Errors:  {error_count} Q&A pairs")
print(f"{'='*60}")

# Create a function to search Q&A pairs
search_function_sql = """
CREATE OR REPLACE FUNCTION match_qa_training(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    question TEXT,
    answer TEXT,
    category TEXT,
    source_url TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        qa_training.id,
        qa_training.question,
        qa_training.answer,
        qa_training.category,
        qa_training.source_url,
        1 - (qa_training.question_embedding <=> query_embedding) AS similarity
    FROM qa_training
    WHERE 1 - (qa_training.question_embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
"""

print("\n[NEXT] NEXT STEP: Create the search function in Supabase:")
print("-" * 60)
print(search_function_sql)
print("-" * 60)

print("\n[SUCCESS] All done! Your chatbot now has high-quality Q&A training data!")
print("[INFO] This will make responses much more accurate and ChatGPT-like!")
