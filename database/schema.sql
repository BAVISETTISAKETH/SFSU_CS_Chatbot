-- SFSU CS Chatbot Database Schema
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- DOCUMENTS TABLE (Main knowledge base)
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384),  -- MiniLM-L6-v2 produces 384-dimensional vectors
    metadata JSONB DEFAULT '{}'::jsonb,
    source VARCHAR(255),
    url TEXT,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster vector similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for text search
CREATE INDEX IF NOT EXISTS documents_content_idx ON documents
USING gin(to_tsvector('english', content));

-- Index for source filtering
CREATE INDEX IF NOT EXISTS documents_source_idx ON documents(source);

-- ============================================================================
-- VERIFIED FACTS TABLE (High-priority, professor-approved knowledge)
-- ============================================================================
CREATE TABLE IF NOT EXISTS verified_facts (
    id BIGSERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding vector(384),
    category VARCHAR(100),  -- e.g., 'courses', 'faculty', 'admissions'
    verified_by VARCHAR(255),  -- professor email
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for vector search on verified facts
CREATE INDEX IF NOT EXISTS verified_facts_embedding_idx ON verified_facts
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- ============================================================================
-- CORRECTIONS TABLE (Student feedback + Professor review workflow)
-- ============================================================================
CREATE TABLE IF NOT EXISTS corrections (
    id BIGSERIAL PRIMARY KEY,
    student_query TEXT NOT NULL,
    rag_response TEXT NOT NULL,
    professor_correction TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'corrected', 'rejected')),
    category VARCHAR(100),
    priority INTEGER DEFAULT 0,  -- Higher = more important
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by VARCHAR(255),  -- professor email
    notes TEXT
);

-- Index for filtering by status
CREATE INDEX IF NOT EXISTS corrections_status_idx ON corrections(status);
CREATE INDEX IF NOT EXISTS corrections_created_at_idx ON corrections(created_at DESC);

-- ============================================================================
-- PROFESSORS TABLE (Authentication)
-- ============================================================================
CREATE TABLE IF NOT EXISTS professors (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(100) DEFAULT 'Computer Science',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Index for login lookups
CREATE INDEX IF NOT EXISTS professors_email_idx ON professors(email);

-- ============================================================================
-- CHAT LOGS TABLE (Analytics & Monitoring)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    user_type VARCHAR(20) DEFAULT 'student' CHECK (user_type IN ('student', 'professor')),
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    response_time_ms INTEGER,
    source VARCHAR(50),  -- 'rag', 'web', 'verified_fact'
    confidence_score FLOAT,
    model_used VARCHAR(100) DEFAULT 'groq-llama-3.3-70b',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS chat_logs_created_at_idx ON chat_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS chat_logs_source_idx ON chat_logs(source);
CREATE INDEX IF NOT EXISTS chat_logs_session_idx ON chat_logs(session_id);

-- ============================================================================
-- WEB SEARCH CACHE TABLE (Cache web search results to save API calls)
-- ============================================================================
CREATE TABLE IF NOT EXISTS web_search_cache (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

-- Index for query lookup
CREATE INDEX IF NOT EXISTS web_search_cache_query_idx ON web_search_cache(query);
CREATE INDEX IF NOT EXISTS web_search_cache_expires_idx ON web_search_cache(expires_at);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_verified_facts_updated_at ON verified_facts;
CREATE TRIGGER update_verified_facts_updated_at
    BEFORE UPDATE ON verified_facts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function for similarity search on documents
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    source varchar(255),
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        documents.source,
        1 - (documents.embedding <=> query_embedding) as similarity
    FROM documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Function for similarity search on verified facts
CREATE OR REPLACE FUNCTION match_verified_facts(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 3
)
RETURNS TABLE (
    id bigint,
    question text,
    answer text,
    category varchar(100),
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        verified_facts.id,
        verified_facts.question,
        verified_facts.answer,
        verified_facts.category,
        1 - (verified_facts.embedding <=> query_embedding) as similarity
    FROM verified_facts
    WHERE 1 - (verified_facts.embedding <=> query_embedding) > match_threshold
    ORDER BY verified_facts.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ============================================================================
-- DEFAULT DATA: Create default professor account
-- ============================================================================
-- Password: admin123 (hashed with bcrypt)
-- IMPORTANT: Change this password after first login!
INSERT INTO professors (email, password_hash, name, department)
VALUES (
    'admin@sfsu.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIx8FZB5G2',  -- admin123
    'Admin Professor',
    'Computer Science'
) ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Daily chat statistics
CREATE OR REPLACE VIEW daily_chat_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_queries,
    AVG(response_time_ms) as avg_response_time,
    COUNT(DISTINCT session_id) as unique_sessions,
    COUNT(CASE WHEN source = 'rag' THEN 1 END) as rag_queries,
    COUNT(CASE WHEN source = 'web' THEN 1 END) as web_queries,
    COUNT(CASE WHEN source = 'verified_fact' THEN 1 END) as verified_fact_queries
FROM chat_logs
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Pending corrections summary
CREATE OR REPLACE VIEW corrections_summary AS
SELECT
    status,
    COUNT(*) as count,
    MAX(created_at) as latest_correction
FROM corrections
GROUP BY status;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Optional but recommended
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE professors ENABLE ROW LEVEL SECURITY;
ALTER TABLE corrections ENABLE ROW LEVEL SECURITY;

-- Professors can see all corrections
CREATE POLICY professors_can_view_corrections ON corrections
    FOR SELECT
    USING (true);

-- Professors can update corrections
CREATE POLICY professors_can_update_corrections ON corrections
    FOR UPDATE
    USING (true);

-- ============================================================================
-- CLEANUP FUNCTION (Remove expired cache entries)
-- ============================================================================

CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM web_search_cache WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANT PERMISSIONS (if using service role)
-- ============================================================================

GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres, anon, authenticated, service_role;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Database schema created successfully!';
    RAISE NOTICE '📊 Tables created: documents, verified_facts, corrections, professors, chat_logs, web_search_cache';
    RAISE NOTICE '🔐 Default professor account: admin@sfsu.edu / admin123 (CHANGE THIS PASSWORD!)';
END $$;
