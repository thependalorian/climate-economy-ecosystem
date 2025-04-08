-- Setup All Tables for Climate Economy Ecosystem
-- Run this script in the Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- PROFILES TABLE
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- JOB MATCHES TABLE
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

-- CHATS TABLE
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

-- ACTIVITY LOG TABLE
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

-- REASONING STEPS TABLE (for RLHF)
CREATE TABLE IF NOT EXISTS public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.reasoning_steps ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own reasoning steps"
    ON public.reasoning_steps
    FOR SELECT
    USING (
        chat_id IN (
            SELECT id FROM public.chats WHERE user_id = auth.uid()
        )
    );

-- CHAT FEEDBACK TABLE
CREATE TABLE IF NOT EXISTS public.chat_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    step_id UUID REFERENCES reasoning_steps(id) ON DELETE CASCADE,
    user_id UUID,
    feedback TEXT,
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    feedback_type TEXT DEFAULT 'message',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.chat_feedback ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own feedback"
    ON public.chat_feedback
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own feedback"
    ON public.chat_feedback
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Create indices for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_job_matches_user_id ON job_matches(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_steps_chat_id ON reasoning_steps(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_chat_id ON chat_feedback(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_step_id ON chat_feedback(step_id);

-- Insert sample data
-- Sample profile
INSERT INTO public.profiles (user_id, email, name, location, user_type, is_veteran, is_ej_community, gateway_city, skills, experience_level, preferred_sectors)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'test@example.com', 'Test User', 'Boston, MA', 'Job Seeker', false, true, 'Boston', ARRAY['Solar Energy', 'Project Management'], 'Entry-Level', ARRAY['Clean Energy', 'Energy Efficiency']);

-- Sample job match
INSERT INTO public.job_matches (user_id, company_name, job_title, match_score, status, location)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'EcoTech Solutions', 'Solar Panel Installer', 85, 'open', 'Boston, MA');

-- Sample chat
INSERT INTO public.chats (user_id, message, role, context)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'Hello, I am looking for solar energy jobs in Boston.', 'user', '{"location": "Boston", "sector": "Solar Energy"}'::jsonb);

-- Sample activity log
INSERT INTO public.activity_log (user_id, action, details)
VALUES 
    ('00000000-0000-0000-0000-000000000000', 'profile_updated', '{"fields": ["skills", "location"]}'::jsonb); 