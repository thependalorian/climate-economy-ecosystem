'use client';

import { useState, useRef, useEffect } from 'react';
import { useAgent } from '@/hooks/useAgent';
import { useAuth } from '@/hooks/useAuth';

/**
 * AgentChat Component
 * 
 * A React component for chatting with specialized agents in the
 * Climate Economy Ecosystem.
 * 
 * @param {Object} props - Component props
 * @param {string} [props.initialMessage] - Initial message to send to agent
 * @param {string} [props.agentType] - Force specific agent type
 * @returns {React.ReactNode} The rendered component
 */
export default function AgentChat({ initialMessage, agentType }) {
  const { isAuthenticated, user } = useAuth();
  const { 
    agents, 
    loading, 
    error, 
    currentAgent, 
    chatHistory, 
    sendMessage, 
    clearChat 
  } = useAgent();
  
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef(null);
  
  // Send initial message if provided
  useEffect(() => {
    if (initialMessage && isAuthenticated) {
      sendMessage(initialMessage, agentType);
    }
  }, [initialMessage, agentType, isAuthenticated, sendMessage]);
  
  // Scroll to bottom when chat history changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);
  
  // Handle message submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    await sendMessage(message, agentType);
    setMessage('');
  };
  
  // Render agent avatar
  const renderAgentAvatar = (agent) => {
    if (!agent) return null;
    
    // Agent-specific avatars
    const avatars = {
      pendo: '👩‍💼', // Main assistant
      jasmine: '👩‍🌾', // EJ specialist
      marcus: '👨‍✈️', // Military specialist
      miguel: '👨‍🎓'  // International specialist
    };
    
    return (
      <div className="flex items-center">
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-lg mr-2">
          {avatars[agent.type] || '🤖'}
        </div>
        <span className="font-medium">{agent.name}</span>
      </div>
    );
  };
  
  if (!isAuthenticated) {
    return (
      <div className="p-4 bg-yellow-50 rounded-lg">
        <p className="text-yellow-700">Please log in to chat with our specialized agents.</p>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden">
      {/* Chat header */}
      <div className="bg-gray-100 p-4 border-b flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold">Climate Economy Assistant</h2>
          {currentAgent && (
            <p className="text-sm text-gray-600">
              Currently chatting with {currentAgent.name}
            </p>
          )}
        </div>
        <button
          onClick={clearChat}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          Clear Chat
        </button>
      </div>
      
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.length === 0 ? (
          <div className="text-center text-gray-500 my-8">
            <p>Start a conversation with our specialized agents.</p>
            <p className="text-sm mt-2">
              We have experts in Environmental Justice communities, military transition,
              and international credential evaluation.
            </p>
          </div>
        ) : (
          chatHistory.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-3/4 p-3 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-blue-100 text-blue-900'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                {msg.role === 'assistant' && msg.agent && (
                  <div className="mb-1">{renderAgentAvatar(msg.agent)}</div>
                )}
                <div className="whitespace-pre-wrap">{msg.content}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-3 bg-red-50 border-t border-red-200">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}
      
      {/* Chat input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
            disabled={loading || !message.trim()}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}
