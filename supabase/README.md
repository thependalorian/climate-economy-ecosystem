# Climate Economy Ecosystem Database Schema

This directory contains the database schema for the Climate Economy Ecosystem. The schema is defined in SQL and is designed to be used with Supabase.

## Overview

The database schema includes tables for:

- User profiles and profile enrichment
- Resumes and resume analysis
- Job recommendations and skill gaps
- Training paths
- Chat sessions and messages
- Feedback collection for RLHF
- User engagement tracking
- Feature voting

## Files

- `schema.sql`: Consolidated schema file that includes all tables, indexes, and policies
- `migrations/`: Directory containing individual migration files

## Schema Structure

### User Data

- `profiles`: Basic user profile information
- `profile_enrichment`: Additional user profile data including social links and skills
- `resumes`: User-uploaded resume files
- `resume_analysis`: Analysis of user resumes including skills, education, and work history

### Job and Skills Data

- `job_recommendations`: Job recommendations for users
- `skill_gaps`: Identified skill gaps for users
- `training_paths`: Recommended training paths for users

### Chat and Feedback

- `chats`: Chat sessions
- `chat_messages`: Individual chat messages
- `chat_feedback`: User feedback on chat messages
- `reasoning_steps`: Reasoning steps for RLHF

### Engagement and Analytics

- `user_engagement`: User engagement metrics
- `feature_votes`: User votes on features
- `connection_thresholds`: Thresholds for connections between users and content
- `memories`: Long-term memory storage for agents

## Row-Level Security (RLS)

The schema includes Row-Level Security policies to ensure that users can only access their own data. Each table has appropriate RLS policies defined.

## Indexes

The schema includes indexes for performance optimization, including:

- Standard B-tree indexes for foreign keys and frequently queried columns
- Vector indexes for embeddings using pgvector

## How to Use

### Initialize a New Database

To initialize a new database with this schema:

1. Create a new Supabase project
2. Run the `schema.sql` file in the SQL Editor

```sql
-- Run the consolidated schema
\i schema.sql
```

### Apply Migrations

If you need to apply individual migrations:

1. Navigate to the SQL Editor in Supabase
2. Run each migration file in order

```sql
-- Run a specific migration
\i migrations/20240402_initial_schema.sql
```

## RLHF Integration

The schema includes tables specifically designed for Reinforcement Learning from Human Feedback (RLHF):

- `reasoning_steps`: Stores individual steps in the reasoning process
- `chat_feedback`: Stores feedback on chat messages and reasoning steps

These tables are used by the RLHF module to collect feedback and improve the agent responses over time.

## Security Considerations

- All tables have Row-Level Security (RLS) policies
- Users can only access their own data
- Service roles have full access for backend operations

## Maintenance

To add new tables or modify existing ones:

1. Create a new migration file in the `migrations/` directory
2. Apply the migration to your database
3. Update the `schema.sql` file to include the changes
