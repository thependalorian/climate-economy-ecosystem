-- Drop All Embedding Indexes to Reduce Database Size
-- This script will drop all embedding indexes to reduce database size

-- First, let's check the current database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS total_database_size
FROM pg_database;

-- Check the size of the framework_docs_embedding_idx index
SELECT 
    'framework_docs_embedding_idx' AS index_name,
    pg_size_pretty(pg_relation_size('framework_docs_embedding_idx')) AS index_size
WHERE EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public' AND indexname = 'framework_docs_embedding_idx'
);

-- Check the size of the strategy_videos_embedding_idx index
SELECT 
    'strategy_videos_embedding_idx' AS index_name,
    pg_size_pretty(pg_relation_size('strategy_videos_embedding_idx')) AS index_size
WHERE EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public' AND indexname = 'strategy_videos_embedding_idx'
);

-- List all embedding indexes
SELECT 
    indexname,
    tablename,
    pg_size_pretty(pg_relation_size(schemaname || '.' || indexname)) AS index_size
FROM pg_indexes
WHERE indexname LIKE '%embedding%'
  AND schemaname = 'public';

-- Drop the framework_docs_embedding_idx index
DROP INDEX IF EXISTS framework_docs_embedding_idx;

-- Drop the strategy_videos_embedding_idx index
DROP INDEX IF EXISTS strategy_videos_embedding_idx;

-- Drop any other embedding indexes
DO $$
DECLARE
    embedding_index text;
BEGIN
    FOR embedding_index IN 
        SELECT indexname
        FROM pg_indexes
        WHERE indexname LIKE '%embedding%'
          AND schemaname = 'public'
    LOOP
        EXECUTE 'DROP INDEX IF EXISTS ' || embedding_index;
        RAISE NOTICE 'Dropped index: %', embedding_index;
    END LOOP;
END $$;

-- Run VACUUM to reclaim space
VACUUM FULL;

-- Check the final database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS final_database_size
FROM pg_database;

-- Disable read-only mode
set session characteristics as transaction read write;
vacuum;
set default_transaction_read_only = 'off';
