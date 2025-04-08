-- Create feature votes table
create table if not exists public.feature_votes (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users not null,
    feature text not null,
    voted_at timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    unique(user_id, feature)
);

-- Add RLS policies
alter table public.feature_votes enable row level security;

-- Allow authenticated users to vote
create policy "Users can vote for features"
    on public.feature_votes
    for insert
    to authenticated
    with check (auth.uid() = user_id);

-- Users can view their own votes
create policy "Users can view their own votes"
    on public.feature_votes
    for select
    to authenticated
    using (auth.uid() = user_id);

-- Create index for faster lookups
create index feature_votes_user_id_feature_idx on public.feature_votes(user_id, feature);

-- Grant access to authenticated users
grant select, insert on public.feature_votes to authenticated; 