-- Migration file for RLHF feedback analytics
-- This table stores aggregated feedback metrics for RLHF

-- Feedback analytics table
CREATE TABLE IF NOT EXISTS public.feedback_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    total_feedback_count INTEGER DEFAULT 0,
    step_feedback_count INTEGER DEFAULT 0,
    message_feedback_count INTEGER DEFAULT 0,
    positive_step_feedback INTEGER DEFAULT 0,
    negative_step_feedback INTEGER DEFAULT 0,
    positive_message_feedback INTEGER DEFAULT 0,
    negative_message_feedback INTEGER DEFAULT 0,
    average_score FLOAT DEFAULT 3.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_feedback_analytics_user_id ON public.feedback_analytics(user_id);

-- RLS policies
ALTER TABLE public.feedback_analytics ENABLE ROW LEVEL SECURITY;

-- Users can view their own feedback analytics
CREATE POLICY "Users can view their own feedback analytics"
    ON public.feedback_analytics
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Only the system can insert/update feedback analytics
CREATE POLICY "System can manage feedback analytics"
    ON public.feedback_analytics
    USING (true);

-- Grant privileges
GRANT SELECT ON public.feedback_analytics TO authenticated;
GRANT INSERT, UPDATE ON public.feedback_analytics TO service_role; 