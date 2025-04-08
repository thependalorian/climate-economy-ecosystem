-- User personas table
create table if not exists public.user_personas (
    id uuid default gen_random_uuid() primary key,
    name text not null,
    description text,
    min_profile_strength integer not null,
    min_engagement_score integer not null,
    min_skill_match integer not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert default personas
insert into public.user_personas (name, description, min_profile_strength, min_engagement_score, min_skill_match) values
    ('veteran', 'Military veterans transitioning to clean energy', 70, 60, 65),
    ('international', 'International professionals in clean energy', 80, 70, 75),
    ('student', 'Students and recent graduates', 60, 50, 55),
    ('career_transition', 'Professionals transitioning to clean energy', 75, 65, 70),
    ('experienced', 'Experienced clean energy professionals', 85, 75, 80);

-- User engagement scoring table
create table if not exists public.user_engagement_scores (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users not null,
    profile_strength integer not null default 0,
    engagement_score integer not null default 0,
    skill_match_score integer not null default 0,
    persona_id uuid references public.user_personas,
    last_calculated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(user_id)
);

-- Engagement activities table
create table if not exists public.engagement_activities (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users not null,
    activity_type text not null,
    points integer not null,
    metadata jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Add RLS policies
alter table public.user_personas enable row level security;
alter table public.user_engagement_scores enable row level security;
alter table public.engagement_activities enable row level security;

-- RLS policies
create policy "Users can view their own engagement scores"
    on public.user_engagement_scores
    for select
    to authenticated
    using (auth.uid() = user_id);

create policy "Users can view personas"
    on public.user_personas
    for select
    to authenticated
    using (true);

create policy "Users can view their own activities"
    on public.engagement_activities
    for select
    to authenticated
    using (auth.uid() = user_id);

-- Create indexes
create index user_engagement_scores_user_id_idx on public.user_engagement_scores(user_id);
create index engagement_activities_user_id_idx on public.engagement_activities(user_id);

-- Grant access
grant select on public.user_personas to authenticated;
grant select on public.user_engagement_scores to authenticated;
grant select on public.engagement_activities to authenticated;

-- Function to calculate engagement score
create or replace function calculate_engagement_score(user_id uuid)
returns integer as $$
declare
    total_points integer;
begin
    select coalesce(sum(points), 0)
    into total_points
    from public.engagement_activities
    where user_id = $1
    and created_at >= now() - interval '30 days';
    
    -- Normalize score to 0-100 range
    return least(100, greatest(0, total_points / 10));
end;
$$ language plpgsql security definer;

-- Function to check if user meets connection threshold
create or replace function can_connect_to_partners(user_id uuid)
returns boolean as $$
declare
    user_scores record;
    user_persona record;
begin
    -- Get user's scores and persona
    select * into user_scores
    from public.user_engagement_scores
    where user_id = $1;
    
    select * into user_persona
    from public.user_personas
    where id = user_scores.persona_id;
    
    -- Check if user meets all thresholds
    return (
        user_scores.profile_strength >= user_persona.min_profile_strength and
        user_scores.engagement_score >= user_persona.min_engagement_score and
        user_scores.skill_match_score >= user_persona.min_skill_match
    );
end;
$$ language plpgsql security definer; 