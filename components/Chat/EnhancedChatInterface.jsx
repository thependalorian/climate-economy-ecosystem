'use client';

import { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { 
  Send, 
  FileUp, 
  X, 
  FileText, 
  ThumbsUp, 
  ThumbsDown, 
  Info, 
  Loader2, 
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import StreamingResponse from './StreamingResponse';

/**
 * Enhanced Chat Interface Component
 * 
 * A comprehensive chat interface that includes:
 * - Real-time streaming responses
 * - File upload capabilities
 * - Message history
 * - Feedback mechanisms
 */
export default function EnhancedChatInterface() {
  const { data: session } = useSession();
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingQuery, setStreamingQuery] = useState('');
  const [fileUpload, setFileUpload] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileAnalysisResults, setFileAnalysisResults] = useState(null);
  const [showFileDialog, setShowFileDialog] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [currentSources, setCurrentSources] = useState([]);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Fetch message history on component mount
  useEffect(() => {
    if (session?.user) {
      fetchMessageHistory();
    } else {
      // Add welcome message for non-authenticated users
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: "Welcome to the Climate Economy Assistant! I can help you explore career opportunities in clean energy, find training programs, and connect with employers in Massachusetts. What would you like to know about today?",
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [session]);

  // Scroll to bottom whenever messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessageHistory = async () => {
    try {
      const response = await fetch('/api/chat/history');
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
    if (!inputValue.trim() && !fileUpload) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim() || (fileUpload ? `I've uploaded a file: ${fileUpload.name}` : ''),
      timestamp: new Date().toISOString(),
      isFileUpload: !!fileUpload
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsStreaming(true);

    // If there's a file to upload, handle it first
    if (fileUpload) {
      await handleFileUpload();
    } else {
      // Set the streaming query to trigger the StreamingResponse component
      setStreamingQuery(userMessage.content);
    }
  };

  const handleStreamingComplete = (response, sources, error) => {
    setIsStreaming(false);
    
    if (error) {
      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: "I'm sorry, there was an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
        isError: true
      }]);
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

  const handleFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (!selectedFile) return;
    
    if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      .includes(selectedFile.type)) {
      alert('Please upload a PDF or Word document');
      return;
    }
    
    if (selectedFile.size > 5 * 1024 * 1024) { // 5MB limit
      alert('File size should be less than 5MB');
      return;
    }
    
    setFileUpload(selectedFile);
  };

  const handleRemoveFile = () => {
    setFileUpload(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileUpload = async () => {
    if (!fileUpload) return;
    
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
        fileName: fileUpload.name,
        fileSize: fileUpload.size,
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
      
      // Add an assistant message with analysis results
      const fileAnalysisMessage = {
        id: Date.now().toString() + '-analysis',
        role: 'assistant',
        content: `I've analyzed your resume and found the following:\n\n**Skills:**\n- Solar Panel Installation\n- Electrical Wiring\n- Project Management\n\n**Experience:**\n- Solar Technician at Green Energy Solutions (2 years)\n- Electrical Apprentice at City Power (1 year)\n\n**Education:**\n- Associate of Science in Electrical Technology\n\nBased on your background, you have valuable experience in the solar energy sector. How would you like me to help with your clean energy career search? I can suggest job opportunities, training programs, or provide information about growing sectors in Massachusetts.`,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, fileAnalysisMessage]);
      setIsStreaming(false);
      setFileUpload(null);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload and analyze your file. Please try again.');
    } finally {
      clearInterval(progressInterval);
      setIsUploading(false);
    }
  };

  const handleToggleSources = () => {
    setShowSources(!showSources);
  };

  const handleFeedback = async (messageId, isPositive) => {
    try {
      await fetch('/api/chat/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messageId,
          feedback: isPositive ? 'positive' : 'negative'
        })
      });

      alert(isPositive ? 'Thank you for your positive feedback!' : 'Thank you for your feedback. We\'ll work to improve our responses.');
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const formatMessageContent = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
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
              {message.isFileUpload ? (
                <div className="flex items-center">
                  <FileText className="h-4 w-4 mr-2" />
                  <span>{message.content}</span>
                </div>
              ) : (
                <div 
                  className="prose prose-sm max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
                />
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

        {isStreaming && (
          <div className="flex justify-start">
            <div className="bg-secondary text-secondary-foreground max-w-[80%] rounded-lg p-4">
              {streamingQuery ? (
                <StreamingResponse 
                  query={streamingQuery} 
                  onComplete={handleStreamingComplete}
                  showSources={false}
                />
              ) : (
                <div className="flex space-x-2 items-center">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Thinking...</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Sources section */}
        {showSources && currentSources.length > 0 && (
          <Card className="p-4 bg-muted/50">
            <h4 className="font-semibold mb-2">Sources</h4>
            <div className="space-y-2">
              {currentSources.map((source, index) => (
                <div key={index} className="text-sm">
                  <div className="font-medium">{source.title || 'Source ' + (index + 1)}</div>
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
          </Card>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t bg-background rounded-b-lg">
        {/* File upload progress */}
        {isUploading && (
          <div className="mb-4">
            <div className="flex justify-between text-xs mb-1">
              <span>Uploading {fileUpload?.name}...</span>
              <span>{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="h-2" />
          </div>
        )}
        
        {/* File display if uploaded but not uploading */}
        {fileUpload && !isUploading && (
          <div className="flex items-center justify-between bg-muted p-2 rounded-md mb-4">
            <div className="flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              <span className="text-sm truncate max-w-[200px]">{fileUpload.name}</span>
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
        
        <div className="flex space-x-2">
          <div className="relative flex-grow">
            <Textarea
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="min-h-[80px] resize-none pr-10"
              disabled={isStreaming}
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
              disabled={isStreaming || isUploading || fileUpload}
            >
              <FileUp className="h-4 w-4" />
            </Button>
          </div>
          <Button
            onClick={handleSendMessage}
            disabled={isStreaming || (!inputValue.trim() && !fileUpload)}
            className="self-end"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        <div className="mt-2 text-xs text-muted-foreground flex items-center">
          <AlertCircle className="h-3 w-3 mr-1" />
          Ask about clean energy careers, training programs, or upload your resume for personalized recommendations
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
    </div>
  );
}
