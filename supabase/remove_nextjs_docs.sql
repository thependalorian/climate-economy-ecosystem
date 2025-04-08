-- Remove NextJS framework-related rows from framework_docs table
-- This script will delete rows containing NextJS-related keywords and vacuum the table

-- First, let's check the current size of the framework_docs table
SELECT pg_size_pretty(pg_total_relation_size('framework_docs')) AS framework_docs_size;

-- Create a temporary table to store the IDs of rows to delete
CREATE TEMP TABLE nextjs_docs_to_delete AS
SELECT id 
FROM framework_docs
WHERE 
    content ILIKE '%next.js%' OR
    content ILIKE '%nextjs%' OR
    content ILIKE '%next-js%' OR
    content ILIKE '%vercel%' OR
    content ILIKE '%react server component%' OR
    content ILIKE '%app router%' OR
    content ILIKE '%pages router%' OR
    content ILIKE '%next/router%' OR
    content ILIKE '%next/link%' OR
    content ILIKE '%next/image%' OR
    content ILIKE '%next/head%' OR
    content ILIKE '%next/script%' OR
    content ILIKE '%next/font%' OR
    content ILIKE '%next/dynamic%' OR
    content ILIKE '%getStaticProps%' OR
    content ILIKE '%getServerSideProps%' OR
    content ILIKE '%getInitialProps%' OR
    content ILIKE '%useRouter%' OR
    content ILIKE '%createNextContext%';

-- Count how many rows will be deleted
SELECT COUNT(*) AS rows_to_delete FROM nextjs_docs_to_delete;

-- Delete the rows
DELETE FROM framework_docs
WHERE id IN (SELECT id FROM nextjs_docs_to_delete);

-- Check how many rows were deleted
SELECT 'Deleted ' || COUNT(*) || ' NextJS framework-related rows' AS result 
FROM nextjs_docs_to_delete;

-- Check the new size of the framework_docs table
SELECT pg_size_pretty(pg_total_relation_size('framework_docs')) AS new_framework_docs_size;

-- Run VACUUM to reclaim space
VACUUM FULL framework_docs;

-- Check the final size after VACUUM
SELECT pg_size_pretty(pg_total_relation_size('framework_docs')) AS final_framework_docs_size;

-- Check the total database size
SELECT pg_size_pretty(sum(pg_database_size(pg_database.datname))) AS total_database_size
FROM pg_database;

-- If the database is in read-only mode, you can disable it with these commands:
-- set session characteristics as transaction read write;
-- vacuum;
-- set default_transaction_read_only = 'off';

-- Drop the temporary table
DROP TABLE nextjs_docs_to_delete;
