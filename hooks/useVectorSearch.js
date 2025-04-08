import { useState, useCallback } from 'react';

/**
 * Custom hook for vector search functionality
 * Provides methods to search the knowledge base with caching and error handling
 * Location: /hooks/useVectorSearch.js
 */
export default function useVectorSearch() {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fromCache, setFromCache] = useState(false);
  
  /**
   * Perform a search using the vector search API
   */
  const search = useCallback(async (query, options = {}) => {
    if (!query || query.trim() === '') {
      setError('Please enter a search query');
      return { results: [], error: 'Please enter a search query' };
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Build query params
      const params = new URLSearchParams({
        query: query.trim()
      });
      
      // Add optional filters
      if (options.type) {
        params.append('type', options.type);
      }
      
      if (options.source) {
        params.append('source', options.source);
      }
      
      if (options.limit) {
        params.append('limit', options.limit);
      }
      
      // Perform the search
      const response = await fetch(`/api/assistant/search?${params.toString()}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search');
      }
      
      const data = await response.json();
      
      // Update state
      setResults(data.results || []);
      setFromCache(data.fromCache || false);
      setIsLoading(false);
      
      // Return results for immediate use
      return { 
        results: data.results || [], 
        fromCache: data.fromCache || false 
      };
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'Failed to perform search');
      setIsLoading(false);
      
      return { results: [], error: err.message };
    }
  }, []);
  
  /**
   * Track when a search result is clicked or used
   */
  const trackResultClick = useCallback(async (resultId) => {
    try {
      await fetch('/api/engagement/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'resource_accessed',
          data: { resultId }
        })
      });
    } catch (err) {
      console.error('Failed to track result click:', err);
      // Non-critical, so just log the error
    }
  }, []);
  
  /**
   * Save a search result for later reference
   */
  const saveResult = useCallback(async (result) => {
    try {
      const response = await fetch('/api/assistant/saved', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ result })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to save result');
      }
      
      return { success: true };
    } catch (err) {
      console.error('Failed to save result:', err);
      return { success: false, error: err.message };
    }
  }, []);
  
  return {
    results,
    isLoading,
    error,
    fromCache,
    search,
    trackResultClick,
    saveResult
  };
} 