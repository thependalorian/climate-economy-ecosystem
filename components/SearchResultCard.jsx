'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  FileText, 
  BookOpen, 
  Briefcase, 
  Bookmark 
} from 'lucide-react';

/**
 * Search Result Card Component
 * Displays information from a search result with source details and relevance score
 * Location: /components/SearchResultCard.jsx
 */
export default function SearchResultCard({ result, onSave }) {
  const [expanded, setExpanded] = useState(false);
  
  // Get icon based on resource type
  const getResourceIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'job':
        return <Briefcase className="h-4 w-4" />;
      case 'training':
        return <BookOpen className="h-4 w-4" />;
      case 'report':
      case 'guide':
      case 'policy':
      case 'study':
        return <FileText className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };
  
  // Format content for display
  const formatContent = (content) => {
    if (!content) return '';
    
    // For expanded view, show more content
    const maxLength = expanded ? 1000 : 300;
    
    if (content.length <= maxLength) {
      return content;
    }
    
    return `${content.substring(0, maxLength)}${expanded ? '...' : '... '}`;
  };
  
  // Calculate relevance color based on score
  const getRelevanceColor = (score) => {
    if (score >= 0.9) return 'bg-green-500';
    if (score >= 0.8) return 'bg-green-400';
    if (score >= 0.7) return 'bg-green-300';
    if (score >= 0.6) return 'bg-yellow-400';
    if (score >= 0.5) return 'bg-yellow-300';
    return 'bg-gray-300';
  };
  
  return (
    <Card className="p-4 mb-4 border-l-4 border-l-emerald-500">
      <div className="mb-2 flex justify-between items-start">
        <h3 className="text-lg font-semibold text-gray-800">
          {result.title || 'Untitled Resource'}
        </h3>
        
        <div className="flex items-center space-x-2">
          {result.resource_type && (
            <Badge variant="outline" className="flex items-center space-x-1">
              {getResourceIcon(result.resource_type)}
              <span>{result.resource_type}</span>
            </Badge>
          )}
          
          <div className="flex items-center">
            <span className="text-xs mr-2">Relevance:</span>
            <Progress 
              className="w-24 h-2" 
              value={result.similarity * 100} 
              indicatorClassName={getRelevanceColor(result.similarity)}
            />
            <span className="text-xs ml-2">{Math.round(result.similarity * 100)}%</span>
          </div>
        </div>
      </div>
      
      <div className="mb-3 text-sm text-gray-600">
        {result.source && (
          <div className="text-xs text-gray-500 mb-1">
            Source: {result.source}
          </div>
        )}
      </div>
      
      <div className="text-sm text-gray-700 whitespace-pre-line">
        {formatContent(result.content)}
        {!expanded && result.content?.length > 300 && (
          <Button 
            variant="ghost" 
            size="sm" 
            className="mt-1 text-moss-green hover:text-spring-green"
            onClick={() => setExpanded(true)}
          >
            <ChevronDown className="h-4 w-4 mr-1" />
            Show more
          </Button>
        )}
        {expanded && (
          <Button 
            variant="ghost" 
            size="sm" 
            className="mt-1 text-moss-green hover:text-spring-green"
            onClick={() => setExpanded(false)}
          >
            <ChevronUp className="h-4 w-4 mr-1" />
            Show less
          </Button>
        )}
      </div>
      
      <div className="mt-4 flex justify-between items-center">
        {result.url ? (
          <Button 
            variant="outline" 
            size="sm" 
            className="text-xs"
            onClick={() => window.open(result.url, '_blank')}
          >
            <ExternalLink className="h-3.5 w-3.5 mr-1" />
            View Source
          </Button>
        ) : (
          <div></div>
        )}
        
        {onSave && (
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-moss-green"
            onClick={() => onSave(result)}
          >
            <Bookmark className="h-3.5 w-3.5 mr-1" />
            Save
          </Button>
        )}
      </div>
    </Card>
  );
} 