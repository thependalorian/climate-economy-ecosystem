-- Create user engagement metrics table
create table if not exists public.user_engagement (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users not null,
    recommendations_count integer default 0 not null,
    recommendations_clicked integer default 0 not null,
    resources_accessed integer default 0 not null,
    connections_count integer default 0 not null,
    connection_requests integer default 0 not null,
    profile_updates integer default 0 not null,
    logins_count integer default 0 not null,
    satisfaction_score integer default 0 not null,
    engagement_score integer default 0 not null,
    last_active timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(user_id)
);

-- Add RLS policies
alter table public.user_engagement enable row level security;

-- Allow authenticated users to view their own engagement metrics
create policy "Users can view their own engagement metrics"
    on public.user_engagement
    for select
    to authenticated
    using (auth.uid() = user_id);

-- Insert a trigger function to calculate engagement score
create or replace function calculate_engagement_score()
returns trigger as $$
begin
    -- Calculate engagement score based on various metrics
    -- Formula: weighting different activities by importance
    new.engagement_score := 
        (new.logins_count * 2) + 
        (new.recommendations_clicked * 3) + 
        (new.resources_accessed * 5) + 
        (new.profile_updates * 10) + 
        (new.connection_requests * 4) +
        (new.satisfaction_score * 3);
        
    -- Normalize to a 0-100 scale with diminishing returns
    new.engagement_score := least(100, greatest(0, 
        case 
            when new.engagement_score > 500 then 100
            when new.engagement_score > 400 then 90 + ((new.engagement_score - 400) / 10)
            when new.engagement_score > 300 then 80 + ((new.engagement_score - 300) / 10)
            when new.engagement_score > 200 then 70 + ((new.engagement_score - 200) / 10)
            when new.engagement_score > 100 then 50 + ((new.engagement_score - 100) / 5)
            when new.engagement_score > 50 then 25 + ((new.engagement_score - 50) / 2)
            else new.engagement_score / 2
        end
    ));
    
    -- Update last_active timestamp
    new.last_active := now();
    
    return new;
end;
$$ language plpgsql;

-- Attach trigger to the table
create trigger update_engagement_score
before insert or update on public.user_engagement
for each row execute function calculate_engagement_score();

-- Grant access to authenticated users
grant select on public.user_engagement to authenticated; 