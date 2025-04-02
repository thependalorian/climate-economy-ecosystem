'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { Spinner } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * StreamingResponse Component
 * 
 * Displays a streaming chat response with token-by-token updates
 * and proper formatting of markdown content.
 */
export default function StreamingResponse({ 
  query,
  onComplete,
  className,
  showSources = false,
  modelOverride = null
}) {
  const [streamedContent, setStreamedContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(true);
  const [sources, setSources] = useState([]);
  const [error, setError] = useState(null);
  const { data: session } = useSession();
  const abortControllerRef = useRef(null);
  
  useEffect(() => {
    if (!query) return;
    
    const fetchStreamingResponse = async () => {
      setIsStreaming(true);
      setStreamedContent('');
      setSources([]);
      setError(null);
      
      try {
        // Create abort controller for the fetch request
        abortControllerRef.current = new AbortController();
        const { signal } = abortControllerRef.current;
        
        // Make the streaming request
        const response = await fetch('/api/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query,
            user_id: session?.user?.id || 'anonymous',
            model: modelOverride
          }),
          signal
        });
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }
        
        // Get the response reader for streaming
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedContent = '';
        
        while (true) {
          const { value, done } = await reader.read();
          
          if (done) {
            break;
          }
          
          // Decode the chunk and update state
          const chunk = decoder.decode(value, { stream: true });
          
          try {
            // Parse the chunk as JSON if it contains a complete object
            if (chunk.trim().startsWith('{') && chunk.trim().endsWith('}')) {
              const parsedChunk = JSON.parse(chunk);
              
              if (parsedChunk.sources) {
                setSources(parsedChunk.sources);
              }
              
              if (parsedChunk.text) {
                accumulatedContent += parsedChunk.text;
                setStreamedContent(accumulatedContent);
              }
            } else {
              // Handle plain text streaming or partial JSON
              accumulatedContent += chunk;
              setStreamedContent(accumulatedContent);
            }
          } catch (e) {
            // If JSON parsing fails, just append the chunk
            accumulatedContent += chunk;
            setStreamedContent(accumulatedContent);
          }
        }
        
        // Call the completion callback with the full response
        if (onComplete) {
          onComplete(accumulatedContent, sources);
        }
      } catch (e) {
        // Ignore AbortError as it's intentional
        if (e.name !== 'AbortError') {
          console.error('Error streaming response:', e);
          setError(e.message);
          
          // Call the completion callback with the error
          if (onComplete) {
            onComplete('', [], e);
          }
        }
      } finally {
        setIsStreaming(false);
      }
    };
    
    fetchStreamingResponse();
    
    // Cleanup function to abort the request if component unmounts
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [query, session, onComplete, modelOverride]);
  
  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  };
  
  if (error) {
    return (
      <div className={`text-red-500 p-4 rounded-md bg-red-50 ${className}`}>
        <p className="font-semibold">Error:</p>
        <p>{error}</p>
      </div>
    );
  }
  
  return (
    <div className={className}>
      {streamedContent.length > 0 ? (
        <div>
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {streamedContent}
            </ReactMarkdown>
          </div>
          
          {isStreaming && (
            <div className="flex items-center mt-2">
              <Spinner className="h-4 w-4 animate-spin mr-2" />
              <span className="text-xs text-muted-foreground">Generating response...</span>
              <button 
                onClick={stopStreaming}
                className="ml-2 text-xs text-primary hover:underline"
              >
                Stop
              </button>
            </div>
          )}
          
          {showSources && sources.length > 0 && !isStreaming && (
            <div className="mt-4 text-sm border-t pt-2">
              <p className="font-medium mb-1">Sources:</p>
              <ul className="space-y-1">
                {sources.map((source, index) => (
                  <li key={index} className="flex items-start text-xs">
                    <span className="mr-1">•</span>
                    {source.url ? (
                      <a 
                        href={source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:underline break-all"
                      >
                        {source.url}
                      </a>
                    ) : (
                      <span>
                        {source.source === 'database' ? 'Knowledge base' : source.source}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : isStreaming ? (
        <div className="flex items-center p-4">
          <Spinner className="h-4 w-4 animate-spin mr-2" />
          <span className="text-muted-foreground">Generating response...</span>
        </div>
      ) : null}
    </div>
  );
} 