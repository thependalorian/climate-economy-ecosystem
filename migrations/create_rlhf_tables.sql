-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    profile_data JSONB DEFAULT '{}'::JSONB,
    preferences JSONB DEFAULT '{}'::JSONB,
    role TEXT DEFAULT 'user'
);

-- Create chats table if it doesn't exist
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    conversation_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    tokens_used INTEGER DEFAULT 0
);

-- Create chat_feedback table if it doesn't exist
CREATE TABLE IF NOT EXISTS chat_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    message_id UUID REFERENCES chats(id),
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down', 'rating', 'comment')),
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create feedback_metrics table if it doesn't exist
CREATE TABLE IF NOT EXISTS feedback_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    total_feedback_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    average_rating NUMERIC(3,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_conversation_id ON chats(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_user_id ON chat_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_message_id ON chat_feedback(message_id);
CREATE INDEX IF NOT EXISTS idx_feedback_metrics_date ON feedback_metrics(date);

-- Create function to update feedback_metrics when new feedback is added
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
    FROM chat_feedback
    WHERE DATE(created_at) = feedback_date;
    
    -- Insert or update metrics for the day
    INSERT INTO feedback_metrics (
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
DROP TRIGGER IF EXISTS trigger_update_feedback_metrics ON chat_feedback;
CREATE TRIGGER trigger_update_feedback_metrics
AFTER INSERT OR UPDATE ON chat_feedback
FOR EACH ROW
EXECUTE FUNCTION update_feedback_metrics();

-- Add RLS policies for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_metrics ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY users_policy ON users
    FOR ALL
    USING (auth.uid() = id);

-- Users can only see their own chats
CREATE POLICY chats_policy ON chats
    FOR ALL
    USING (auth.uid() = user_id);

-- Users can only see their own feedback
CREATE POLICY chat_feedback_policy ON chat_feedback
    FOR ALL
    USING (auth.uid() = user_id);

-- Only admins can see feedback metrics
CREATE POLICY feedback_metrics_policy ON feedback_metrics
    FOR ALL
    USING (auth.role() = 'authenticated' AND EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid() AND users.role = 'admin'
    ));
