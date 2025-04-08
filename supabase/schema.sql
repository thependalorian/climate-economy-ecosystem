-- Consolidated Schema for Climate Economy Ecosystem
-- This file contains all the database schema definitions for the Climate Economy Ecosystem.
-- It combines all the migrations into a single file for easy initialization.

-- Initial Schema (20240402_initial_schema.sql)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- User Profiles
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    location TEXT,
    is_ej_community BOOLEAN DEFAULT FALSE,
    is_veteran BOOLEAN DEFAULT FALSE,
    is_international BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Resume Data
CREATE TABLE public.resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    extracted_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Resume Analysis
CREATE TABLE public.resume_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID REFERENCES public.resumes(id) ON DELETE CASCADE,
    skills JSONB,
    education JSONB,
    work_history JSONB,
    certifications JSONB,
    social_links JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Job Recommendations
CREATE TABLE public.job_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    url TEXT,
    salary_range TEXT,
    match_score FLOAT,
    skills_match JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Skill Gaps
CREATE TABLE public.skill_gaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    missing_skill TEXT NOT NULL,
    importance_score FLOAT,
    training_resources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Training Paths
CREATE TABLE public.training_paths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    path_name TEXT NOT NULL,
    description TEXT,
    skills JSONB,
    resources JSONB,
    estimated_time TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Chat Sessions
CREATE TABLE public.chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Chat Messages
CREATE TABLE public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID REFERENCES public.chats(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    user_query TEXT NOT NULL,
    agent_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Memory Storage
CREATE TABLE public.memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    category TEXT,
    metadata JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- RLS Policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resume_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.memories ENABLE ROW LEVEL SECURITY;

-- Profile policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles
    FOR SELECT
    TO authenticated
    USING (id = auth.uid());

CREATE POLICY "Users can update their own profile"
    ON public.profiles
    FOR UPDATE
    TO authenticated
    USING (id = auth.uid());

-- Resume policies
CREATE POLICY "Users can view their own resumes"
    ON public.resumes
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own resumes"
    ON public.resumes
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own resumes"
    ON public.resumes
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid());

-- Resume analysis policies
CREATE POLICY "Users can view their own resume analysis"
    ON public.resume_analysis
    FOR SELECT
    TO authenticated
    USING (resume_id IN (SELECT id FROM public.resumes WHERE user_id = auth.uid()));

-- Job recommendation policies
CREATE POLICY "Users can view their own job recommendations"
    ON public.job_recommendations
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Skill gaps policies
CREATE POLICY "Users can view their own skill gaps"
    ON public.skill_gaps
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Training paths policies
CREATE POLICY "Users can view their own training paths"
    ON public.training_paths
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Chat policies
CREATE POLICY "Users can view their own chats"
    ON public.chats
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own chats"
    ON public.chats
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

-- Chat messages policies
CREATE POLICY "Users can view messages from their chats"
    ON public.chat_messages
    FOR SELECT
    TO authenticated
    USING (chat_id IN (SELECT id FROM public.chats WHERE user_id = auth.uid()));

-- Memory policies
CREATE POLICY "Users can view their own memories"
    ON public.memories
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Grant privileges
GRANT SELECT, INSERT, UPDATE ON public.profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.resumes TO authenticated;
GRANT SELECT ON public.resume_analysis TO authenticated;
GRANT SELECT ON public.job_recommendations TO authenticated;
GRANT SELECT ON public.skill_gaps TO authenticated;
GRANT SELECT ON public.training_paths TO authenticated;
GRANT SELECT, INSERT ON public.chats TO authenticated;
GRANT SELECT ON public.chat_messages TO authenticated;
GRANT SELECT ON public.memories TO authenticated;

-- Profile Enrichment (20231201000000_profile_enrichment.sql)
CREATE TABLE public.profile_enrichment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    linkedin_url TEXT,
    github_url TEXT,
    twitter_url TEXT,
    portfolio_url TEXT,
    skills JSONB,
    interests JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.profile_enrichment ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile enrichment"
    ON public.profile_enrichment
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their own profile enrichment"
    ON public.profile_enrichment
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own profile enrichment"
    ON public.profile_enrichment
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

GRANT SELECT, INSERT, UPDATE ON public.profile_enrichment TO authenticated;

