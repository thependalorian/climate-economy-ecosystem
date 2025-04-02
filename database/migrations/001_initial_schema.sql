-- Migration: Initial Schema
-- Created: 2024-04-02

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS "vector";

-- climate_memories table (for mem0 storage)
CREATE TABLE IF NOT EXISTS climate_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    user_id TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON climate_memories(user_id);

-- User profiles table
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

-- Events table for metrics tracking
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    properties JSONB DEFAULT '{}'::JSONB,
    session_id TEXT
);

-- Create index on event_type and timestamp for analytics queries
CREATE INDEX IF NOT EXISTS idx_events_type_timestamp ON events(event_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    career_page TEXT,
    location TEXT,
    sector TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job opportunities table
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

-- Create indexes for job search
CREATE INDEX IF NOT EXISTS idx_jobs_location ON job_opportunities(location);
CREATE INDEX IF NOT EXISTS idx_jobs_ej_friendly ON job_opportunities(is_ej_friendly) WHERE is_ej_friendly = TRUE;
CREATE INDEX IF NOT EXISTS idx_jobs_veteran_friendly ON job_opportunities(is_veteran_friendly) WHERE is_veteran_friendly = TRUE;

-- Training programs table
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

-- Create indexes for training program search
CREATE INDEX IF NOT EXISTS idx_training_location ON training_programs(location);
CREATE INDEX IF NOT EXISTS idx_training_sector ON training_programs(sector);
CREATE INDEX IF NOT EXISTS idx_training_ej_focused ON training_programs(is_ej_focused) WHERE is_ej_focused = TRUE; 