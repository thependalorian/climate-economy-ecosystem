-- Migration: Metrics and Monitoring
-- Created: 2024-07-12

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Events tracking table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    user_id UUID,
    metadata JSONB,
    session_id TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for events table
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id);

-- API performance tracking table
CREATE TABLE IF NOT EXISTS api_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint TEXT NOT NULL,
    duration_ms DOUBLE PRECISION NOT NULL,
    status_code INTEGER NOT NULL,
    user_id UUID,
    query_params JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for api_performance table
CREATE INDEX IF NOT EXISTS idx_api_performance_endpoint ON api_performance(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_performance_timestamp ON api_performance(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_performance_status_code ON api_performance(status_code);

-- User satisfaction tracking table
CREATE TABLE IF NOT EXISTS user_satisfaction (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_id TEXT NOT NULL,
    satisfaction_score INTEGER NOT NULL CHECK (satisfaction_score BETWEEN 1 AND 5),
    feedback TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for user_satisfaction table
CREATE INDEX IF NOT EXISTS idx_user_satisfaction_user_id ON user_satisfaction(user_id);
CREATE INDEX IF NOT EXISTS idx_user_satisfaction_timestamp ON user_satisfaction(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_satisfaction_score ON user_satisfaction(satisfaction_score);

-- Performance alerts table
CREATE TABLE IF NOT EXISTS performance_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint TEXT NOT NULL,
    metric TEXT NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    current_value DOUBLE PRECISION NOT NULL,
    severity TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance_alerts table
CREATE INDEX IF NOT EXISTS idx_performance_alerts_endpoint ON performance_alerts(endpoint);
CREATE INDEX IF NOT EXISTS idx_performance_alerts_resolved ON performance_alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_performance_alerts_timestamp ON performance_alerts(timestamp);

-- Session tracking table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id UUID,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    user_agent TEXT,
    ip_address TEXT,
    referrer TEXT,
    pages_viewed INTEGER DEFAULT 0,
    is_mobile BOOLEAN,
    location TEXT
);

-- Create indexes for sessions table
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_is_mobile ON sessions(is_mobile);

-- Function to calculate session duration
CREATE OR REPLACE FUNCTION calculate_session_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically calculate session duration
CREATE TRIGGER calc_session_duration
BEFORE UPDATE ON sessions
FOR EACH ROW
WHEN (OLD.ended_at IS NULL AND NEW.ended_at IS NOT NULL)
EXECUTE FUNCTION calculate_session_duration();

-- Analytics summary table (pre-calculated metrics)
CREATE TABLE IF NOT EXISTS analytics_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    summary_date DATE NOT NULL,
    summary_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index for analytics summaries to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_analytics_summaries_unique 
ON analytics_summaries(summary_date, summary_type, metric_name);

-- Feedback categories lookup table
CREATE TABLE IF NOT EXISTS feedback_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial feedback categories
INSERT INTO feedback_categories (name, description)
VALUES
    ('UI/UX', 'Feedback related to user interface and experience'),
    ('Content', 'Feedback related to content quality and relevance'),
    ('Recommendations', 'Feedback on job and training recommendations'),
    ('Performance', 'Feedback related to system performance and speed'),
    ('General', 'General feedback not fitting other categories')
ON CONFLICT (name) DO NOTHING;

-- Feedback categorization table (for sentiment analysis results)
CREATE TABLE IF NOT EXISTS feedback_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    satisfaction_id UUID REFERENCES user_satisfaction(id),
    sentiment TEXT NOT NULL,
    categories TEXT[] NOT NULL,
    action_items TEXT[],
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to aggregate daily events
CREATE OR REPLACE FUNCTION aggregate_daily_events()
RETURNS VOID AS $$
DECLARE
    current_date DATE := CURRENT_DATE;
BEGIN
    -- Count events by type
    INSERT INTO analytics_summaries (summary_date, summary_type, metric_name, metric_value)
    SELECT 
        DATE(timestamp) AS event_date,
        'daily',
        'event_counts',
        jsonb_object_agg(event_type, count)
    FROM (
        SELECT 
            event_type,
            COUNT(*) AS count
        FROM events
        WHERE DATE(timestamp) = current_date - INTERVAL '1 day'
        GROUP BY event_type
    ) AS event_counts
    ON CONFLICT (summary_date, summary_type, metric_name)
    DO UPDATE SET metric_value = EXCLUDED.metric_value;
    
    -- Count active users
    INSERT INTO analytics_summaries (summary_date, summary_type, metric_name, metric_value)
    SELECT 
        DATE(timestamp) AS event_date,
        'daily',
        'active_users',
        jsonb_build_object(
            'count', COUNT(DISTINCT user_id),
            'is_mobile', jsonb_build_object(
                'true', COUNT(DISTINCT user_id) FILTER (WHERE s.is_mobile = true),
                'false', COUNT(DISTINCT user_id) FILTER (WHERE s.is_mobile = false OR s.is_mobile IS NULL)
            )
        )
    FROM events e
    LEFT JOIN sessions s ON e.session_id = s.id
    WHERE DATE(e.timestamp) = current_date - INTERVAL '1 day'
    AND user_id IS NOT NULL
    ON CONFLICT (summary_date, summary_type, metric_name)
    DO UPDATE SET metric_value = EXCLUDED.metric_value;
    
    -- Average API response time
    INSERT INTO analytics_summaries (summary_date, summary_type, metric_name, metric_value)
    SELECT 
        DATE(timestamp) AS event_date,
        'daily',
        'api_performance',
        jsonb_build_object(
            'avg_duration_ms', ROUND(AVG(duration_ms), 2),
            'total_requests', COUNT(*),
            'error_rate', ROUND(COUNT(*) FILTER (WHERE status_code >= 400)::FLOAT / COUNT(*), 4),
            'by_endpoint', jsonb_object_agg(
                endpoint, 
                jsonb_build_object(
                    'avg_duration_ms', ROUND(AVG(duration_ms), 2),
                    'count', COUNT(*)
                )
            )
        )
    FROM api_performance
    WHERE DATE(timestamp) = current_date - INTERVAL '1 day'
    GROUP BY DATE(timestamp)
    ON CONFLICT (summary_date, summary_type, metric_name)
    DO UPDATE SET metric_value = EXCLUDED.metric_value;
    
    -- User satisfaction metrics
    INSERT INTO analytics_summaries (summary_date, summary_type, metric_name, metric_value)
    SELECT 
        DATE(timestamp) AS event_date,
        'daily',
        'satisfaction',
        jsonb_build_object(
            'avg_score', ROUND(AVG(satisfaction_score), 2),
            'count', COUNT(*),
            'score_distribution', jsonb_build_object(
                '1', COUNT(*) FILTER (WHERE satisfaction_score = 1),
                '2', COUNT(*) FILTER (WHERE satisfaction_score = 2),
                '3', COUNT(*) FILTER (WHERE satisfaction_score = 3),
                '4', COUNT(*) FILTER (WHERE satisfaction_score = 4),
                '5', COUNT(*) FILTER (WHERE satisfaction_score = 5)
            )
        )
    FROM user_satisfaction
    WHERE DATE(timestamp) = current_date - INTERVAL '1 day'
    GROUP BY DATE(timestamp)
    ON CONFLICT (summary_date, summary_type, metric_name)
    DO UPDATE SET metric_value = EXCLUDED.metric_value;
END;
$$ LANGUAGE plpgsql;

-- Create a cron job to run the aggregation daily (if pg_cron extension is available)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pg_cron'
    ) THEN
        PERFORM cron.schedule('0 1 * * *', 'SELECT aggregate_daily_events()');
    END IF;
END
$$; 