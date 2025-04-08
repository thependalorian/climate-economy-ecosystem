-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create tables
CREATE TABLE IF NOT EXISTS climate_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    user_id TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT,
    location TEXT,
    is_ej_community BOOLEAN DEFAULT FALSE,
    gateway_city TEXT,
    is_veteran BOOLEAN DEFAULT FALSE,
    military_background JSONB,
    international_credentials JSONB,
    preferences JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    properties JSONB DEFAULT '{}'::JSONB,
    session_id TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    career_page TEXT,
    location TEXT,
    sector TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT,
    salary_range TEXT,
    requirements JSONB,
    is_ej_friendly BOOLEAN DEFAULT FALSE,
    is_veteran_friendly BOOLEAN DEFAULT FALSE,
    is_international_friendly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS training_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    provider TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    duration TEXT NOT NULL,
    cost TEXT,
    funding_options JSONB,
    requirements TEXT,
    is_ej_focused BOOLEAN DEFAULT FALSE,
    sector TEXT NOT NULL,
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON climate_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_events_type_timestamp ON events(event_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON job_opportunities(location);
CREATE INDEX IF NOT EXISTS idx_jobs_ej_friendly ON job_opportunities(is_ej_friendly) WHERE is_ej_friendly = TRUE;
CREATE INDEX IF NOT EXISTS idx_jobs_veteran_friendly ON job_opportunities(is_veteran_friendly) WHERE is_veteran_friendly = TRUE;
CREATE INDEX IF NOT EXISTS idx_training_location ON training_programs(location);
CREATE INDEX IF NOT EXISTS idx_training_sector ON training_programs(sector);
CREATE INDEX IF NOT EXISTS idx_training_ej_focused ON training_programs(is_ej_focused) WHERE is_ej_focused = TRUE;

-- Enable Row Level Security
ALTER TABLE climate_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_programs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable read access for all users" ON climate_memories
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON climate_memories
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for all users" ON user_profiles
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON user_profiles
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for all users" ON events
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON events
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for all users" ON companies
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON companies
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for all users" ON job_opportunities
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON job_opportunities
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for all users" ON training_programs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON training_programs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated'); 