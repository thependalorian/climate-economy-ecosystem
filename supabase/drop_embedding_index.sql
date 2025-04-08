-- Drop Embedding Index to Reduce Database Size
-- This script will drop the framework_docs_embedding_idx index to reduce database size

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

-- Drop the framework_docs_embedding_idx index
DROP INDEX IF EXISTS framework_docs_embedding_idx;

-- Run VACUUM to reclaim space
VACUUM FULL;

-- Check the final database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS final_database_size
FROM pg_database;

-- If the database is in read-only mode, you can disable it with these commands:
set session characteristics as transaction read write;
vacuum;
set default_transaction_read_only = 'off';
