'use client';

import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, MessageSquare, Search, Activity, 
  ArrowRight, Send, Info, AlertCircle, 
  ThumbsUp, ThumbsDown, Trash2, Upload, 
  X, PaperclipIcon, FileIcon, CheckCircle
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { useToast } from '@/components/ui/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import MainLayout from '@/components/layout/MainLayout';
import StreamingResponse from './StreamingResponse';

/**
 * Integrated Chat Interface Component
 * 
 * Combines chat functionality with file upload capabilities and streaming responses
 */
export default function IntegratedChatInterface() {
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
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileAnalysisResults, setFileAnalysisResults] = useState(null);
  const [showFileDialog, setShowFileDialog] = useState(false);
  const [streamingQuery, setStreamingQuery] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

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

    // Set the streaming query to trigger the StreamingResponse component
    setStreamingQuery(userMessage.content);
  };

  const handleStreamingComplete = (response, sources, error) => {
    setIsTyping(false);
    
    if (error) {
      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: "I'm sorry, there was an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
        isError: true
      }]);
      
      toast({
        title: "Error",
        description: "Could not process your message. Please try again.",
        variant: "destructive",
      });
      return;
    }
    
    // Add assistant response to chat
    const assistantMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content: response,
      timestamp: new Date().toISOString(),
      sources: sources || [],
    };
    
    setMessages(prev => [...prev, assistantMessage]);
    
    // Set sources if available
    if (sources && sources.length > 0) {
      setCurrentSources(sources);
    }
    
    // Reset streaming query
    setStreamingQuery('');
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

      toast({
        title: "Conversation cleared",
        description: "Your conversation history has been cleared.",
      });
    } catch (error) {
      console.error('Error clearing conversation:', error);
      toast({
        title: "Error",
        description: "Failed to clear conversation. Please try again.",
        variant: "destructive",
      });
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

      toast({
        title: "Thank you for your feedback!",
        description: isPositive ?
          "We're glad this was helpful." :
          "We'll work to improve our responses.",
        variant: isPositive ? "default" : "secondary",
      });

    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  // File upload handlers
  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (!selectedFile) return;
    
    if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      .includes(selectedFile.type)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF or Word document",
        variant: "destructive",
      });
      return;
    }
    
    if (selectedFile.size > 5 * 1024 * 1024) { // 5MB limit
      toast({
        title: "File too large",
        description: "File size should be less than 5MB",
        variant: "destructive",
      });
      return;
    }
    
    setUploadedFile(selectedFile);
    handleUploadFile(selectedFile);
  };

  const handleUploadFile = async (file) => {
    setIsUploading(true);
    setUploadProgress(0);
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);
    
    try {
      // In a real implementation, this would be an API call to upload the file
      // For now, we'll simulate the upload and analysis process
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Set progress to 100% when complete
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Simulate file analysis results
      const analysisResults = {
        fileName: file.name,
        fileSize: file.size,
        uploadDate: new Date().toISOString(),
        skills: ['Solar Panel Installation', 'Electrical Wiring', 'Project Management'],
        experience: [
          { title: 'Solar Technician', company: 'Green Energy Solutions', years: 2 },
          { title: 'Electrical Apprentice', company: 'City Power', years: 1 }
        ],
        education: [
          { degree: 'Associate of Science', field: 'Electrical Technology', institution: 'Community College' }
        ]
      };
      
      setFileAnalysisResults(analysisResults);
      setShowFileDialog(true);
      
      // Add a system message about the file upload
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: `File uploaded: ${file.name}`,
        timestamp: new Date().toISOString(),
        isFileUpload: true
      }]);
      
      // Add an assistant message with analysis results
      const fileAnalysisMessage = {
        id: Date.now().toString() + '-analysis',
        role: 'assistant',
        content: `I've analyzed your resume and found the following:\n\n**Skills:**\n- Solar Panel Installation\n- Electrical Wiring\n- Project Management\n\n**Experience:**\n- Solar Technician at Green Energy Solutions (2 years)\n- Electrical Apprentice at City Power (1 year)\n\n**Education:**\n- Associate of Science in Electrical Technology\n\nHow would you like me to help with your clean energy career search?`,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, fileAnalysisMessage]);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      toast({
        title: "Upload failed",
        description: "Failed to upload and analyze your file. Please try again.",
        variant: "destructive",
      });
    } finally {
      clearInterval(progressInterval);
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setFileAnalysisResults(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
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
                      <h3 className="font-semibold mb-2">Climate Economy Fit</h3>
                      <div className="relative pt-1">
                        <Progress value={userProfile.climateEconomyScore || 0} className="h-4" />
                        <span className="absolute top-0 right-0 text-xs font-semibold inline-block">
                          {userProfile.climateEconomyScore || 0}%
                        </span>
                      </div>
                    </div>

                    {userProfile.skills && userProfile.skills.length > 0 && (
                      <div>
                        <h3 className="font-semibold mb-2">Top Skills</h3>
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
                    <div className="text-muted-foreground">
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
              <h3 className="font-semibold mb-4">Quick Links</h3>
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
                          ? 'bg-primary/10 text-foreground'
                          : message.role === 'system'
                            ? message.isFileUpload 
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-rose-100 text-rose-800'
                            : 'bg-muted text-foreground'
                      }`}
                    >
                      {message.isFileUpload ? (
                        <div className="flex items-center">
                          <FileIcon className="h-4 w-4 mr-2" />
                          <span>{message.content}</span>
                        </div>
                      ) : (
                        <div className="whitespace-pre-wrap">{message.content}</div>
                      )}

                      {message.fromCache && (
                        <span className="text-xs text-muted-foreground mt-2 flex items-center">
                          <Info className="h-3 w-3 mr-1" />
                          Cached response
                        </span>
                      )}

                      {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                        <button
                          onClick={handleToggleSources}
                          className="mt-2 text-xs flex items-center text-muted-foreground hover:text-primary"
                        >
                          <Info className="h-3 w-3 mr-1" />
                          {showSources ? 'Hide sources' : `${message.sources.length} sources`}
                        </button>
                      )}

                      {message.role === 'assistant' && (
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
                      )}
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-muted text-foreground max-w-[80%] rounded-lg p-4">
                      {streamingQuery ? (
                        <StreamingResponse 
                          query={streamingQuery} 
                          onComplete={handleStreamingComplete}
                          showSources={false}
                        />
                      ) : (
                        <div className="flex space-x-2">
                          <div className="h-2 w-2 bg-primary rounded-full animate-bounce"></div>
                          <div className="h-2 w-2 bg-primary rounded-full animate-bounce delay-75"></div>
                          <div className="h-2 w-2 bg-primary rounded-full animate-bounce delay-150"></div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Sources section */}
              {showSources && currentSources.length > 0 && (
                <div className="p-4 bg-muted/50 border-t">
                  <h4 className="font-semibold mb-2">Sources</h4>
                  <div className="space-y-2">
                    {currentSources.map((source, index) => (
                      <div key={index} className="text-sm">
                        <div className="font-medium">{source.title || 'Untitled Source'}</div>
                        {source.url && (
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline text-xs"
                          >
                            {source.url}
                          </a>
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
                </div>
              )}

              {/* Input area */}
              <div className="p-4 border-t border-border">
                <div className="flex flex-col space-y-2">
                  {/* File upload progress */}
                  {isUploading && (
                    <div className="mb-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span>Uploading {uploadedFile?.name}...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <Progress value={uploadProgress} className="h-2" />
                    </div>
                  )}
                  
                  {/* File display if uploaded but not uploading */}
                  {uploadedFile && !isUploading && (
                    <div className="flex items-center justify-between bg-muted p-2 rounded-md mb-2">
                      <div className="flex items-center">
                        <FileIcon className="h-4 w-4 mr-2" />
                        <span className="text-sm truncate max-w-[200px]">{uploadedFile.name}</span>
                      </div>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={handleRemoveFile}
                        className="h-6 w-6 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                  
                  {/* Input and buttons */}
                  <div className="flex space-x-2">
                    <div className="relative flex-grow">
                      <textarea
                        value={inputValue}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your message..."
                        className="w-full px-4 py-2 pr-10 border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                        rows={2}
                        disabled={isTyping}
                      />
                      <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".pdf,.doc,.docx"
                        onChange={handleFileChange}
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        className="absolute right-2 top-2"
                        onClick={handleFileButtonClick}
                        disabled={isTyping || isUploading || uploadedFile}
                      >
                        <PaperclipIcon className="h-4 w-4" />
                      </Button>
                    </div>
                    <Button
                      onClick={handleSendMessage}
                      disabled={isTyping || !inputValue.trim()}
                      className="self-end"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="mt-2 text-xs text-muted-foreground flex items-center">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Ask about clean energy careers, training programs, or upload your resume for personalized recommendations
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
      
      {/* File Analysis Dialog */}
      <Dialog open={showFileDialog} onOpenChange={setShowFileDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Resume Analysis Complete</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <div className="flex items-center text-green-600 mb-4">
              <CheckCircle className="h-5 w-5 mr-2" />
              <span className="font-medium">Successfully analyzed your resume</span>
            </div>
            
            <p className="text-sm text-muted-foreground mb-4">We've identified the following information:</p>
            
            {fileAnalysisResults && (
              <>
                <div className="mb-4">
                  <h4 className="font-medium text-sm mb-2">Skills Identified:</h4>
                  <div className="flex flex-wrap gap-2">
                    {fileAnalysisResults.skills.map(skill => (
                      <Badge key={skill} variant="secondary">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div className="mb-4">
                  <h4 className="font-medium text-sm mb-2">Experience:</h4>
                  <ul className="text-sm space-y-2">
                    {fileAnalysisResults.experience.map((exp, index) => (
                      <li key={index} className="flex justify-between">
                        <span>{exp.title} at {exp.company}</span>
                        <span className="text-muted-foreground">{exp.years} {exp.years === 1 ? 'year' : 'years'}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="mb-4">
                  <h4 className="font-medium text-sm mb-2">Education:</h4>
                  <ul className="text-sm space-y-2">
                    {fileAnalysisResults.education.map((edu, index) => (
                      <li key={index}>
                        <div>{edu.degree} in {edu.field}</div>
                        <div className="text-muted-foreground">{edu.institution}</div>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button onClick={() => setShowFileDialog(false)}>Continue</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </MainLayout>
  );
}
