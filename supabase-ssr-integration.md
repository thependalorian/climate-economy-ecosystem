# Supabase SSR Integration Guide

This guide explains how Supabase has been integrated with Next.js using Server-Side Rendering (SSR) for enhanced security, performance, and developer experience.

## Overview

Our implementation leverages Supabase's Auth Helpers for Next.js to securely handle sessions and data fetching on both the client and server side. This approach provides:

1. **Enhanced security** - API keys and tokens remain on the server
2. **Improved performance** - Data is pre-fetched on the server
3. **Better user experience** - Reduced loading states and flashes of unauthenticated content
4. **Type safety** - TypeScript integration throughout the codebase

## Implementation Architecture

### Core Files

The implementation consists of several key files:

| File | Purpose |
|------|---------|
| [`lib/supabase-server.js`](../lib/supabase-server.js) | Server-side Supabase client creation and utility functions |
| [`lib/supabase-client.js`](../lib/supabase-client.js) | Client-side Supabase client creation and utility functions |
| [`middleware.js`](../middleware.js) | Route protection and session refreshing |
| [`app/layout.jsx`](../app/layout.jsx) | Root layout with Provider configuration |

### Data Ingestion

For our data ingestion pipeline, we use a direct HTTP approach to Supabase rather than the JavaScript client. This provides:

1. **Cross-language compatibility** - Works with Python scripts for data ingestion
2. **Direct API access** - Bypasses client libraries for more control
3. **Robust error handling** - Custom retry and rate limiting logic

The data ingestion process:

1. Processes document files (PDF, Markdown) from the `/docs` directory
2. Generates embeddings using OpenAI's embedding model
3. Stores content and metadata in Supabase tables with proper indexing
4. Implements duplicate detection to avoid re-processing the same content

Key ingestion files:

| File | Purpose |
|------|---------|
| [`tools/data_ingestion.py`](../tools/data_ingestion.py) | Main ingestion script for documents |
| [`tools/test_supabase.py`](../tools/test_supabase.py) | Test connectivity to Supabase |

### Authentication Flow

1. **Session Management**:
   - Sessions are stored in cookies using the `createServerComponentClient` and `createClientComponentClient` from `@supabase/auth-helpers-nextjs`
   - The middleware automatically refreshes sessions on each request

2. **Route Protection**:
   - Protected routes (dashboard, profile, etc.) are defined in the middleware
   - Unauthenticated users are redirected to the login page with a redirect URL

3. **Server-Side Data Fetching**:
   - Server components use `createServerSupabaseClient()` to fetch data
   - This creates a Supabase client with proper cookie handling

## Usage Examples

### Server Component

```jsx
// Example server component
import { createServerSupabaseClient } from '@/lib/supabase-server';

export default async function Dashboard() {
  // Create Supabase client
  const supabase = createServerSupabaseClient();
  
  // Get the current user
  const { data: { user } } = await supabase.auth.getUser();
  
  // Redirect if not authenticated
  if (!user) {
    redirect('/login?redirect=/dashboard');
  }
  
  // Fetch data from Supabase
  const { data: memories } = await supabase
    .from('climate_memories')
    .select('*')
    .limit(5);
  
  return (
    <div>
      <h1>Welcome, {user.email}</h1>
      <MemoryList memories={memories} />
    </div>
  );
}
```

### Client Component

```jsx
'use client';

import { useState, useEffect } from 'react';
import { createClientSupabaseClient } from '@/lib/supabase-client';

export default function MemorySearchForm() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const supabase = createClientSupabaseClient();
  
  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const { data, error } = await supabase.rpc('search_memories', {
        query_text: query
      });
      
      if (error) throw error;
      setResults(data || []);
    } catch (error) {
      console.error('Error searching memories:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <form onSubmit={handleSearch}>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search climate knowledge..."
          className="input input-bordered w-full"
        />
        <button 
          type="submit"
          className="btn btn-primary mt-2"
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      
      <div className="mt-4">
        {results.map(result => (
          <div key={result.id} className="card bg-base-100 shadow-md p-4 mb-3">
            <h3 className="font-semibold">{result.metadata?.file_name || 'Content'}</h3>
            <p>{result.content.substring(0, 200)}...</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Database Schema

Our Supabase database includes the following key tables:

- `climate_memories` - Stores document content with embeddings for semantic search
- `companies` - Information about clean energy companies
- `sectors` - Clean energy sector categories
- `training_programs` - Educational and training programs
- `job_opportunities` - Career opportunities in the climate economy

## Vector Search Integration

For semantic search capabilities, we use:

1. **OpenAI Embeddings** - We generate vector embeddings for all document chunks
2. **pgvector Extension** - Enables vector similarity search in Postgres
3. **RPC Functions** - Custom database functions for specialized search

Example vector search function:

```sql
CREATE OR REPLACE FUNCTION search_memories(
  query_text TEXT,
  match_count INT DEFAULT 5
)
RETURNS SETOF climate_memories
LANGUAGE plpgsql
AS $$
DECLARE
  query_embedding vector(1536);
BEGIN
  -- Generate embedding for the query using open ai api
  SELECT embedding INTO query_embedding FROM 
    (SELECT openai_embedding(query_text) AS embedding) AS embeddings;
  
  -- Return matches sorted by similarity
  RETURN QUERY
  SELECT *
  FROM climate_memories
  WHERE embedding IS NOT NULL
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

## Security Considerations

1. **API Keys**
   - The service role key is only used server-side and never exposed to the client
   - The public anon key is used for client-side requests with RLS protection

2. **Authentication**
   - All authentication happens through secure PKCE flows
   - Sessions are stored in HTTP-only cookies
   - The middleware refreshes sessions automatically

3. **Data Access**
   - Row Level Security (RLS) policies protect data on the database level
   - Server-side requests use appropriate policies for data access

## ACT Brand Integration

All components follow the ACT brand guidelines with:

1. **Color Palette**
   - Primary: Spring Green (#B2DE26)
   - Dark: Midnight Forest (#001818)
   - Secondary: Moss Green (#394816)
   - Light backgrounds: Seafoam Blue (#E0FFFF) and Sand Gray (#EBE9E1)

2. **Typography**
   - Helvetica for headings with -20 tracking and 32pt leading (for 28pt text)
   - Inter for body text with 1.5 line height

3. **UI Component Library**
   - DaisyUI components are used throughout the application
   - Custom styling is applied to match the ACT brand

## Additional Resources

- [Supabase Auth Helpers Documentation](https://supabase.com/docs/guides/auth/auth-helpers/nextjs)
- [Next.js Server Components Documentation](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [pgvector Documentation](https://github.com/pgvector/pgvector) 