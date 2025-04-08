-- Reduce Vector Embeddings Size
-- This script will reduce the size of vector embeddings in the database

-- First, let's check the current database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS total_database_size
FROM pg_database;

-- Check the size of the framework_docs table and its embedding index
SELECT 
    'framework_docs' AS table_name,
    pg_size_pretty(pg_relation_size('framework_docs')) AS table_size,
    pg_size_pretty(pg_relation_size('framework_docs_embedding_idx')) AS embedding_idx_size,
    pg_size_pretty(pg_total_relation_size('framework_docs')) AS total_size
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'framework_docs'
);

-- Check the size of the strategy_videos table and its embedding index
SELECT 
    'strategy_videos' AS table_name,
    pg_size_pretty(pg_relation_size('strategy_videos')) AS table_size,
    pg_size_pretty(pg_relation_size('strategy_videos_embedding_idx')) AS embedding_idx_size,
    pg_size_pretty(pg_total_relation_size('strategy_videos')) AS total_size
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'strategy_videos'
);

-- Check for other tables with embedding columns or indexes
SELECT 
    table_name,
    column_name
FROM information_schema.columns
WHERE column_name LIKE '%embedding%'
  AND table_schema = 'public';

SELECT 
    indexname,
    tablename,
    pg_size_pretty(pg_relation_size(schemaname || '.' || indexname)) AS index_size
FROM pg_indexes
WHERE indexname LIKE '%embedding%'
  AND schemaname = 'public';

-- OPTION 1: Drop embedding indexes (keeps the data but removes the indexes)
-- This is less destructive as it keeps the embedding data but removes the indexes

-- Drop framework_docs_embedding_idx if it exists
DROP INDEX IF EXISTS framework_docs_embedding_idx;

-- Drop strategy_videos_embedding_idx if it exists
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

-- OPTION 2: Remove embedding columns (more destructive, removes the actual embedding data)
-- Uncomment these if you want to completely remove the embedding columns

-- ALTER TABLE framework_docs DROP COLUMN IF EXISTS embedding;
-- ALTER TABLE strategy_videos DROP COLUMN IF EXISTS embedding;

-- Remove embedding columns from any other tables
-- DO $$
-- DECLARE
--     table_rec record;
-- BEGIN
--     FOR table_rec IN 
--         SELECT table_name, column_name
--         FROM information_schema.columns
--         WHERE column_name LIKE '%embedding%'
--           AND table_schema = 'public'
--     LOOP
--         EXECUTE 'ALTER TABLE ' || table_rec.table_name || ' DROP COLUMN IF EXISTS ' || table_rec.column_name;
--         RAISE NOTICE 'Dropped column: %.%', table_rec.table_name, table_rec.column_name;
--     END LOOP;
-- END $$;

-- OPTION 3: Delete specific framework_docs rows (e.g., by framework type)
-- This is a more targeted approach to remove specific content

-- Delete React framework docs (if you're focusing on NextJS, you might want to keep React)
-- DELETE FROM framework_docs WHERE content ILIKE '%react%' AND content NOT ILIKE '%nextjs%' AND content NOT ILIKE '%next.js%';

-- Delete other framework docs that might not be needed
DELETE FROM framework_docs WHERE content ILIKE '%angular%';
DELETE FROM framework_docs WHERE content ILIKE '%vue%';
DELETE FROM framework_docs WHERE content ILIKE '%svelte%';
DELETE FROM framework_docs WHERE content ILIKE '%ember%';
DELETE FROM framework_docs WHERE content ILIKE '%backbone%';
DELETE FROM framework_docs WHERE content ILIKE '%jquery%';
DELETE FROM framework_docs WHERE content ILIKE '%meteor%';
DELETE FROM framework_docs WHERE content ILIKE '%polymer%';
DELETE FROM framework_docs WHERE content ILIKE '%knockout%';
DELETE FROM framework_docs WHERE content ILIKE '%aurelia%';

-- Run VACUUM to reclaim space
VACUUM FULL;

-- Check the final database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS final_database_size
FROM pg_database;

-- If the database is in read-only mode, you can disable it with these commands:
-- set session characteristics as transaction read write;
-- vacuum;
-- set default_transaction_read_only = 'off';
