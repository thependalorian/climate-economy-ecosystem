-- Remove strategy tables to reduce database size
-- This script will identify and delete strategy-related tables and vacuum the database

-- First, let's check the current database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS total_database_size
FROM pg_database;

-- Check if strategy_videos table exists and its size
SELECT 
    pg_size_pretty(pg_total_relation_size('strategy_videos')) AS strategy_videos_size
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'strategy_videos'
);

-- Check if strategy_videos_embedding_idx exists and its size
SELECT 
    pg_size_pretty(pg_relation_size('strategy_videos_embedding_idx')) AS strategy_videos_embedding_idx_size
WHERE EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public' AND indexname = 'strategy_videos_embedding_idx'
);

-- Check for other strategy-related tables
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size('public.' || table_name)) AS table_size
FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE '%strategy%';

-- Backup strategy data before deletion (optional)
-- CREATE TABLE strategy_videos_backup AS SELECT * FROM strategy_videos;

-- Drop strategy_videos_embedding_idx if it exists
DROP INDEX IF EXISTS strategy_videos_embedding_idx;

-- Drop strategy_videos table if it exists
DROP TABLE IF EXISTS strategy_videos;

-- Check for other strategy-related tables and drop them
DO $$
DECLARE
    strategy_table text;
BEGIN
    FOR strategy_table IN 
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE '%strategy%'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || strategy_table || ' CASCADE';
        RAISE NOTICE 'Dropped table: %', strategy_table;
    END LOOP;
END $$;

-- Run VACUUM to reclaim space
VACUUM FULL;

-- Check the final database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS final_database_size
FROM pg_database;

-- If the database is in read-only mode, you can disable it with these commands:
-- set session characteristics as transaction read write;
-- vacuum;
-- set default_transaction_read_only = 'off';
