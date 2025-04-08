-- Enable the UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    file_path TEXT NOT NULL,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create partner_organizations table
CREATE TABLE IF NOT EXISTS partner_organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    location TEXT,
    skills TEXT[],
    interests TEXT[],
    community_involvement BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create sectors table
CREATE TABLE IF NOT EXISTS sectors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    opportunities TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create domains table
CREATE TABLE IF NOT EXISTS domains (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    skills TEXT[],
    certifications TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create RLS policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE partner_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains ENABLE ROW LEVEL SECURITY;

-- Create policies for documents
CREATE POLICY "Enable read access for all users" ON documents
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON documents
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policies for partner_organizations
CREATE POLICY "Enable read access for all users" ON partner_organizations
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON partner_organizations
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policies for sectors
CREATE POLICY "Enable read access for all users" ON sectors
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON sectors
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policies for domains
CREATE POLICY "Enable read access for all users" ON domains
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON domains
    FOR INSERT WITH CHECK (auth.role() = 'authenticated'); 