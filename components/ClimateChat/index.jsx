"use client";

import { useState, useRef, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { Send, Link as LinkIcon, Loader } from 'lucide-react';

/**
 * ClimateChat Component 
 * An AI assistant that provides information on clean energy opportunities in Massachusetts
 * Following ACT brand guidelines
 * Location: /components/ClimateChat/index.jsx
 */
export default function ClimateChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { data: session } = useSession();
  const [sources, setSources] = useState([]);
  const [showSources, setShowSources] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim() === '') return;
    
    // Add user message to chat
    const userMessage = { role: 'user', content: input.trim() };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    
    // Clear input and set loading
    setInput('');
    setLoading(true);
    
    try {
      // Call chat API
      const response = await fetch('/api/climate-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content,
          user_id: session?.user?.id || 'anonymous',
          stream: false, // Not using streaming for now
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      const data = await response.json();
      
      // Add assistant message to chat
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: 'assistant', content: data.text }
      ]);
      
      // Store sources if available
      if (data.sources && data.sources.length > 0) {
        setSources(data.sources);
      } else {
        setSources([]);
      }
      
    } catch (error) {
      console.error('Error calling climate chat API:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error. Please try again later.' 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSources = () => {
    setShowSources(!showSources);
  };

  return (
    <div className="card bg-base-100 border-2 border-spring-green h-[600px] flex flex-col">
      <div className="card-title bg-base-300 p-4 rounded-t-lg">
        <h3 className="text-xl font-bold">Massachusetts Clean Tech Assistant</h3>
        {sources.length > 0 && (
          <button 
            className="btn btn-ghost btn-sm"
            onClick={toggleSources}
          >
            <LinkIcon className="text-secondary" size={16} />
          </button>
        )}
      </div>
      
      <div className="card-body p-0 flex-grow overflow-y-auto">
        <div className="p-4">
          {messages.length === 0 ? (
            <div className="text-center text-secondary my-8">
              <p className="text-lg font-medium mb-2">How can I help you today?</p>
              <p className="text-sm mb-6">Ask about clean energy jobs, training programs, or resources in Massachusetts.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-4">
                <SuggestionButton 
                  text="Clean energy jobs near Boston" 
                  onClick={() => {
                    setInput("What clean energy jobs are available near Boston?");
                    handleSubmit({preventDefault: () => {}});
                  }}
                />
                <SuggestionButton 
                  text="Translate military skills" 
                  onClick={() => {
                    setInput("How can I translate my military experience to clean energy careers?");
                    handleSubmit({preventDefault: () => {}});
                  }}
                />
                <SuggestionButton 
                  text="International credentials" 
                  onClick={() => {
                    setInput("How can I get my international engineering degree recognized in Massachusetts?");
                    handleSubmit({preventDefault: () => {}});
                  }}
                />
                <SuggestionButton 
                  text="Gateway Cities opportunities" 
                  onClick={() => {
                    setInput("What clean energy opportunities are available in Gateway Cities?");
                    handleSubmit({preventDefault: () => {}});
                  }}
                />
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div 
                  key={index} 
                  className={`chat ${
                    message.role === 'user' 
                      ? 'chat-end' 
                      : 'chat-start'
                  }`}
                >
                  <div className={`chat-bubble ${
                    message.role === 'user' 
                      ? 'chat-bubble-primary' 
                      : 'chat-bubble-secondary'
                  }`}>
                    {message.content}
                  </div>
                </div>
              ))}
            </>
          )}
          {loading && (
            <div className="chat chat-start">
              <div className="chat-bubble chat-bubble-secondary">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          {showSources && sources.length > 0 && (
            <div className="mt-4 bg-base-200 rounded-lg text-sm p-4 border border-spring-green/20">
              <p className="font-medium mb-2">Sources:</p>
              <ul className="space-y-1">
                {sources.map((source, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2 text-primary">•</span>
                    {source.url ? (
                      <a 
                        href={source.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-secondary hover:text-primary transition-colors break-all"
                      >
                        {source.url}
                      </a>
                    ) : (
                      <span className="text-secondary">Internal database</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <div className="card-actions justify-center p-4 border-t border-base-300">
        <form onSubmit={handleSubmit} className="flex space-x-2 w-full">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about clean energy in Massachusetts..."
            className="input input-bordered w-full"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={loading || input.trim() === ''}
          >
            {loading ? (
              <Loader className="animate-spin" size={18} />
            ) : (
              <Send size={18} />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

function SuggestionButton({ text, onClick }) {
  return (
    <button
      onClick={onClick}
      className="btn btn-outline btn-sm btn-block justify-start text-left normal-case font-normal"
    >
      {text}
    </button>
  );
} 