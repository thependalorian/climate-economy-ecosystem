-- Migration: 010_rlhf_tables.sql
-- Description: Creates tables for Reinforcement Learning from Human Feedback (RLHF)

-- Create chats table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    conversation_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    metadata JSONB DEFAULT '{}'::JSONB,
    tokens_used INTEGER DEFAULT 0
);

-- Create reasoning_steps table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES public.chats(id) ON DELETE CASCADE,
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create chat_feedback table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.chat_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    chat_id UUID REFERENCES public.chats(id) ON DELETE CASCADE,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down', 'rating', 'comment')),
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create feedback_metrics table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.feedback_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    total_feedback_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    average_rating NUMERIC(3,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON public.chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_conversation_id ON public.chats(conversation_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_steps_chat_id ON public.reasoning_steps(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_user_id ON public.chat_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_chat_id ON public.chat_feedback(chat_id);
CREATE INDEX IF NOT EXISTS idx_feedback_metrics_date ON public.feedback_metrics(date);

-- Create function to update feedback metrics
CREATE OR REPLACE FUNCTION update_feedback_metrics()
RETURNS TRIGGER AS $$
DECLARE
    feedback_date DATE;
    positive_count INTEGER;
    negative_count INTEGER;
    total_count INTEGER;
    avg_rating NUMERIC(3,2);
BEGIN
    feedback_date := DATE(NEW.created_at);
    
    -- Calculate metrics for the day
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE feedback_score >= 4),
        COUNT(*) FILTER (WHERE feedback_score <= 2),
        AVG(feedback_score)
    INTO 
        total_count,
        positive_count,
        negative_count,
        avg_rating
    FROM public.chat_feedback
    WHERE DATE(created_at) = feedback_date;
    
    -- Insert or update metrics for the day
    INSERT INTO public.feedback_metrics (
        date, 
        total_feedback_count, 
        positive_feedback_count, 
        negative_feedback_count, 
        average_rating
    )
    VALUES (
        feedback_date,
        total_count,
        positive_count,
        negative_count,
        avg_rating
    )
    ON CONFLICT (date) 
    DO UPDATE SET
        total_feedback_count = EXCLUDED.total_feedback_count,
        positive_feedback_count = EXCLUDED.positive_feedback_count,
        negative_feedback_count = EXCLUDED.negative_feedback_count,
        average_rating = EXCLUDED.average_rating,
        updated_at = timezone('utc'::text, now());
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating metrics
DROP TRIGGER IF EXISTS trigger_update_feedback_metrics ON public.chat_feedback;
CREATE TRIGGER trigger_update_feedback_metrics
AFTER INSERT OR UPDATE ON public.chat_feedback
FOR EACH ROW
EXECUTE FUNCTION update_feedback_metrics();

-- Enable Row Level Security
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reasoning_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_metrics ENABLE ROW LEVEL SECURITY;

-- Create policies for chats table
CREATE POLICY "Users can view their own chats"
    ON public.chats
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own chats"
    ON public.chats
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create policies for reasoning_steps table
CREATE POLICY "Users can view their own reasoning steps"
    ON public.reasoning_steps
    FOR SELECT
    USING (
        chat_id IN (
            SELECT id FROM public.chats WHERE user_id = auth.uid()
        )
    );

-- Create policies for chat_feedback table
CREATE POLICY "Users can view their own feedback"
    ON public.chat_feedback
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own feedback"
    ON public.chat_feedback
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Create policies for feedback_metrics table
CREATE POLICY "Only admins can view feedback metrics"
    ON public.feedback_metrics
    FOR SELECT
    USING (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM auth.users
        WHERE auth.users.id = auth.uid() AND auth.users.role = 'admin'
    ));

-- Add comments for documentation
COMMENT ON TABLE public.chats IS 'Stores chat messages for the climate assistant';
COMMENT ON TABLE public.reasoning_steps IS 'Stores reasoning steps for RLHF';
COMMENT ON TABLE public.chat_feedback IS 'Stores user feedback on chat messages';
COMMENT ON TABLE public.feedback_metrics IS 'Stores aggregated feedback metrics by date';
