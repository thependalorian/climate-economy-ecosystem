'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Search, FileText, ExternalLink, ThumbsUp, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

/**
 * Knowledge Base Search
 * Semantic search interface with filtering options
 * Location: /app/assistant/search/page.jsx
 */
export default function KnowledgeBaseSearch() {
  const { toast } = useToast();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [useHybrid, setUseHybrid] = useState(true);
  const [selectedType, setSelectedType] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  
  // Filter options
  const resourceTypes = [
    { value: '', label: 'All Types' },
    { value: 'article', label: 'Articles' },
    { value: 'report', label: 'Reports' },
    { value: 'guide', label: 'Guides' },
    { value: 'job', label: 'Job Postings' },
    { value: 'course', label: 'Training Courses' }
  ];
  
  const dataSourceOptions = [
    { value: '', label: 'All Sources' },
    { value: 'website', label: 'Website' },
    { value: 'document', label: 'Document' },
    { value: 'api', label: 'API' },
    { value: 'database', label: 'Database' }
  ];
  
  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      toast({
        title: "Search Error",
        description: "Please enter a search term",
        variant: "destructive",
      });
      return;
    }
    
    try {
      setLoading(true);
      
      // Build search parameters
      const searchParams = new URLSearchParams({
        query: query.trim(),
        hybrid: useHybrid.toString()
      });
      
      if (selectedType) {
        searchParams.append('type', selectedType);
      }
      
      if (selectedSource) {
        searchParams.append('source', selectedSource);
      }
      
      // Fetch results from API
      const response = await fetch(`/api/assistant/search?${searchParams}`);
      
      if (!response.ok) {
        throw new Error(`Search failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.results || data.results.length === 0) {
        setResults([]);
        toast({
          title: "No Results",
          description: "No results found. Try different search terms or filters.",
          variant: "default",
        });
      } else {
        setResults(data.results);
        
        // Track search for engagement
        fetch('/api/engagement/track', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            action: 'resource_accessed',
            data: { query }
          })
        });
      }
    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Search Error",
        description: error.message || "Failed to perform search",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleResultClick = (result) => {
    // Track click for engagement
    fetch('/api/engagement/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        action: 'recommendation_clicked',
        data: { resultId: result.id }
      })
    });
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-midnight-forest mb-6">
          Climate Economy Knowledge Base
        </h1>
        
        <Card className="p-6 mb-8">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
              <div className="flex-grow">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Search for resources, jobs, training..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="flex space-x-2">
                <Select value={selectedType} onValueChange={setSelectedType}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Resource Type" />
                  </SelectTrigger>
                  <SelectContent>
                    {resourceTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Select value={selectedSource} onValueChange={setSelectedSource}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Source" />
                  </SelectTrigger>
                  <SelectContent>
                    {dataSourceOptions.map((source) => (
                      <SelectItem key={source.value} value={source.value}>
                        {source.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Button type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Searching
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Search
                    </>
                  )}
                </Button>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Checkbox 
                id="hybrid-search" 
                checked={useHybrid} 
                onCheckedChange={setUseHybrid} 
              />
              <label
                htmlFor="hybrid-search"
                className="text-sm text-moss-green cursor-pointer"
              >
                Enable hybrid search (combines semantic search with keyword matching for better results)
              </label>
            </div>
          </form>
        </Card>
        
        {results.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-midnight-forest">
              Search Results ({results.length})
            </h2>
            
            {results.map((result) => (
              <Card key={result.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex flex-col space-y-4">
                  <div className="flex justify-between items-start">
                    <h3 className="text-lg font-semibold text-midnight-forest">
                      {result.title || 'Untitled Resource'}
                    </h3>
                    
                    {result.similarity && (
                      <Badge className="bg-spring-green/20 text-spring-green">
                        {Math.round(result.similarity * 100)}% Match
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-moss-green line-clamp-3">
                    {result.content || 'No content available'}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    {result.metadata?.resource_type && (
                      <Badge variant="outline">
                        {result.metadata.resource_type}
                      </Badge>
                    )}
                    
                    {result.metadata?.data_type && (
                      <Badge variant="secondary">
                        {result.metadata.data_type}
                      </Badge>
                    )}
                  </div>
                  
                  <div className="flex justify-between items-center">
                    {result.url ? (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex items-center" 
                        asChild
                        onClick={() => handleResultClick(result)}
                      >
                        <a 
                          href={result.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="mr-2 h-4 w-4" />
                          View Resource
                        </a>
                      </Button>
                    ) : (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex items-center"
                        onClick={() => handleResultClick(result)}
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        View Details
                      </Button>
                    )}
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(result.content);
                        toast({
                          title: "Copied to clipboard",
                          description: "Content copied to clipboard",
                          variant: "default",
                        });
                      }}
                    >
                      <ThumbsUp className="mr-2 h-4 w-4" />
                      Helpful
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
        
        {query && results.length === 0 && !loading && (
          <Card className="p-6 text-center">
            <h3 className="text-lg font-semibold text-midnight-forest mb-2">
              No results found
            </h3>
            <p className="text-moss-green">
              Try different search terms or adjust your filters.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
} 