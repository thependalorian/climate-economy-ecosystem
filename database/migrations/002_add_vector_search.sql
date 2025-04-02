-- Migration: Add Vector Search Functionality
-- Created: 2024-04-02

-- Check if vector extension is available and installed
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        RAISE NOTICE 'Vector extension is not installed. Please install pgvector extension first.';
    END IF;
END
$$;

-- Enable the pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create climate_memories table for storing company and climate resources
CREATE TABLE IF NOT EXISTS public.climate_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    source_type TEXT,
    url TEXT,
    title TEXT,
    chunk_index INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 1,
    crawl_time TIMESTAMP WITH TIME ZONE DEFAULT now(),
    company TEXT,
    sector TEXT,
    domain TEXT,
    path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create index on company field
CREATE INDEX IF NOT EXISTS climate_memories_company_idx ON public.climate_memories(company);

-- Create index on sector field
CREATE INDEX IF NOT EXISTS climate_memories_sector_idx ON public.climate_memories(sector);

-- Create index on source_type field
CREATE INDEX IF NOT EXISTS climate_memories_source_type_idx ON public.climate_memories(source_type);

-- Create index on url field
CREATE INDEX IF NOT EXISTS climate_memories_url_idx ON public.climate_memories(url);

-- Create vector index on embedding field
CREATE INDEX IF NOT EXISTS climate_memories_embedding_idx ON public.climate_memories USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Enable RLS on the table
ALTER TABLE public.climate_memories ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to read
CREATE POLICY "Authenticated users can read climate_memories"
ON public.climate_memories
FOR SELECT
TO authenticated
USING (true);

-- Create policy for service roles to insert/update
CREATE POLICY "Service role can insert and update climate_memories"
ON public.climate_memories
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Function to search climate_memories using vector similarity
CREATE OR REPLACE FUNCTION search_climate_memories(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.75,
    match_count INT DEFAULT 10,
    filter_company TEXT DEFAULT NULL,
    filter_sector TEXT DEFAULT NULL,
    filter_source_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT,
    company TEXT,
    sector TEXT,
    source_type TEXT,
    url TEXT,
    title TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        cm.id,
        cm.content,
        cm.metadata,
        1 - (cm.embedding <=> query_embedding) as similarity,
        cm.company,
        cm.sector,
        cm.source_type,
        cm.url,
        cm.title
    FROM public.climate_memories cm
    WHERE 
        (1 - (cm.embedding <=> query_embedding)) > match_threshold
        AND (filter_company IS NULL OR cm.company = filter_company)
        AND (filter_sector IS NULL OR cm.sector = filter_sector)
        AND (filter_source_type IS NULL OR cm.source_type = filter_source_type)
    ORDER BY cm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create HNSW index on embeddings for faster vector search
CREATE INDEX IF NOT EXISTS climate_memories_embedding_idx ON climate_memories
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Create sample gateway cities lookup table
CREATE TABLE IF NOT EXISTS gateway_cities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    county TEXT,
    primary_sectors TEXT[],
    ej_community_zones TEXT[],
    coordinates POINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert Massachusetts Gateway Cities
INSERT INTO gateway_cities (name, county, primary_sectors, ej_community_zones, coordinates)
VALUES
    ('Brockton', 'Plymouth', ARRAY['Manufacturing', 'Solar', 'Health'], ARRAY['North', 'East'], POINT(-71.0183, 42.0834)),
    ('Boston', 'Suffolk', ARRAY['Cleantech', 'Green Buildings', 'Finance'], ARRAY['Roxbury', 'Dorchester', 'Mattapan'], POINT(-71.0589, 42.3601)),
    ('Fall River', 'Bristol', ARRAY['Offshore Wind', 'Manufacturing'], ARRAY['South', 'Central'], POINT(-71.1556, 41.7015)),
    ('New Bedford', 'Bristol', ARRAY['Offshore Wind', 'Fishing'], ARRAY['South', 'Central'], POINT(-70.9342, 41.6362)),
    ('Lawrence', 'Essex', ARRAY['Energy Efficiency', 'Weatherization'], ARRAY['Central', 'North'], POINT(-71.1631, 42.7070)),
    ('Lowell', 'Middlesex', ARRAY['Energy Efficiency', 'Textiles'], ARRAY['Downtown', 'Acre'], POINT(-71.3161, 42.6334)),
    ('Springfield', 'Hampden', ARRAY['Clean Transportation', 'EVs'], ARRAY['North End', 'South End'], POINT(-72.5893, 42.1015)),
    ('Worcester', 'Worcester', ARRAY['Green Construction', 'Waste Management'], ARRAY['Main South', 'Piedmont'], POINT(-71.8023, 42.2626)),
    ('Chelsea', 'Suffolk', ARRAY['Clean Transportation', 'Waste Management'], ARRAY['Downtown', 'Waterfront'], POINT(-71.0328, 42.3917)),
    ('Holyoke', 'Hampden', ARRAY['Renewable Energy', 'Hydropower'], ARRAY['South', 'Downtown'], POINT(-72.6162, 42.2042))
ON CONFLICT (name) DO NOTHING; 