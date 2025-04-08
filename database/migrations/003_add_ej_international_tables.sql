-- Migration: Add EJ Communities and International Professionals Tables
-- Created: 2024-05-15

-- EJ Communities Tables

-- Gateway Cities reference table
CREATE TABLE IF NOT EXISTS gateway_cities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    county TEXT NOT NULL,
    population INTEGER,
    median_income NUMERIC,
    minority_percentage NUMERIC,
    english_isolation_percentage NUMERIC,
    geom GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- EJ Census Tracts table
CREATE TABLE IF NOT EXISTS ej_census_tracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    census_tract_id TEXT NOT NULL,
    city TEXT NOT NULL,
    county TEXT NOT NULL,
    ej_criteria JSONB NOT NULL,
    population INTEGER,
    median_income NUMERIC,
    minority_percentage NUMERIC,
    english_isolation_percentage NUMERIC,
    geom GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transportation hubs table
CREATE TABLE IF NOT EXISTS transportation_hubs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- bus_terminal, train_station, etc.
    city TEXT NOT NULL,
    address TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    geom GEOMETRY(POINT, 4326),
    services JSONB,
    accessibility_features JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Community projects table
CREATE TABLE IF NOT EXISTS community_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    organization TEXT NOT NULL,
    type TEXT NOT NULL, -- solar, energy_efficiency, etc.
    city TEXT NOT NULL,
    address TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    geom GEOMETRY(POINT, 4326),
    description TEXT,
    participation_options JSONB,
    contact_info JSONB,
    website TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Multilingual resources table
CREATE TABLE IF NOT EXISTS multilingual_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type TEXT NOT NULL, -- glossary, guide, etc.
    language TEXT NOT NULL,
    title TEXT NOT NULL,
    content JSONB NOT NULL,
    cultural_context TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- International Professionals Tables

-- Country information table
CREATE TABLE IF NOT EXISTS country_information (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_name TEXT NOT NULL,
    country_code TEXT NOT NULL,
    education_system JSONB,
    licensing_system JSONB,
    cultural_workplace_norms JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Credential mappings table
CREATE TABLE IF NOT EXISTS credential_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    origin_country TEXT NOT NULL,
    origin_credential TEXT NOT NULL,
    credential_type TEXT NOT NULL, -- degree, certification, license
    field TEXT NOT NULL, -- engineering, electrical, etc.
    massachusetts_equivalent TEXT,
    recognition_status TEXT NOT NULL, -- full, partial, not recognized
    gaps JSONB,
    licensing_board TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Regulatory requirements table
CREATE TABLE IF NOT EXISTS regulatory_requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    occupation TEXT NOT NULL,
    license_type TEXT NOT NULL,
    licensing_board TEXT NOT NULL,
    education_requirements TEXT,
    experience_requirements TEXT,
    exam_requirements JSONB,
    fees JSONB,
    renewal_requirements TEXT,
    continuing_education TEXT,
    website TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Support resources table
CREATE TABLE IF NOT EXISTS support_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    resource_type TEXT NOT NULL, -- government, nonprofit, community_organization
    website TEXT,
    services JSONB,
    target_audience JSONB, -- ej_communities, international_professionals, etc.
    languages JSONB,
    contact_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profile extensions

-- Add columns to user_profiles table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_profiles') THEN
        -- Add EJ community fields
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'is_ej_community') THEN
            ALTER TABLE user_profiles ADD COLUMN is_ej_community BOOLEAN DEFAULT FALSE;
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'preferred_language') THEN
            ALTER TABLE user_profiles ADD COLUMN preferred_language TEXT;
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'transportation_constraints') THEN
            ALTER TABLE user_profiles ADD COLUMN transportation_constraints JSONB;
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'cultural_context') THEN
            ALTER TABLE user_profiles ADD COLUMN cultural_context TEXT;
        END IF;
        
        -- Add international professional fields
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'origin_country') THEN
            ALTER TABLE user_profiles ADD COLUMN origin_country TEXT;
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'international_credentials') THEN
            ALTER TABLE user_profiles ADD COLUMN international_credentials JSONB;
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'credential_evaluation') THEN
            ALTER TABLE user_profiles ADD COLUMN credential_evaluation JSONB;
        END IF;
    END IF;
END $$;

-- Create indexes

-- Gateway Cities indexes
CREATE INDEX IF NOT EXISTS idx_gateway_cities_name ON gateway_cities(name);
CREATE INDEX IF NOT EXISTS idx_gateway_cities_geom ON gateway_cities USING GIST(geom);

-- EJ Census Tracts indexes
CREATE INDEX IF NOT EXISTS idx_ej_census_tracts_city ON ej_census_tracts(city);
CREATE INDEX IF NOT EXISTS idx_ej_census_tracts_geom ON ej_census_tracts USING GIST(geom);

-- Transportation hubs indexes
CREATE INDEX IF NOT EXISTS idx_transportation_hubs_city ON transportation_hubs(city);
CREATE INDEX IF NOT EXISTS idx_transportation_hubs_type ON transportation_hubs(type);
CREATE INDEX IF NOT EXISTS idx_transportation_hubs_geom ON transportation_hubs USING GIST(geom);