-- Engagement Scoring (20240402_engagement_scoring.sql)
CREATE TABLE public.user_engagement (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    login_count INTEGER DEFAULT 0,
    chat_count INTEGER DEFAULT 0,
    job_view_count INTEGER DEFAULT 0,
    resource_view_count INTEGER DEFAULT 0,
    satisfaction_score INTEGER DEFAULT 0,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.user_engagement ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own engagement"
    ON public.user_engagement
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

GRANT SELECT ON public.user_engagement TO authenticated;

-- Feature Votes (20240402_feature_votes.sql)
CREATE TABLE public.feature_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    feature_name TEXT NOT NULL,
    vote_value INTEGER NOT NULL CHECK (vote_value >= 1 AND vote_value <= 5),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.feature_votes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own feature votes"
    ON public.feature_votes
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own feature votes"
    ON public.feature_votes
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

GRANT SELECT, INSERT ON public.feature_votes TO authenticated;

-- Add Indexes and Vectors (20240403_add_indexes_and_vectors.sql)
-- Add indexes for performance
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX idx_resume_analysis_resume_id ON public.resume_analysis(resume_id);
CREATE INDEX idx_job_recommendations_user_id ON public.job_recommendations(user_id);
CREATE INDEX idx_skill_gaps_user_id ON public.skill_gaps(user_id);
CREATE INDEX idx_training_paths_user_id ON public.training_paths(user_id);
CREATE INDEX idx_chats_user_id ON public.chats(user_id);
CREATE INDEX idx_chat_messages_chat_id ON public.chat_messages(chat_id);
CREATE INDEX idx_memories_user_id ON public.memories(user_id);
CREATE INDEX idx_memories_category ON public.memories(category);

-- Add vector index for memory embeddings
CREATE INDEX idx_memories_embedding ON public.memories USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Connection Thresholds (20240403_connection_thresholds.sql)
CREATE TABLE public.connection_thresholds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    connection_type TEXT NOT NULL,
    threshold FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.connection_thresholds ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own connection thresholds"
    ON public.connection_thresholds
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their own connection thresholds"
    ON public.connection_thresholds
    FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own connection thresholds"
    ON public.connection_thresholds
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

GRANT SELECT, INSERT, UPDATE ON public.connection_thresholds TO authenticated;

-- User Engagement (20240403_user_engagement.sql)
-- Add new columns to user_engagement table
ALTER TABLE public.user_engagement 
ADD COLUMN profile_completion_percentage INTEGER DEFAULT 0,
ADD COLUMN days_active_last_month INTEGER DEFAULT 0,
ADD COLUMN feature_usage JSONB,
ADD COLUMN engagement_score FLOAT DEFAULT 0;

-- Chat Feedback (20240404_chat_feedback.sql)
CREATE TABLE public.chat_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    message_id UUID REFERENCES public.chat_messages(id) ON DELETE CASCADE,
    feedback_type TEXT NOT NULL,
    feedback_details TEXT,
    feedback_time TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.chat_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own chat feedback"
    ON public.chat_feedback
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own chat feedback"
    ON public.chat_feedback
    FOR INSERT
    TO authenticated
    WITH CHECK (user_id = auth.uid());

GRANT SELECT, INSERT ON public.chat_feedback TO authenticated;

-- RLHF Schema (20240405_rlhf_schema.sql)
-- Step tracking table
CREATE TABLE public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES public.chats(id),
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Add step_id to chat_feedback
ALTER TABLE public.chat_feedback
ADD COLUMN step_id UUID REFERENCES public.reasoning_steps(id),
ADD COLUMN feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5);

-- Add indices
CREATE INDEX idx_reasoning_steps_chat_id ON public.reasoning_steps(chat_id);
CREATE INDEX idx_chat_feedback_step_id ON public.chat_feedback(step_id);

-- RLS policies
ALTER TABLE public.reasoning_steps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view steps from their chats"
    ON public.reasoning_steps
    FOR SELECT
    TO authenticated
    USING (chat_id IN (SELECT id FROM public.chats WHERE user_id = auth.uid()));

-- Grant privileges
GRANT SELECT ON public.reasoning_steps TO authenticated;
GRANT INSERT, UPDATE ON public.chat_feedback TO authenticated;
