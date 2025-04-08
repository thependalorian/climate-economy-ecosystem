'use client';

import { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { 
  Send, 
  Info, 
  Loader2, 
  ThumbsUp, 
  ThumbsDown,
  AlertCircle,
  FileText
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import ReactMarkdown from 'react-markdown';

/**
 * Climate Assistant Component
 * 
 * A specialized assistant for Massachusetts climate economy information
 * with RLHF feedback collection
 */
export default function ClimateAssistant() {
  const { data: session } = useSession();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [currentSources, setCurrentSources] = useState([]);
  const messagesEndRef = useRef(null);

  // Add welcome message on component mount
  useEffect(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: "Welcome to the Massachusetts Climate Economy Assistant. I can help you find information about clean energy careers, training programs, and resources in Massachusetts. What would you like to know?",
        timestamp: new Date().toISOString()
      }
    ]);
  }, []);

  // Scroll to bottom when messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the climate query API
      const response = await fetch('/api/climate/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: userMessage.content,
          userId: session?.user?.id || 'anonymous'
        })
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();

      // Add assistant response to chat
      const assistantMessage = {
        id: data.message_id || Date.now().toString() + '-response',
        chat_id: data.chat_id,
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
        timestamp: new Date().toISOString(),
        within_constraints: data.within_constraints
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Set sources if available
      if (data.sources && data.sources.length > 0) {
        setCurrentSources(data.sources);
      }

    } catch (error) {
      console.error('Error querying climate assistant:', error);

      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now().toString() + '-error',
        role: 'system',
        content: "I'm sorry, there was an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSources = () => {
    setShowSources(!showSources);
  };

  const handleFeedback = async (messageId, isPositive) => {
    try {
      await fetch('/api/climate/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messageId,
          feedbackType: 'thumbs',
          isPositive
        })
      });

      // Show feedback confirmation
      alert(isPositive ? 'Thank you for your positive feedback!' : 'Thank you for your feedback. We\'ll work to improve our responses.');
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 rounded-t-lg">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : message.role === 'system'
                    ? message.isError 
                      ? 'bg-destructive text-destructive-foreground'
                      : 'bg-muted text-muted-foreground'
                    : 'bg-secondary text-secondary-foreground'
              }`}
            >
              {message.role === 'assistant' ? (
                <>
                  <ReactMarkdown className="prose prose-sm max-w-none dark:prose-invert">
                    {message.content}
                  </ReactMarkdown>
                  
                  {message.sources && message.sources.length > 0 && (
                    <button
                      onClick={handleToggleSources}
                      className="mt-2 text-xs flex items-center text-muted-foreground hover:text-primary"
                    >
                      <Info className="h-3 w-3 mr-1" />
                      {showSources ? 'Hide sources' : `${message.sources.length} sources`}
                    </button>
                  )}

                  <div className="mt-2 flex items-center justify-end space-x-2">
                    <button
                      onClick={() => handleFeedback(message.id, true)}
                      className="text-muted-foreground hover:text-primary"
                      aria-label="Helpful"
                    >
                      <ThumbsUp className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleFeedback(message.id, false)}
                      className="text-muted-foreground hover:text-primary"
                      aria-label="Not helpful"
                    >
                      <ThumbsDown className="h-4 w-4" />
                    </button>
                  </div>
                </>
              ) : (
                <div>{message.content}</div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-secondary text-secondary-foreground max-w-[80%] rounded-lg p-4">
              <div className="flex space-x-2 items-center">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Searching Massachusetts climate information...</span>
              </div>
            </div>
          </div>
        )}

        {/* Sources section */}
        {showSources && currentSources.length > 0 && (
          <Card className="p-4 bg-muted/50">
            <CardContent className="p-0 pt-4">
              <h4 className="font-semibold mb-2">Sources</h4>
              <div className="space-y-2">
                {currentSources.map((source, index) => (
                  <div key={index} className="text-sm">
                    <div className="font-medium">{source.metadata?.source || 'Source ' + (index + 1)}</div>
                    <div className="text-muted-foreground text-xs">{source.content}</div>
                    {source.metadata?.source_type && (
                      <Badge variant="outline" className="mt-1">
                        {source.metadata.source_type}
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
              <button
                onClick={handleToggleSources}
                className="mt-2 text-xs flex items-center text-muted-foreground hover:text-primary"
              >
                Hide sources
              </button>
            </CardContent>
          </Card>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t bg-background rounded-b-lg">
        <div className="flex space-x-2">
          <Textarea
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about clean energy careers, training programs, or resources in Massachusetts..."
            className="min-h-[80px] resize-none"
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="self-end"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        <div className="mt-2 text-xs text-muted-foreground flex items-center">
          <AlertCircle className="h-3 w-3 mr-1" />
          This assistant provides information specific to Massachusetts clean energy economy
        </div>
      </div>
    </div>
  );
}
