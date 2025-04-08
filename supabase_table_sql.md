# Supabase Table Creation SQL

Here are the SQL statements needed to create the missing tables for the Climate Economy Ecosystem project. You can run these statements in the Supabase SQL Editor.

## 1. Profiles Table

```sql
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    email TEXT,
    name TEXT,
    location TEXT,
    user_type TEXT,
    is_veteran BOOLEAN DEFAULT FALSE,
    is_ej_community BOOLEAN DEFAULT FALSE,
    gateway_city TEXT,
    resume_url TEXT,
    skills TEXT[],
    experience_level TEXT,
    preferred_sectors TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create sample profile
INSERT INTO public.profiles (id, user_id, email, name, location, user_type, is_veteran, is_ej_community, gateway_city, skills, experience_level, preferred_sectors)
VALUES 
    (gen_random_uuid(), '00000000-0000-0000-0000-000000000000', 'test@example.com', 'Test User', 'Boston, MA', 'Job Seeker', false, true, 'Boston', ARRAY['Solar Energy', 'Project Management'], 'Entry-Level', ARRAY['Clean Energy', 'Energy Efficiency']);
```

## 2. Job Matches Table

```sql
CREATE TABLE IF NOT EXISTS public.job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    job_id UUID,
    company_name TEXT,
    job_title TEXT,
    match_score INTEGER,
    status TEXT,
    location TEXT,
    url TEXT,
    applied_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.job_matches ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own job matches"
    ON public.job_matches
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own job matches"
    ON public.job_matches
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own job matches"
    ON public.job_matches
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Create sample job match
INSERT INTO public.job_matches (user_id, company_name, job_title, match_score, status, location)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'EcoTech Solutions', 'Solar Panel Installer', 85, 'open', 'Boston, MA');
```

## 3. Chats Table

```sql
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    message TEXT NOT NULL,
    role TEXT NOT NULL,
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own chats"
    ON public.chats
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chats"
    ON public.chats
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create sample chat
INSERT INTO public.chats (user_id, message, role, context)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'Hello, I am looking for solar energy jobs in Boston.', 'user', '{"location": "Boston", "sector": "Solar Energy"}'::jsonb);
```

## 4. Activity Log Table

```sql
CREATE TABLE IF NOT EXISTS public.activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    action TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own activity logs"
    ON public.activity_log
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert activity logs"
    ON public.activity_log
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create sample activity log
INSERT INTO public.activity_log (user_id, action, details)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'profile_updated', '{"fields": ["skills", "location"]}'::jsonb);
```

## 5. Climate Memories Table (if needed)

```sql
CREATE TABLE IF NOT EXISTS public.climate_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    user_id TEXT,
    metadata JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.climate_memories ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Anyone can select climate_memories"
    ON public.climate_memories
    FOR SELECT
    USING (true);

-- Create vector search function
CREATE OR REPLACE FUNCTION search_memories(
  query_text TEXT,
  match_count INT DEFAULT 5
)
RETURNS SETOF climate_memories
LANGUAGE plpgsql
AS $$
DECLARE
  query_embedding vector(1536);
BEGIN
  -- You would need to implement this separately with OpenAI
  -- This is just a placeholder
  SELECT embedding INTO query_embedding FROM 
    climate_memories WHERE id = (SELECT id FROM climate_memories LIMIT 1);
  
  -- Return matches sorted by similarity
  RETURN QUERY
  SELECT *
  FROM climate_memories
  WHERE embedding IS NOT NULL
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

## 6. Training Programs Table

```sql
CREATE TABLE IF NOT EXISTS public.training_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    provider TEXT NOT NULL,
    description TEXT,
    location TEXT,
    duration TEXT,
    cost TEXT,
    url TEXT,
    skills_covered TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.training_programs ENABLE ROW LEVEL SECURITY;

-- Create policy for anyone to view
CREATE POLICY "Anyone can view training programs"
    ON public.training_programs
    FOR SELECT
    USING (true);

-- Create sample training program
INSERT INTO public.training_programs (title, provider, description, location, duration, cost, skills_covered)
VALUES 
    ('Solar Panel Installation Training', 'Massachusetts Clean Energy Center', 'Comprehensive training for solar panel installation and maintenance', 'Boston, MA', '8 weeks', '$2,500', ARRAY['Solar Installation', 'Electrical Systems', 'Safety Procedures']);
```

## How to Use These SQL Statements

1. Log in to your Supabase project dashboard
2. Go to the SQL Editor section
3. Create a new query
4. Copy and paste each section separately and run them one by one
5. Verify the tables were created by checking the Table Editor

Remember to run these SQL statements with caution in a production environment. You may want to modify them according to your specific needs, especially the sample data insertions.

## Additional Notes

- These tables use Row Level Security (RLS) policies to ensure data is only accessible to the appropriate users
- Sample data is included to help with testing
- The vector search function for climate_memories is just a placeholder - you'd need to implement the proper embedding generation with OpenAI 