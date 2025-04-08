#!/usr/bin/env python3
"""
Generate SQL for RLHF Tables

This script generates SQL that can be run in the Supabase dashboard to create the necessary tables for RLHF.
"""

import os
import sys

# SQL to create the RLHF tables
SQL_TEMPLATE = """
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create chats table
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    conversation_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    tokens_used INTEGER DEFAULT 0
);

-- Create reasoning_steps table
CREATE TABLE IF NOT EXISTS public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID REFERENCES public.chats(id) ON DELETE CASCADE,
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_feedback table
CREATE TABLE IF NOT EXISTS public.chat_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    message_id UUID REFERENCES public.chats(id),
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down', 'rating', 'comment')),
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create feedback_metrics table
CREATE TABLE IF NOT EXISTS public.feedback_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    total_feedback_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    average_rating NUMERIC(3,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON public.chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_conversation_id ON public.chats(conversation_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_steps_chat_id ON public.reasoning_steps(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_user_id ON public.chat_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_message_id ON public.chat_feedback(message_id);
CREATE INDEX IF NOT EXISTS idx_feedback_metrics_date ON public.feedback_metrics(date);

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
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating metrics
DROP TRIGGER IF EXISTS trigger_update_feedback_metrics ON public.chat_feedback;
CREATE TRIGGER trigger_update_feedback_metrics
AFTER INSERT OR UPDATE ON public.chat_feedback
FOR EACH ROW
EXECUTE FUNCTION update_feedback_metrics();
"""

def main():
    """Generate SQL and save it to a file"""
    # Create output directory if it doesn't exist
    os.makedirs("sql", exist_ok=True)
    
    # Save SQL to file
    sql_file = "sql/create_rlhf_tables.sql"
    with open(sql_file, "w") as f:
        f.write(SQL_TEMPLATE)
    
    print(f"SQL generated and saved to {sql_file}")
    print("To create the tables:")
    print("1. Log in to your Supabase dashboard")
    print("2. Go to the SQL Editor")
    print("3. Copy and paste the contents of the SQL file")
    print("4. Execute the SQL")

if __name__ == "__main__":
    main()
