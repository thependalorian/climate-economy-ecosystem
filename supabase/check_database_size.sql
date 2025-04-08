-- Check database size and largest tables/indexes
-- This script will show the current database size and identify the largest tables and indexes

-- Check the current database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS total_database_size
FROM pg_database;

-- Check the size of each database
SELECT 
    datname AS database_name,
    pg_size_pretty(pg_database_size(datname)) AS database_size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- Check the size of each table (including indexes)
SELECT 
    table_schema || '.' || table_name AS table_full_name,
    pg_size_pretty(pg_total_relation_size(table_schema || '.' || table_name)) AS total_size,
    pg_size_pretty(pg_relation_size(table_schema || '.' || table_name)) AS table_size,
    pg_size_pretty(pg_total_relation_size(table_schema || '.' || table_name) - pg_relation_size(table_schema || '.' || table_name)) AS index_size
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
  AND table_schema NOT LIKE 'pg_toast%'
  AND table_type = 'BASE TABLE'
ORDER BY pg_total_relation_size(table_schema || '.' || table_name) DESC
LIMIT 20;

-- Check the size of each index
SELECT
    schemaname || '.' || tablename AS table_name,
    indexname AS index_name,
    pg_size_pretty(pg_relation_size(schemaname || '.' || indexname)) AS index_size
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(schemaname || '.' || indexname) DESC
LIMIT 20;

-- Check the size of the framework_docs table and its indexes
SELECT 
    'framework_docs' AS table_name,
    pg_size_pretty(pg_relation_size('framework_docs')) AS table_size,
    pg_size_pretty(pg_total_relation_size('framework_docs') - pg_relation_size('framework_docs')) AS index_size,
    pg_size_pretty(pg_total_relation_size('framework_docs')) AS total_size
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'framework_docs'
);

-- Check the size of the framework_docs_embedding_idx index
SELECT 
    'framework_docs_embedding_idx' AS index_name,
    pg_size_pretty(pg_relation_size('framework_docs_embedding_idx')) AS index_size
WHERE EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE schemaname = 'public' AND indexname = 'framework_docs_embedding_idx'
);

-- Check the row count of the framework_docs table
SELECT 
    COUNT(*) AS row_count
FROM framework_docs
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'framework_docs'
);

-- Check the WAL size
SELECT pg_size_pretty(sum(size)) as wal_size from pg_ls_waldir();

-- Check disk usage distribution
SELECT
    pg_size_pretty(pg_database_size(current_database())) AS database_size,
    pg_size_pretty((SELECT sum(size) FROM pg_ls_waldir())) AS wal_size,
    pg_size_pretty(
        (SELECT sum(pg_total_relation_size(oid)) FROM pg_class WHERE relkind = 'r' AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'pg_catalog'))
    ) AS system_size;
