'use client';

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { FileText, MessageSquare, Search, Activity, ArrowRight, Send, Info, AlertCircle, ThumbsUp, ThumbsDown, Trash2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { useToast } from '@/components/ui/toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import MainLayout from '@/components/layout/MainLayout';

/**
 * Climate Economy Assistant Chat Interface
 * Main chat interface for user interaction with the AI assistant
 * Location: /app/assistant/chat/page.jsx
 */
export default function ChatAssistant() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [showSources, setShowSources] = useState(false);
  const [currentSources, setCurrentSources] = useState([]);
  const [clearDialogOpen, setClearDialogOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch user profile and message history on component mount
  useEffect(() => {
    if (user) {
      fetchUserProfile();
      fetchMessageHistory();
    } else {
      // Add welcome message for non-authenticated users
      if (messages.length === 0) {
        setMessages([
          {
            id: 'welcome',
            role: 'assistant',
            content: "Welcome to the Climate Economy Assistant! I can help you explore career opportunities in clean energy, find training programs, and connect with employers in Massachusetts. What would you like to know about today?",
            timestamp: new Date().toISOString()
          }
        ]);
      }
    }
  }, [user]);

  // Scroll to bottom whenever messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('/api/user/profile');
      if (response.ok) {
        const data = await response.json();
        setUserProfile(data);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchMessageHistory = async () => {
    try {
      const response = await fetch('/api/assistant/history');
      if (response.ok) {
        const data = await response.json();
        if (data.messages && data.messages.length > 0) {
          setMessages(data.messages);
        } else {
          // If no message history, add welcome message
          setMessages([
            {
              id: 'welcome',
              role: 'assistant',
              content: "Welcome to the Climate Economy Assistant! I can help you explore career opportunities in clean energy, find training programs, and connect with employers in Massachusetts. What would you like to know about today?",
              timestamp: new Date().toISOString()
            }
          ]);
        }
      }
    } catch (error) {
      console.error('Error fetching message history:', error);
      // Add welcome message on error
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: "Welcome to the Climate Economy Assistant! I can help you explore career opportunities in clean energy, find training programs, and connect with employers in Massachusetts. What would you like to know about today?",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  };

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
    setIsTyping(true);

    try {
      // Track message for engagement
      await fetch('/api/engagement/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'message_sent' })
      });

      // Send message to API
      const response = await fetch('/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          history: messages.slice(-10) // Send last 10 messages for context
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        sources: data.sources || [],
        fromCache: data.fromCache || false
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Set sources if available
      if (data.sources && data.sources.length > 0) {
        setCurrentSources(data.sources);
      }

    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: "I'm sorry, there was an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
        isError: true
      }]);

      toast("Could not process your message. Please try again.", "error");
    } finally {
      setIsTyping(false);
    }
  };

  const handleClearConversation = async () => {
    try {
      if (user) {
        await fetch('/api/assistant/clear', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
      }

      // Reset messages with a new welcome message
      setMessages([{
        id: 'welcome-new',
        role: 'assistant',
        content: "I've cleared our conversation. How can I help you today?",
        timestamp: new Date().toISOString()
      }]);

      setClearDialogOpen(false);

      toast("Your conversation history has been cleared.", "success");
    } catch (error) {
      console.error('Error clearing conversation:', error);
      toast("Failed to clear conversation. Please try again.", "error");
    }
  };

  const handleToggleSources = () => {
    setShowSources(!showSources);
  };

  const handleFeedback = async (messageId, isPositive) => {
    try {
      await fetch('/api/assistant/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messageId,
          feedback: isPositive ? 'positive' : 'negative'
        })
      });

      // Update engagement metrics
      await fetch('/api/engagement/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'feedback_provided',
          data: { isPositive }
        })
      });

      toast(
        isPositive ?
          "Thank you for your feedback! We're glad this was helpful." :
          "Thank you for your feedback! We'll work to improve our responses.",
        isPositive ? "success" : "info"
      );

    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-midnight-forest mb-6">
          Climate Economy Assistant
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Left sidebar with user info and options */}
          <div className="md:col-span-1">
            <Card className="p-6 mb-6">
              <div className="space-y-4">
                {userProfile ? (
                  <>
                    <div>
                      <h3 className="font-semibold text-midnight-forest mb-2">Climate Economy Fit</h3>
                      <div className="relative pt-1">
                        <Progress value={userProfile.climateEconomyScore || 0} className="h-4" />
                        <span className="absolute top-0 right-0 text-xs font-semibold inline-block text-midnight-forest">
                          {userProfile.climateEconomyScore || 0}%
                        </span>
                      </div>
                    </div>

                    {userProfile.skills && userProfile.skills.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-midnight-forest mb-2">Top Skills</h3>
                        <div className="flex flex-wrap gap-2">
                          {userProfile.skills.slice(0, 5).map((skill, index) => (
                            <Badge key={index} variant="secondary">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <Button variant="outline" size="sm" className="w-full" asChild>
                      <Link href="/onboarding">
                        Update Profile
                      </Link>
                    </Button>
                  </>
                ) : (
                  <div className="space-y-4">
                    <div className="text-moss-green">
                      Complete your profile to get personalized recommendations.
                    </div>
                    <Button variant="default" className="w-full" asChild>
                      <Link href="/onboarding">
                        Create Profile
                      </Link>
                    </Button>
                  </div>
                )}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="font-semibold text-midnight-forest mb-4">Quick Links</h3>
              <div className="space-y-2">
                <Button variant="ghost" size="sm" className="w-full justify-start" asChild>
                  <Link href="/dashboard">
                    <Activity className="mr-2 h-4 w-4" />
                    Dashboard
                  </Link>
                </Button>
                <Button variant="ghost" size="sm" className="w-full justify-start" asChild>
                  <Link href="/assistant/search">
                    <Search className="mr-2 h-4 w-4" />
                    Knowledge Base
                  </Link>
                </Button>
                <Button variant="ghost" size="sm" className="w-full justify-start" asChild>
                  <Link href="/assistant/resume">
                    <FileText className="mr-2 h-4 w-4" />
                    Resume Analysis
                  </Link>
                </Button>

                <Dialog open={clearDialogOpen} onOpenChange={setClearDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="ghost" size="sm" className="w-full justify-start text-rose-600 hover:text-rose-700 hover:bg-rose-50">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Clear Chat
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Clear Conversation</DialogTitle>
                      <DialogDescription>
                        This will permanently delete your conversation history. This action cannot be undone.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setClearDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button variant="destructive" onClick={handleClearConversation}>
                        Clear
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </Card>
          </div>

          {/* Chat area */}
          <div className="md:col-span-3">
            <Card className="h-[calc(100vh-12rem)] flex flex-col">
              {/* Chat messages */}
              <div className="flex-grow overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-spring-green text-midnight-forest'
                          : message.role === 'system'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-sand-gray text-midnight-forest'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>

                      {message.fromCache && (
                        <span className="text-xs text-moss-green mt-2 flex items-center">
                          <Info className="h-3 w-3 mr-1" />
                          Cached response
                        </span>
                      )}

                      {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                        <button
                          onClick={handleToggleSources}
                          className="mt-2 text-xs flex items-center text-moss-green hover:text-spring-green"
                        >
                          <Info className="h-3 w-3 mr-1" />
                          {showSources ? 'Hide sources' : `${message.sources.length} sources`}
                        </button>
                      )}

                      {message.role === 'assistant' && (
                        <div className="mt-2 flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleFeedback(message.id, true)}
                            className="text-moss-green hover:text-spring-green"
                            aria-label="Helpful"
                          >
                            <ThumbsUp className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleFeedback(message.id, false)}
                            className="text-moss-green hover:text-spring-green"
                            aria-label="Not helpful"
                          >
                            <ThumbsDown className="h-4 w-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-sand-gray text-midnight-forest max-w-[80%] rounded-lg p-4">
                      <div className="flex space-x-2">
                        <div className="h-2 w-2 bg-moss-green rounded-full animate-bounce"></div>
                        <div className="h-2 w-2 bg-moss-green rounded-full animate-bounce delay-75"></div>
                        <div className="h-2 w-2 bg-moss-green rounded-full animate-bounce delay-150"></div>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Sources section */}
              {showSources && currentSources.length > 0 && (
                <div className="p-4 bg-seafoam-blue/20 border-t border-spring-green/20">
                  <h4 className="font-semibold text-midnight-forest mb-2">Sources</h4>
                  <div className="space-y-2">
                    {currentSources.map((source, index) => (
                      <div key={index} className="text-sm">
                        <div className="font-medium">{source.title || 'Untitled Source'}</div>
                        {source.url && (
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-spring-green hover:underline text-xs"
                          >
                            {source.url}
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={handleToggleSources}
                    className="mt-2 text-xs flex items-center text-moss-green hover:text-spring-green"
                  >
                    Hide sources
                  </button>
                </div>
              )}

              {/* Input area */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <textarea
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    className="flex-grow px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-spring-green resize-none"
                    rows={2}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={isTyping || !inputValue.trim()}
                    className="self-end"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                <div className="mt-2 text-xs text-moss-green flex items-center">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Ask about clean energy careers, training programs, or job opportunities in Massachusetts
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}