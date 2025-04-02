-- Create job_listings table for storing company job listings
CREATE TABLE IF NOT EXISTS public.job_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company TEXT NOT NULL REFERENCES public.companies(name),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location TEXT,
    sector TEXT,
    focus_areas TEXT[],
    salary_range TEXT,
    application_url TEXT,
    skills_required TEXT[],
    experience_level TEXT,
    remote_status TEXT,
    posted_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_date TIMESTAMP WITH TIME ZONE,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(requirements, '')), 'C')
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create index on company field
CREATE INDEX IF NOT EXISTS job_listings_company_idx ON public.job_listings(company);

-- Create index on sector field
CREATE INDEX IF NOT EXISTS job_listings_sector_idx ON public.job_listings(sector);

-- Create index on focus_areas field
CREATE INDEX IF NOT EXISTS job_listings_focus_areas_idx ON public.job_listings USING gin(focus_areas);

-- Create index on skills_required field
CREATE INDEX IF NOT EXISTS job_listings_skills_idx ON public.job_listings USING gin(skills_required);

-- Create full-text search index
CREATE INDEX IF NOT EXISTS job_listings_search_idx ON public.job_listings USING gin(search_vector);

-- Create table for job search queries and results
CREATE TABLE IF NOT EXISTS public.job_search_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_query JSONB NOT NULL,
    result_ids UUID[] NOT NULL,
    search_time TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT now() + interval '1 day',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS on the tables
ALTER TABLE public.job_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_search_cache ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to read job listings
CREATE POLICY "Authenticated users can read job_listings"
ON public.job_listings
FOR SELECT
TO authenticated
USING (true);

-- Create policy for service roles to manage job listings
CREATE POLICY "Service role can manage job_listings"
ON public.job_listings
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Create policy for authenticated users to read job search cache
CREATE POLICY "Authenticated users can read job_search_cache"
ON public.job_search_cache
FOR SELECT
TO authenticated
USING (true);

-- Create policy for service roles to manage job search cache
CREATE POLICY "Service role can manage job_search_cache"
ON public.job_search_cache
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Function to search for job listings based on criteria
CREATE OR REPLACE FUNCTION search_job_listings(
    search_text TEXT DEFAULT NULL,
    company_names TEXT[] DEFAULT NULL,
    sectors TEXT[] DEFAULT NULL,
    focus_areas TEXT[] DEFAULT NULL,
    skills TEXT[] DEFAULT NULL,
    experience_levels TEXT[] DEFAULT NULL,
    locations TEXT[] DEFAULT NULL,
    remote_status TEXT DEFAULT NULL,
    max_results INT DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    company TEXT,
    title TEXT,
    description TEXT,
    requirements TEXT,
    location TEXT,
    sector TEXT,
    focus_areas TEXT[],
    skills_required TEXT[],
    experience_level TEXT,
    remote_status TEXT,
    application_url TEXT,
    posted_date TIMESTAMP WITH TIME ZONE,
    rank FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        j.id,
        j.company,
        j.title,
        j.description,
        j.requirements,
        j.location,
        j.sector,
        j.focus_areas,
        j.skills_required,
        j.experience_level,
        j.remote_status,
        j.application_url,
        j.posted_date,
        ts_rank(j.search_vector, query) AS rank
    FROM 
        public.job_listings j,
        to_tsquery('english', coalesce(
            regexp_replace(search_text, '[^a-zA-Z0-9]+', ' & ', 'g'),
            ''
        )) query
    WHERE
        -- Only return non-expired jobs
        (j.expires_date IS NULL OR j.expires_date > now())
        -- Apply search_text filter if provided
        AND (search_text IS NULL OR j.search_vector @@ query)
        -- Apply company filter if provided
        AND (company_names IS NULL OR j.company = ANY(company_names))
        -- Apply sector filter if provided
        AND (sectors IS NULL OR j.sector = ANY(sectors))
        -- Apply focus areas filter if provided
        AND (focus_areas IS NULL OR j.focus_areas && focus_areas)
        -- Apply skills filter if provided
        AND (skills IS NULL OR j.skills_required && skills)
        -- Apply experience level filter if provided
        AND (experience_levels IS NULL OR j.experience_level = ANY(experience_levels))
        -- Apply location filter if provided
        AND (locations IS NULL OR j.location = ANY(locations))
        -- Apply remote status filter if provided
        AND (remote_status IS NULL OR j.remote_status = remote_status)
    ORDER BY
        CASE WHEN search_text IS NOT NULL THEN ts_rank(j.search_vector, query) ELSE 0 END DESC,
        j.posted_date DESC
    LIMIT max_results;
END;
$$; 