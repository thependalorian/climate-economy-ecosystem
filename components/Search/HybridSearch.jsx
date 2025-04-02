'use client';

import { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { 
  Search, 
  Filter, 
  X, 
  BarChart2, 
  Clock, 
  ExternalLink, 
  ThumbsUp, 
  ThumbsDown,
  Database,
  Globe,
  BookOpen
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

/**
 * Advanced Hybrid Search Component
 * 
 * Provides a sophisticated search interface for the Climate Economy Ecosystem
 * with filtering, ranking controls, and result visualization
 */
export default function HybridSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeFilters, setActiveFilters] = useState({
    source: 'all', // 'all', 'database', 'web'
    category: 'all', // 'all', 'job', 'training', 'report', etc.
    timeframe: 'all', // 'all', 'day', 'week', 'month', 'year'
  });
  const [searchStats, setSearchStats] = useState({
    totalResults: 0,
    dbResults: 0,
    webResults: 0,
    searchTime: 0
  });
  const [rankingMethod, setRankingMethod] = useState('relevance'); // 'relevance', 'date', 'hybrid'
  const [showFilters, setShowFilters] = useState(false);
  const [expandedResult, setExpandedResult] = useState(null);
  const { data: session } = useSession();
  const searchTimeoutRef = useRef(null);
  const [searchHistory, setSearchHistory] = useState([]);
  
  // Categories for filtering
  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'job', label: 'Job Opportunities' },
    { value: 'training', label: 'Training Programs' },
    { value: 'report', label: 'Reports & Research' },
    { value: 'company', label: 'Companies' },
    { value: 'resource', label: 'Resources' }
  ];
  
  // Sources for filtering
  const sources = [
    { value: 'all', label: 'All Sources' },
    { value: 'database', label: 'Knowledge Base' },
    { value: 'web', label: 'Web Results' }
  ];
  
  // Time frames for filtering
  const timeframes = [
    { value: 'all', label: 'Any Time' },
    { value: 'day', label: 'Past 24 Hours' },
    { value: 'week', label: 'Past Week' },
    { value: 'month', label: 'Past Month' },
    { value: 'year', label: 'Past Year' }
  ];
  
  // Ranking methods
  const rankingMethods = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'date', label: 'Most Recent' },
    { value: 'hybrid', label: 'Balanced' }
  ];

  // Load search history from localStorage on component mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedHistory = localStorage.getItem('searchHistory');
      if (savedHistory) {
        try {
          setSearchHistory(JSON.parse(savedHistory));
        } catch (e) {
          console.error('Error parsing search history:', e);
        }
      }
    }
  }, []);
  
  // Save search history to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined' && searchHistory.length > 0) {
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    }
  }, [searchHistory]);

  const handleSearch = async (e) => {
    e?.preventDefault();
    
    if (!query.trim()) return;
    
    // Clear any pending search timeouts
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    setIsLoading(true);
    const startTime = Date.now();
    
    try {
      const response = await fetch('/api/search/hybrid', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          user_id: session?.user?.id || 'anonymous',
          filters: activeFilters,
          ranking_method: rankingMethod,
          max_results: 20
        }),
      });
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const data = await response.json();
      const endTime = Date.now();
      
      // Update results and stats
      setResults(data.results || []);
      setSearchStats({
        totalResults: data.results?.length || 0,
        dbResults: data.results?.filter(r => r.source === 'database').length || 0,
        webResults: data.results?.filter(r => r.source === 'web').length || 0,
        searchTime: (endTime - startTime) / 1000
      });
      
      // Add to search history if not already present
      if (!searchHistory.some(item => item.query === query.trim())) {
        setSearchHistory(prev => [
          { 
            id: Date.now(), 
            query: query.trim(), 
            timestamp: new Date().toISOString() 
          },
          ...prev.slice(0, 9) // Keep only the 10 most recent searches
        ]);
      }
    } catch (error) {
      console.error('Error performing search:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleQueryChange = (e) => {
    setQuery(e.target.value);
    
    // Auto-search after a delay if query has at least 3 characters
    if (e.target.value.trim().length >= 3) {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
      
      searchTimeoutRef.current = setTimeout(() => {
        handleSearch();
      }, 500); // 500ms delay
    }
  };
  
  const handleFilterChange = (type, value) => {
    setActiveFilters(prev => ({
      ...prev,
      [type]: value
    }));
    
    // Re-run search with new filters if we have a query
    if (query.trim()) {
      searchTimeoutRef.current = setTimeout(() => {
        handleSearch();
      }, 300);
    }
  };
  
  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };
  
  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setSearchStats({
      totalResults: 0,
      dbResults: 0,
      webResults: 0,
      searchTime: 0
    });
  };
  
  const getSourceIcon = (source) => {
    switch (source) {
      case 'database':
        return <Database size={16} className="text-blue-500" />;
      case 'web':
        return <Globe size={16} className="text-green-500" />;
      default:
        return <BookOpen size={16} />;
    }
  };
  
  const rateResult = async (resultId, isHelpful) => {
    try {
      await fetch('/api/search/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: session?.user?.id || 'anonymous',
          result_id: resultId,
          query: query,
          is_helpful: isHelpful
        }),
      });
      
      // Update UI to show feedback was recorded
      setResults(prev => 
        prev.map(item => 
          item.id === resultId 
            ? { ...item, rated: true, helpful: isHelpful } 
            : item
        )
      );
    } catch (error) {
      console.error('Error rating search result:', error);
    }
  };
  
  const loadHistoryQuery = (historyItem) => {
    setQuery(historyItem.query);
    searchTimeoutRef.current = setTimeout(() => {
      handleSearch();
    }, 100);
  };
  
  const clearHistory = () => {
    setSearchHistory([]);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('searchHistory');
    }
  };
  
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };
  
  return (
    <div className="w-full max-w-5xl mx-auto space-y-4">
      {/* Search form */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-grow">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search className="h-4 w-4 text-muted-foreground" />
          </div>
          <Input
            type="search"
            placeholder="Search for clean energy jobs, training, or resources..."
            value={query}
            onChange={handleQueryChange}
            className="pl-10 pr-10"
          />
          {query && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute inset-y-0 right-0 flex items-center pr-3"
              aria-label="Clear search"
            >
              <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
            </button>
          )}
        </div>
        <Button type="submit" disabled={!query.trim() || isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </Button>
        <Button 
          type="button" 
          variant={showFilters ? "default" : "outline"} 
          onClick={toggleFilters}
          aria-label="Toggle filters"
        >
          <Filter className="h-4 w-4" />
        </Button>
      </form>
      
      {/* Filters */}
      {showFilters && (
        <Card>
          <CardContent className="pt-4 pb-2">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium">Source</label>
                <Select 
                  value={activeFilters.source} 
                  onValueChange={(value) => handleFilterChange('source', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All Sources" />
                  </SelectTrigger>
                  <SelectContent>
                    {sources.map(source => (
                      <SelectItem key={source.value} value={source.value}>
                        {source.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium">Category</label>
                <Select 
                  value={activeFilters.category} 
                  onValueChange={(value) => handleFilterChange('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(category => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium">Time Frame</label>
                <Select 
                  value={activeFilters.timeframe} 
                  onValueChange={(value) => handleFilterChange('timeframe', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any Time" />
                  </SelectTrigger>
                  <SelectContent>
                    {timeframes.map(timeframe => (
                      <SelectItem key={timeframe.value} value={timeframe.value}>
                        {timeframe.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <label className="text-sm font-medium">Ranking Method</label>
                <Select 
                  value={rankingMethod} 
                  onValueChange={setRankingMethod}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Relevance" />
                  </SelectTrigger>
                  <SelectContent>
                    {rankingMethods.map(method => (
                      <SelectItem key={method.value} value={method.value}>
                        {method.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Search stats */}
      {results.length > 0 && (
        <div className="flex items-center text-sm text-muted-foreground">
          <BarChart2 className="h-4 w-4 mr-1" />
          <span>{searchStats.totalResults} results</span>
          <span className="mx-2">|</span>
          <Database className="h-4 w-4 mr-1" />
          <span>{searchStats.dbResults} from database</span>
          <span className="mx-2">|</span>
          <Globe className="h-4 w-4 mr-1" />
          <span>{searchStats.webResults} from web</span>
          <span className="mx-2">|</span>
          <Clock className="h-4 w-4 mr-1" />
          <span>{searchStats.searchTime.toFixed(2)} seconds</span>
        </div>
      )}
      
      {/* Main content area with tabs */}
      <Tabs defaultValue="results">
        <TabsList>
          <TabsTrigger value="results">Search Results</TabsTrigger>
          <TabsTrigger value="history">Search History</TabsTrigger>
        </TabsList>
        
        {/* Results Tab */}
        <TabsContent value="results">
          {isLoading ? (
            <div className="flex justify-center p-12">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result, index) => (
                <Card key={index} className="relative overflow-hidden">
                  <CardContent className="pt-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-1">{getSourceIcon(result.source)}</div>
                      <div className="flex-grow">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-lg line-clamp-1">
                            {result.title || 'Untitled Resource'}
                          </h3>
                          {result.category && (
                            <Badge variant="outline" className="capitalize">
                              {result.category}
                            </Badge>
                          )}
                        </div>
                        
                        {result.url && (
                          <a 
                            href={result.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-muted-foreground hover:text-primary flex items-center mb-2"
                          >
                            {result.url.length > 50 ? `${result.url.substring(0, 50)}...` : result.url}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        )}
                        
                        <p className={`text-sm ${expandedResult === result.id ? '' : 'line-clamp-3'}`}>
                          {result.snippet || result.content}
                        </p>
                        
                        <div className="flex justify-between items-center mt-2">
                          <div className="flex gap-2 items-center">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => setExpandedResult(expandedResult === result.id ? null : result.id)}
                            >
                              {expandedResult === result.id ? 'Show Less' : 'Show More'}
                            </Button>
                            
                            {result.date && (
                              <span className="text-xs text-muted-foreground">
                                {formatDate(result.date)}
                              </span>
                            )}
                          </div>
                          
                          {!result.rated && (
                            <div className="flex gap-1">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => rateResult(result.id, true)}
                                aria-label="This is helpful"
                              >
                                <ThumbsUp className="h-4 w-4" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => rateResult(result.id, false)}
                                aria-label="This is not helpful"
                              >
                                <ThumbsDown className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                          
                          {result.rated && (
                            <span className="text-xs text-green-500">
                              {result.helpful ? 'Marked as helpful' : 'Thanks for your feedback'}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : query ? (
            <Card>
              <CardContent className="py-8 text-center">
                <h3 className="text-lg font-medium mb-2">No results found</h3>
                <p className="text-muted-foreground">
                  Try different keywords or adjust your filters to find what you're looking for.
                </p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <h3 className="text-lg font-medium mb-2">Search the Clean Energy Ecosystem</h3>
                <p className="text-muted-foreground">
                  Search for jobs, training programs, companies, and resources in the Massachusetts clean energy sector.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardContent className="py-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium">Recent Searches</h3>
                {searchHistory.length > 0 && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={clearHistory}
                  >
                    Clear History
                  </Button>
                )}
              </div>
              
              {searchHistory.length > 0 ? (
                <ul className="space-y-2">
                  {searchHistory.map(item => (
                    <li key={item.id} className="flex justify-between items-center">
                      <Button 
                        variant="ghost" 
                        className="text-left justify-start h-auto py-2 w-full"
                        onClick={() => loadHistoryQuery(item)}
                      >
                        <span className="truncate">{item.query}</span>
                      </Button>
                      <span className="text-xs text-muted-foreground">
                        {formatDate(item.timestamp)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-center text-muted-foreground py-4">
                  Your search history will appear here
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 