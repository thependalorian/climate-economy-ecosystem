import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import OpenAI from 'openai';
import { searchKnowledgeBase } from '@/lib/assistant/tools';
import { getCache, setCache } from '@/lib/redis';

/**
 * API Route for Vector Search
 * Performs semantic search on climate economy knowledge base
 * Uses the assistant's function calling approach
 * Location: /app/api/assistant/search/route.js
 */
export async function GET(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const searchParams = request.nextUrl.searchParams;
    
    // Get search parameters
    const query = searchParams.get('query');
    const type = searchParams.get('type');
    const source = searchParams.get('source');
    const limit = parseInt(searchParams.get('limit') || '10', 10);
    
    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }
    
    // Get user if authenticated for personalization and tracking
    const { data: { user } } = await supabase.auth.getUser();
    
    // Check cache first
    const cacheKey = `search:${query.substring(0, 20)}:${type || 'all'}:${source || 'all'}:${limit}`;
    const cachedResults = await getCache(cacheKey);
    
    if (cachedResults) {
      return NextResponse.json({
        results: cachedResults,
        fromCache: true
      });
    }
    
    // Call the search function from our tools
    const searchResults = await searchKnowledgeBase({
      query,
      filter_type: type,
      filter_source: source,
      limit
    });
    
    // Cache the results for 1 hour
    await setCache(cacheKey, searchResults, 3600);
    
    // Track search for engagement if user is authenticated
    if (user) {
      try {
        // Update user engagement
        const { data: engagement } = await supabase
          .from('user_engagement')
          .select('*')
          .eq('user_id', user.id)
          .single();
        
        if (engagement) {
          await supabase
            .from('user_engagement')
            .update({
              resources_accessed: engagement.resources_accessed + 1,
              updated_at: new Date().toISOString()
            })
            .eq('user_id', user.id);
        } else {
          await supabase
            .from('user_engagement')
            .insert({
              user_id: user.id,
              resources_accessed: 1
            });
        }
      } catch (error) {
        console.error('Error tracking search:', error);
        // Don't fail the request if tracking fails
      }
    }
    
    return NextResponse.json({ results: searchResults });
    
  } catch (error) {
    console.error('Error in search API:', error);
    return NextResponse.json(
      { error: 'Failed to perform search', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * Generate embedding for semantic search
 */
async function generateEmbedding(text) {
  try {
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    const response = await openai.embeddings.create({
      model: "text-embedding-ada-002",
      input: text
    });
    
    return response.data[0].embedding;
  } catch (error) {
    console.error('Error generating embedding:', error);
    throw error;
  }
}

/**
 * Perform vector search using embeddings
 */
async function performVectorSearch(supabase, embedding, type, source) {
  // Set defaults
  const matchThreshold = 0.7;
  const matchCount = 20;
  
  // Build RPC parameters
  const params = {
    query_embedding: embedding,
    match_threshold: matchThreshold,
    match_count: matchCount
  };
  
  // Call match_documents RPC
  const { data, error } = await supabase.rpc('match_documents', params);
  
  if (error) {
    console.error('Error in vector search:', error);
    throw error;
  }
  
  // Process and filter results
  let results = data || [];
  
  // Apply additional filters if specified
  if (type || source) {
    results = results.filter(item => {
      const metadata = item.metadata || {};
      
      // Filter by resource type
      if (type && metadata.resource_type !== type) {
        return false;
      }
      
      // Filter by source
      if (source && metadata.source !== source) {
        return false;
      }
      
      return true;
    });
  }
  
  // Format results
  return results.map(item => ({
    id: item.id,
    title: item.metadata?.title || 'Untitled',
    content: item.content,
    url: item.metadata?.url || null,
    similarity: item.similarity,
    metadata: item.metadata
  }));
}

/**
 * Perform hybrid search (combining vector and text search)
 */
async function performHybridSearch(supabase, query, embedding, type, source) {
  // Vector search results
  const vectorResults = await performVectorSearch(
    supabase,
    embedding,
    type,
    source
  );
  
  // Text search results
  const textSearchQuery = `%${query.toLowerCase()}%`;
  
  // Build query
  let textSearchBuilder = supabase
    .from('documents')
    .select('*')
    .or(`content.ilike.${textSearchQuery},metadata->title.ilike.${textSearchQuery}`);
  
  // Apply additional filters if specified
  if (type) {
    textSearchBuilder = textSearchBuilder.eq('metadata->>resource_type', type);
  }
  
  if (source) {
    textSearchBuilder = textSearchBuilder.eq('metadata->>source', source);
  }
  
  const { data: textResults, error } = await textSearchBuilder.limit(20);
  
  if (error) {
    console.error('Error in text search:', error);
    throw error;
  }
  
  // Format text results
  const formattedTextResults = (textResults || []).map(item => ({
    id: item.id,
    title: item.metadata?.title || 'Untitled',
    content: item.content,
    url: item.metadata?.url || null,
    similarity: 0.5, // Default similarity for text results
    metadata: item.metadata,
    source: 'text'
  }));
  
  // Combine results, removing duplicates
  const combinedResults = [...vectorResults];
  
  for (const textResult of formattedTextResults) {
    if (!combinedResults.some(item => item.id === textResult.id)) {
      combinedResults.push(textResult);
    }
  }
  
  // Sort by similarity
  return combinedResults.sort((a, b) => b.similarity - a.similarity);
} 