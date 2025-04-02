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