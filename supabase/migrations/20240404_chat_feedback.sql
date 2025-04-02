-- Create chat feedback table
create table if not exists public.chat_feedback (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users not null,
    message_id text not null,
    feedback_type text not null,
    feedback_details text,
    feedback_time timestamp with time zone default timezone('utc'::text, now()) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Add index for faster lookup by user
create index if not exists chat_feedback_user_id_idx on public.chat_feedback (user_id);

-- Add index for faster lookup by message
create index if not exists chat_feedback_message_id_idx on public.chat_feedback (message_id);

-- Add RLS policies
alter table public.chat_feedback enable row level security;

-- Allow authenticated users to insert and view their own feedback
create policy "Users can insert feedback"
    on public.chat_feedback
    for insert
    to authenticated
    with check (auth.uid() = user_id);

create policy "Users can view their own feedback"
    on public.chat_feedback
    for select
    to authenticated
    using (auth.uid() = user_id);

-- Grant access to authenticated users
grant insert, select on public.chat_feedback to authenticated; 