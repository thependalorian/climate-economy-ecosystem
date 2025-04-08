-- Create connection thresholds table
create table if not exists public.connection_thresholds (
    id uuid default gen_random_uuid() primary key,
    persona_type text not null,
    profile_strength_min integer not null,
    engagement_score_min integer not null,
    match_score_min integer not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(persona_type)
);

-- Add RLS policies
alter table public.connection_thresholds enable row level security;

-- Allow authenticated users to view thresholds
create policy "Users can view connection thresholds"
    on public.connection_thresholds
    for select
    to authenticated;

-- Insert default thresholds for different persona types
INSERT INTO public.connection_thresholds 
(persona_type, profile_strength_min, engagement_score_min, match_score_min)
VALUES
-- Veterans have a lower threshold due to valuable transferable skills
('veteran', 60, 40, 70),
-- International professionals need more verification of credentials
('international', 80, 50, 75),
-- Students need more engagement to demonstrate commitment
('student', 70, 60, 70),
-- EJ communities have a lower threshold to increase participation
('ej', 60, 30, 65),
-- Reentry workforce needs more profile data to match effectively
('reentry', 75, 45, 70),
-- Default threshold for other users
('default', 70, 50, 75);

-- Grant access to authenticated users
grant select on public.connection_thresholds to authenticated; 