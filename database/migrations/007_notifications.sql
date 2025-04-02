-- Migration: Notifications
-- Created: 2024-07-15

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Notifications table for user alerts and messages
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('info', 'success', 'warning', 'error', 'job', 'training', 'system')),
    link TEXT,
    read BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);

-- Function to set updated_at timestamp automatically
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update the updated_at column
CREATE TRIGGER update_notification_updated_at
BEFORE UPDATE ON notifications
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Add RLS policies for security
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Allow users to see only their own notifications
CREATE POLICY notifications_select_policy
ON notifications
FOR SELECT
USING (auth.uid() = user_id);

-- Allow users to update only their own notifications (for marking as read)
CREATE POLICY notifications_update_policy
ON notifications
FOR UPDATE
USING (auth.uid() = user_id);

-- Allow users to delete only their own notifications
CREATE POLICY notifications_delete_policy
ON notifications
FOR DELETE
USING (auth.uid() = user_id);

-- Only service role and system can insert notifications
CREATE POLICY notifications_insert_policy
ON notifications
FOR INSERT
WITH CHECK (
    auth.role() = 'service_role' OR 
    auth.role() = 'authenticated'
);

-- Add function to create system notifications for new opportunities
CREATE OR REPLACE FUNCTION create_opportunity_notification()
RETURNS TRIGGER AS $$
DECLARE
    matching_users CURSOR FOR
        SELECT u.id
        FROM user_profiles u
        WHERE 
            -- Match based on skills if present
            (NEW.required_skills IS NULL OR 
             u.skills && NEW.required_skills) AND
            -- Match based on location if present
            (NEW.location IS NULL OR 
             u.location = NEW.location OR
             u.gateway_city = NEW.location);
    user_id TEXT;
BEGIN
    -- For each matching user, create a notification
    FOR user_id IN matching_users LOOP
        INSERT INTO notifications (
            user_id,
            title,
            message,
            type,
            link,
            metadata
        ) VALUES (
            user_id,
            CASE 
                WHEN NEW.table_name = 'job_opportunities' THEN 'New Job Opportunity'
                WHEN NEW.table_name = 'training_programs' THEN 'New Training Program'
                ELSE 'New Opportunity'
            END,
            CASE 
                WHEN NEW.table_name = 'job_opportunities' THEN 'A new job matching your profile has been posted: ' || NEW.title
                WHEN NEW.table_name = 'training_programs' THEN 'A new training program matching your interests is available: ' || NEW.title
                ELSE 'A new opportunity matching your profile is available'
            END,
            CASE 
                WHEN NEW.table_name = 'job_opportunities' THEN 'job'
                WHEN NEW.table_name = 'training_programs' THEN 'training'
                ELSE 'info'
            END,
            '/opportunities/' || NEW.id,
            jsonb_build_object(
                'opportunity_id', NEW.id,
                'opportunity_type', NEW.table_name,
                'title', NEW.title,
                'location', NEW.location
            )
        );
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Comment on table and columns for documentation
COMMENT ON TABLE notifications IS 'Stores user notifications for alerts, messages, and updates';
COMMENT ON COLUMN notifications.id IS 'Unique identifier for the notification';
COMMENT ON COLUMN notifications.user_id IS 'The user ID this notification belongs to';
COMMENT ON COLUMN notifications.title IS 'Short title for the notification';
COMMENT ON COLUMN notifications.message IS 'Detailed message content';
COMMENT ON COLUMN notifications.type IS 'Type of notification (info, success, warning, error, job, training, system)';
COMMENT ON COLUMN notifications.link IS 'Optional link URL for the notification to direct users';
COMMENT ON COLUMN notifications.read IS 'Whether the notification has been read by the user';
COMMENT ON COLUMN notifications.metadata IS 'Additional JSON data related to the notification';
COMMENT ON COLUMN notifications.created_at IS 'When the notification was created';
COMMENT ON COLUMN notifications.updated_at IS 'When the notification was last updated'; 