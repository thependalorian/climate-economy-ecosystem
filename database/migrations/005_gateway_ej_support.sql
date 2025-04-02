-- Migration: Gateway Cities and EJ Communities Support
-- Created: 2024-07-12

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Gateway Cities table
CREATE TABLE IF NOT EXISTS gateway_cities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    description TEXT,
    specializations TEXT[],
    key_initiatives TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on city name
CREATE UNIQUE INDEX IF NOT EXISTS idx_gateway_cities_name ON gateway_cities(name);

-- Environmental Justice communities table
CREATE TABLE IF NOT EXISTS ej_communities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    is_gateway_city BOOLEAN DEFAULT FALSE,
    census_tracts TEXT[],
    ej_criteria TEXT[],
    population INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index on community name
CREATE UNIQUE INDEX IF NOT EXISTS idx_ej_communities_name ON ej_communities(name);

-- Add spatial index for location-based queries
CREATE INDEX IF NOT EXISTS idx_gateway_cities_location ON gateway_cities USING gist (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

CREATE INDEX IF NOT EXISTS idx_ej_communities_location ON ej_communities USING gist (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

-- EJ-specific support programs table
CREATE TABLE IF NOT EXISTS ej_support_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    organization TEXT NOT NULL,
    program_type TEXT NOT NULL,
    website_url TEXT,
    funding_range TEXT,
    eligibility_criteria TEXT[],
    targeted_sectors TEXT[],
    application_deadline TEXT,
    contact_information TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Training programs for EJ communities table
CREATE TABLE IF NOT EXISTS ej_training_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    training_program_id UUID REFERENCES training_programs(id),
    ej_community_id UUID REFERENCES ej_communities(id),
    serves_ej BOOLEAN DEFAULT TRUE,
    accessibility_details TEXT,
    language_support TEXT[],
    provides_transportation BOOLEAN DEFAULT FALSE,
    provides_childcare BOOLEAN DEFAULT FALSE,
    additional_support_services TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create composite index for program-community relationship
CREATE UNIQUE INDEX IF NOT EXISTS idx_ej_training_programs_composite 
ON ej_training_programs(training_program_id, ej_community_id);

-- Enhance training_programs table with EJ and Gateway City fields
ALTER TABLE training_programs 
ADD COLUMN IF NOT EXISTS is_ej_focused BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS serves_gateway_cities BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS support_services TEXT[],
ADD COLUMN IF NOT EXISTS language_options TEXT[];

-- Enhance job_opportunities table with EJ and Gateway City fields
ALTER TABLE job_opportunities 
ADD COLUMN IF NOT EXISTS is_ej_friendly BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_gateway_city_focused BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS transportation_access TEXT,
ADD COLUMN IF NOT EXISTS language_requirements TEXT[];

-- Add function to find nearest Gateway Cities
CREATE OR REPLACE FUNCTION find_nearest_gateway_cities(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    max_distance_km DOUBLE PRECISION DEFAULT 30,
    max_results INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    distance_km DOUBLE PRECISION,
    specializations TEXT[],
    key_initiatives TEXT[]
)
LANGUAGE SQL
AS $$
    SELECT 
        gc.id,
        gc.name,
        ST_DistanceSphere(
            ST_SetSRID(ST_MakePoint(lng, lat), 4326),
            ST_SetSRID(ST_MakePoint(gc.longitude, gc.latitude), 4326)
        ) / 1000 AS distance_km,
        gc.specializations,
        gc.key_initiatives
    FROM gateway_cities gc
    WHERE ST_DistanceSphere(
        ST_SetSRID(ST_MakePoint(lng, lat), 4326),
        ST_SetSRID(ST_MakePoint(gc.longitude, gc.latitude), 4326)
    ) / 1000 <= max_distance_km
    ORDER BY distance_km ASC
    LIMIT max_results;
$$;

-- Add function to find nearest EJ communities
CREATE OR REPLACE FUNCTION find_nearest_ej_communities(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    max_distance_km DOUBLE PRECISION DEFAULT 10,
    max_results INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    distance_km DOUBLE PRECISION,
    is_gateway_city BOOLEAN,
    ej_criteria TEXT[]
)
LANGUAGE SQL
AS $$
    SELECT 
        ej.id,
        ej.name,
        ST_DistanceSphere(
            ST_SetSRID(ST_MakePoint(lng, lat), 4326),
            ST_SetSRID(ST_MakePoint(ej.longitude, ej.latitude), 4326)
        ) / 1000 AS distance_km,
        ej.is_gateway_city,
        ej.ej_criteria
    FROM ej_communities ej
    WHERE ST_DistanceSphere(
        ST_SetSRID(ST_MakePoint(lng, lat), 4326),
        ST_SetSRID(ST_MakePoint(ej.longitude, ej.latitude), 4326)
    ) / 1000 <= max_distance_km
    ORDER BY distance_km ASC
    LIMIT max_results;
$$;

-- Add function to find EJ-focused training programs near a location
CREATE OR REPLACE FUNCTION find_ej_training_programs(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    max_distance_km DOUBLE PRECISION DEFAULT 20,
    sector TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    provider TEXT,
    location TEXT,
    distance_km DOUBLE PRECISION,
    is_ej_focused BOOLEAN,
    support_services TEXT[],
    language_options TEXT[],
    sector TEXT
)
LANGUAGE SQL
AS $$
    SELECT 
        tp.id,
        tp.title,
        tp.provider,
        tp.location,
        ST_DistanceSphere(
            ST_SetSRID(ST_MakePoint(lng, lat), 4326),
            ST_SetSRID(ST_MakePoint(ej.longitude, ej.latitude), 4326)
        ) / 1000 AS distance_km,
        tp.is_ej_focused,
        tp.support_services,
        tp.language_options,
        tp.sector
    FROM training_programs tp
    JOIN ej_training_programs ejtp ON tp.id = ejtp.training_program_id
    JOIN ej_communities ej ON ejtp.ej_community_id = ej.id
    WHERE 
        tp.is_ej_focused = TRUE
        AND ST_DistanceSphere(
            ST_SetSRID(ST_MakePoint(lng, lat), 4326),
            ST_SetSRID(ST_MakePoint(ej.longitude, ej.latitude), 4326)
        ) / 1000 <= max_distance_km
        AND (sector IS NULL OR tp.sector = sector)
    ORDER BY distance_km ASC;
$$;

-- Add location field to user_profiles if not exists
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS postal_code TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS is_gateway_city_resident BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS ej_community_id UUID REFERENCES ej_communities(id),
ADD COLUMN IF NOT EXISTS transportation_access TEXT[];

-- Add function to check if a location is in an EJ community
CREATE OR REPLACE FUNCTION is_in_ej_community(
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION
)
RETURNS BOOLEAN
LANGUAGE SQL
AS $$
    SELECT EXISTS (
        SELECT 1 FROM ej_communities ej
        WHERE ST_DistanceSphere(
            ST_SetSRID(ST_MakePoint(lng, lat), 4326),
            ST_SetSRID(ST_MakePoint(ej.longitude, ej.latitude), 4326)
        ) / 1000 <= 3  -- Approximate neighborhood radius in km
    );
$$;

-- Add seed data for Gateway Cities
INSERT INTO gateway_cities (name, latitude, longitude, specializations, key_initiatives)
VALUES
    ('Lawrence', 42.7070, -71.1631, ARRAY['Energy Efficiency', 'Workforce Development', 'Solar'], ARRAY['Groundwork Lawrence green initiatives', 'Lawrence Partnership workforce development', 'Community clean energy projects']),
    ('Worcester', 42.2626, -71.8023, ARRAY['Energy Efficiency', 'Green Innovation', 'Building Retrofits'], ARRAY['Green Worcester Plan implementation', 'Clark University Climate Action Plan', 'Worcester Regional Food Hub energy efficiency']),
    ('New Bedford', 41.6362, -70.9342, ARRAY['Offshore Wind', 'Port Development', 'Coastal Resilience'], ARRAY['New Bedford Marine Commerce Terminal (offshore wind)', 'Community Preservation Act efficiency projects', 'Port electrification planning']),
    ('Holyoke', 42.2042, -72.6162, ARRAY['Solar', 'Hydropower', 'Smart Grid'], ARRAY['Mt. Tom Solar Farm (former coal plant site)', 'Holyoke Gas & Electric renewable portfolio', 'Smart grid innovations through HG&E']),
    ('Chelsea', 42.3917, -71.0328, ARRAY['Climate Resilience', 'Environmental Justice', 'Urban Sustainability'], ARRAY['Climate resilience planning with GreenRoots', 'Environmental justice advocacy', 'Municipal vulnerability preparedness program'])
ON CONFLICT (name) DO UPDATE SET
    specializations = EXCLUDED.specializations,
    key_initiatives = EXCLUDED.key_initiatives,
    updated_at = NOW();

-- Add seed data for EJ communities
INSERT INTO ej_communities (name, latitude, longitude, is_gateway_city, census_tracts, ej_criteria)
VALUES
    ('Chelsea', 42.3917, -71.0328, TRUE, ARRAY['25025050100', '25025050200', '25025050300'], ARRAY['income', 'minority', 'english isolation']),
    ('Lawrence', 42.7070, -71.1631, TRUE, ARRAY['2502535300', '2502535400', '2502535500'], ARRAY['income', 'minority', 'english isolation']),
    ('Dorchester', 42.3016, -71.0676, FALSE, ARRAY['25025090600', '25025090700', '25025090800'], ARRAY['income', 'minority', 'english isolation'])
ON CONFLICT (name) DO UPDATE SET
    is_gateway_city = EXCLUDED.is_gateway_city,
    census_tracts = EXCLUDED.census_tracts,
    ej_criteria = EXCLUDED.ej_criteria,
    updated_at = NOW(); 