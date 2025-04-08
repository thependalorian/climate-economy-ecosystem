-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector embeddings table for semantic search
CREATE TABLE IF NOT EXISTS climate_memories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    source_type TEXT NOT NULL,
    url TEXT,
    title TEXT,
    chunk_index INTEGER,
    total_chunks INTEGER,
    crawl_time TIMESTAMP WITH TIME ZONE,
    company TEXT,
    sector TEXT,
    domain TEXT,
    path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_persona ON profiles(persona);
CREATE INDEX IF NOT EXISTS idx_profiles_location ON profiles(location);
CREATE INDEX IF NOT EXISTS idx_profiles_skills ON profiles USING GIN(skills);
CREATE INDEX IF NOT EXISTS idx_profiles_interests ON profiles USING GIN(interests);

CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_requirements ON jobs USING GIN(requirements);

CREATE INDEX IF NOT EXISTS idx_training_programs_provider ON training_programs(provider);
CREATE INDEX IF NOT EXISTS idx_training_programs_skills ON training_programs USING GIN(skills_covered);

-- Create vector search indexes
CREATE INDEX IF NOT EXISTS idx_climate_memories_embedding ON climate_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_climate_memories_source_type ON climate_memories(source_type);
CREATE INDEX IF NOT EXISTS idx_climate_memories_company ON climate_memories(company);
CREATE INDEX IF NOT EXISTS idx_climate_memories_sector ON climate_memories(sector);

-- Create function for semantic search
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(1536),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        climate_memories.id,
        climate_memories.content,
        climate_memories.metadata,
        1 - (climate_memories.embedding <=> query_embedding) as similarity
    FROM climate_memories
    WHERE 1 - (climate_memories.embedding <=> query_embedding) > match_threshold
    ORDER BY climate_memories.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create function for hybrid search (combining vector and text search)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding vector(1536),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity float,
    text_similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        climate_memories.id,
        climate_memories.content,
        climate_memories.metadata,
        1 - (climate_memories.embedding <=> query_embedding) as similarity,
        ts_rank_cd(to_tsvector('english', climate_memories.content), plainto_tsquery('english', query_text)) as text_similarity
    FROM climate_memories
    WHERE 
        1 - (climate_memories.embedding <=> query_embedding) > match_threshold
        OR to_tsvector('english', climate_memories.content) @@ plainto_tsquery('english', query_text)
    ORDER BY 
        (1 - (climate_memories.embedding <=> query_embedding)) DESC,
        ts_rank_cd(to_tsvector('english', climate_memories.content), plainto_tsquery('english', query_text)) DESC
    LIMIT match_count;
END;
$$;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_climate_memories_updated_at
    BEFORE UPDATE ON climate_memories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 