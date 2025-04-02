-- Migration: Credential Evaluation Support
-- Created: 2024-07-10

-- Credential evaluation records table
CREATE TABLE IF NOT EXISTS credential_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    country TEXT NOT NULL,
    original_credential TEXT NOT NULL,
    field TEXT,
    us_equivalent TEXT,
    evaluation_notes TEXT,
    recommended_actions JSONB,
    additional_training JSONB,
    confidence INTEGER,
    massachusetts_specific JSONB,
    resources JSONB,
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'pending',
    has_formal_evaluation BOOLEAN DEFAULT FALSE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_credential_user_id ON credential_evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_credential_country ON credential_evaluations(country);
CREATE INDEX IF NOT EXISTS idx_credential_field ON credential_evaluations(field);

-- Add education equivalency reference table
CREATE TABLE IF NOT EXISTS education_equivalencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country TEXT NOT NULL,
    original_credential TEXT NOT NULL,
    us_equivalent TEXT NOT NULL,
    education_level TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique constraint on country/credential combination
CREATE UNIQUE INDEX IF NOT EXISTS idx_education_equiv_unique 
ON education_equivalencies(country, original_credential);

-- Add credential evaluation services table
CREATE TABLE IF NOT EXISTS credential_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    is_naces_member BOOLEAN DEFAULT FALSE,
    serves_clean_energy BOOLEAN DEFAULT FALSE,
    massachusetts_specific BOOLEAN DEFAULT FALSE,
    processing_time TEXT,
    approximate_cost TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add functional index for searching credential evaluations
CREATE INDEX idx_credential_eval_search ON credential_evaluations 
USING gin((
    setweight(to_tsvector('english', coalesce(country, '')), 'A') || 
    setweight(to_tsvector('english', coalesce(original_credential, '')), 'A') || 
    setweight(to_tsvector('english', coalesce(field, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(us_equivalent, '')), 'B')
));

-- Add field to track international credential verification
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS credential_verified BOOLEAN DEFAULT FALSE;

-- Add function to auto-update user_profiles when credential is evaluated
CREATE OR REPLACE FUNCTION update_user_profile_credentials()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the user_profile with the most recent evaluation results
    UPDATE user_profiles
    SET 
        international_credentials = jsonb_build_object(
            'country', NEW.country,
            'original_credential', NEW.original_credential,
            'field', NEW.field,
            'us_equivalent', NEW.us_equivalent,
            'evaluation_date', NEW.evaluation_date,
            'status', NEW.status
        ),
        credential_verified = NEW.has_formal_evaluation,
        updated_at = NOW()
    WHERE user_id = NEW.user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call function after insert or update
CREATE TRIGGER trigger_update_user_credentials
AFTER INSERT OR UPDATE ON credential_evaluations
FOR EACH ROW
EXECUTE FUNCTION update_user_profile_credentials();

-- Update the job_opportunities table to better support international candidates
ALTER TABLE job_opportunities
ADD COLUMN IF NOT EXISTS international_equivalencies JSONB DEFAULT '[]'::JSONB; 