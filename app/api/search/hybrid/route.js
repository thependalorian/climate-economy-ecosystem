import { NextResponse } from 'next/server';
import { metrics_service } from '@/lib/monitoring/metrics_service';
import { auth } from '@/auth';
import supabaseAdmin from '@/lib/supabase-api';

/**
 * Hybrid Search API
 * Combines vector search and keyword search for comprehensive results
 * Location: /app/api/search/hybrid/route.js
 */

export async function GET(request) {
  try {
    // Get search parameters
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q');
    const filters = searchParams.get('filters');
    const limit = parseInt(searchParams.get('limit') || '10', 10);
    const offset = parseInt(searchParams.get('offset') || '0', 10);
    
    if (!query || query.trim() === '') {
      return NextResponse.json(
        { error: 'Search query is required' },
        { status: 400 }
      );
    }
    
    // Get user for analytics
    const session = await auth();
    const userId = session?.user?.id || 'anonymous';
    
    // Start timing for performance metrics
    const startTime = Date.now();
    
    // Parse filters if provided
    let filterCategories = [];
    if (filters) {
      try {
        filterCategories = JSON.parse(filters);
      } catch (e) {
        console.error('Error parsing filters:', e);
      }
    }
    
    // Perform hybrid search
    const results = await performHybridSearch(query, filterCategories, limit, offset);
    
    // Calculate performance metrics
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // Track search event
    await metrics_service.track_event(
      'hybrid_search',
      userId,
      {
        query,
        filters: filterCategories,
        resultCount: results.length,
        duration_ms: duration
      }
    );
    
    // Track API performance
    await metrics_service.track_api_performance(
      '/api/search/hybrid',
      duration,
      200,
      userId,
      { query, filters: filterCategories }
    );
    
    return NextResponse.json({
      results,
      meta: {
        count: results.length,
        query,
        filters: filterCategories,
        duration_ms: duration
      }
    });
  } catch (error) {
    console.error('Error in hybrid search:', error);
    
    return NextResponse.json(
      { error: 'Failed to perform search', message: error.message },
      { status: 500 }
    );
  }
}

/**
 * Performs hybrid search combining vector and keyword search
 */
async function performHybridSearch(query, filterCategories = [], limit = 10, offset = 0) {
  try {
    // Calculate embedding for vector search
    const { data: embedding } = await supabaseAdmin.functions.invoke('embed-text', {
      body: { text: query }
    });
    
    if (!embedding?.vector) {
      throw new Error('Failed to generate text embedding');
    }
    
    // Prepare filter conditions
    let filterCondition = '';
    if (filterCategories.length > 0) {
      filterCondition = `category IN (${filterCategories.map(c => `'${c}'`).join(',')})`;
    }
    
    // Perform vector search
    const { data: vectorResults, error: vectorError } = await supabaseAdmin
      .rpc('match_climate_memories', {
        query_embedding: embedding.vector,
        match_threshold: 0.6,
        match_count: limit * 2 // Get more than needed to allow for post-processing
      });
    
    if (vectorError) {
      throw new Error(`Vector search error: ${vectorError.message}`);
    }
    
    // Perform keyword search
    const keywordQuery = supabaseAdmin
      .from('climate_memories')
      .select('*')
      .textSearch('content', query, {
        type: 'websearch',
        config: 'english'
      })
      .limit(limit * 2); // Get more than needed
    
    // Apply filter if provided
    if (filterCondition) {
      keywordQuery.filter(filterCondition);
    }
    
    const { data: keywordResults, error: keywordError } = await keywordQuery;
    
    if (keywordError) {
      throw new Error(`Keyword search error: ${keywordError.message}`);
    }
    
    // Combine results, remove duplicates, and score them
    const combinedResults = combineAndScoreResults(vectorResults, keywordResults, query);
    
    // Sort by score (descending)
    combinedResults.sort((a, b) => b.score - a.score);
    
    // Apply pagination
    return combinedResults.slice(offset, offset + limit);
  } catch (error) {
    console.error('Error in performHybridSearch:', error);
    throw error;
  }
}

/**
 * Combines vector and keyword search results, removing duplicates
 * and calculating a combined relevance score
 */
function combineAndScoreResults(vectorResults, keywordResults, query) {
  // Create a map to track IDs and prevent duplicates
  const resultMap = new Map();
  
  // Process vector search results
  if (vectorResults && vectorResults.length > 0) {
    vectorResults.forEach((item) => {
      resultMap.set(item.id, {
        id: item.id,
        content: item.content,
        category: item.category,
        source: item.source,
        metadata: item.metadata || {},
        created_at: item.created_at,
        score: item.similarity * 0.7, // Weight vector search at 70%
        vector_match: true,
        keyword_match: false
      });
    });
  }
  
  // Process keyword search results
  if (keywordResults && keywordResults.length > 0) {
    keywordResults.forEach((item) => {
      // Calculate a simple keyword relevance score
      const queryWords = query.toLowerCase().split(/\s+/);
      const contentWords = item.content.toLowerCase().split(/\s+/);
      
      // Count the number of query words that appear in content
      const matchCount = queryWords.filter(qw => 
        contentWords.some(cw => cw.includes(qw))
      ).length;
      
      // Calculate a score between 0 and 1
      const keywordScore = queryWords.length > 0 
        ? matchCount / queryWords.length * 0.5 // Weight keyword search at 50%
        : 0;
      
      if (resultMap.has(item.id)) {
        // Item already exists from vector search, update score
        const existingItem = resultMap.get(item.id);
        existingItem.score += keywordScore;
        existingItem.keyword_match = true;
      } else {
        // New item from keyword search
        resultMap.set(item.id, {
          id: item.id,
          content: item.content,
          category: item.category,
          source: item.source,
          metadata: item.metadata || {},
          created_at: item.created_at,
          score: keywordScore,
          vector_match: false,
          keyword_match: true
        });
      }
    });
  }
  
  // Convert map to array
  return Array.from(resultMap.values());
} 