-- Community projects indexes
CREATE INDEX IF NOT EXISTS idx_community_projects_city ON community_projects(city);
CREATE INDEX IF NOT EXISTS idx_community_projects_type ON community_projects(type);
CREATE INDEX IF NOT EXISTS idx_community_projects_geom ON community_projects USING GIST(geom);

-- Multilingual resources indexes
CREATE INDEX IF NOT EXISTS idx_multilingual_resources_language ON multilingual_resources(language);
CREATE INDEX IF NOT EXISTS idx_multilingual_resources_type ON multilingual_resources(resource_type);

-- Country information indexes
CREATE INDEX IF NOT EXISTS idx_country_information_name ON country_information(country_name);
CREATE INDEX IF NOT EXISTS idx_country_information_code ON country_information(country_code);

-- Credential mappings indexes
CREATE INDEX IF NOT EXISTS idx_credential_mappings_country ON credential_mappings(origin_country);
CREATE INDEX IF NOT EXISTS idx_credential_mappings_field ON credential_mappings(field);
CREATE INDEX IF NOT EXISTS idx_credential_mappings_status ON credential_mappings(recognition_status);

-- Regulatory requirements indexes
CREATE INDEX IF NOT EXISTS idx_regulatory_requirements_occupation ON regulatory_requirements(occupation);
CREATE INDEX IF NOT EXISTS idx_regulatory_requirements_license ON regulatory_requirements(license_type);
CREATE INDEX IF NOT EXISTS idx_regulatory_requirements_board ON regulatory_requirements(licensing_board);

-- Support resources indexes
CREATE INDEX IF NOT EXISTS idx_support_resources_type ON support_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_support_resources_gin_audience ON support_resources USING GIN(target_audience);
CREATE INDEX IF NOT EXISTS idx_support_resources_gin_languages ON support_resources USING GIN(languages);

-- Create functions for geospatial queries

-- Function to find opportunities within a radius of a location
CREATE OR REPLACE FUNCTION find_opportunities_in_radius(
    location_point GEOMETRY,
    radius_miles NUMERIC,
    is_ej_priority BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    type TEXT,
    organization TEXT,
    address TEXT,
    distance_miles NUMERIC,
    has_public_transit BOOLEAN,
    ej_friendly BOOLEAN
) AS $$
BEGIN
    -- Convert miles to meters (1 mile ≈ 1609.34 meters)
    DECLARE radius_meters NUMERIC := radius_miles * 1609.34;
    
    RETURN QUERY
    WITH nearby_opportunities AS (
        -- Find nearby community projects
        SELECT 
            cp.id,
            cp.name,
            cp.type,
            cp.organization,
            cp.address,
            ST_Distance(cp.geom, location_point) / 1609.34 AS distance_miles,
            EXISTS (
                SELECT 1 FROM transportation_hubs th
                WHERE ST_DWithin(th.geom, cp.geom, 800) -- 800 meters ≈ 0.5 miles
                AND th.type IN ('bus_terminal', 'train_station', 'subway_station')
            ) AS has_public_transit,
            TRUE AS ej_friendly
        FROM community_projects cp
        WHERE ST_DWithin(cp.geom, location_point, radius_meters)
        
        UNION ALL
        
        -- Find nearby job opportunities (assuming a job_opportunities table exists)
        SELECT 
            jo.id,
            jo.title AS name,
            'job' AS type,
            jo.company AS organization,
            jo.address,
            ST_Distance(jo.geom, location_point) / 1609.34 AS distance_miles,
            EXISTS (
                SELECT 1 FROM transportation_hubs th
                WHERE ST_DWithin(th.geom, jo.geom, 800)
                AND th.type IN ('bus_terminal', 'train_station', 'subway_station')
            ) AS has_public_transit,
            jo.ej_friendly
        FROM job_opportunities jo
        WHERE ST_DWithin(jo.geom, location_point, radius_meters)
        
        UNION ALL
        
        -- Find nearby training programs (assuming a training_programs table exists)
        SELECT 
            tp.id,
            tp.name,
            'training' AS type,
            tp.provider AS organization,
            tp.address,
            ST_Distance(tp.geom, location_point) / 1609.34 AS distance_miles,
            EXISTS (
                SELECT 1 FROM transportation_hubs th
                WHERE ST_DWithin(th.geom, tp.geom, 800)
                AND th.type IN ('bus_terminal', 'train_station', 'subway_station')
            ) AS has_public_transit,
            tp.ej_friendly
        FROM training_programs tp
        WHERE ST_DWithin(tp.geom, location_point, radius_meters)
    )
    
    SELECT * FROM nearby_opportunities
    WHERE (NOT is_ej_priority OR ej_friendly = TRUE)
    ORDER BY 
        CASE WHEN is_ej_priority THEN
            -- Prioritize opportunities with public transit when EJ priority is set
            CASE WHEN has_public_transit THEN 0 ELSE 1 END
        ELSE
            0
        END,
        distance_miles ASC;
END;
$$ LANGUAGE plpgsql;
