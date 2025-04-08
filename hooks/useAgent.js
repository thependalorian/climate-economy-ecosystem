'use client';

import { useState, useCallback, useEffect } from 'react';
import { agentClient } from '@/lib/client/agent-client';
import { useAuth } from '@/hooks/useAuth';
import { useMetrics } from '@/hooks/useMetrics';

/**
 * useAgent Hook
 * 
 * A custom React hook for interacting with specialized agents in the
 * Climate Economy Ecosystem.
 * 
 * @returns {Object} Object containing agent state and methods
 */
export function useAgent() {
  const { user } = useAuth();
  const { trackEvent } = useMetrics();
  
  const [agents, setAgents] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [currentAgent, setCurrentAgent] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  
  // Initialize session ID and fetch agents on mount
  useEffect(() => {
    // Generate a session ID
    setSessionId(crypto.randomUUID());
    
    // Fetch available agents
    const fetchAgents = async () => {
      try {
        const agentList = await agentClient.listAgents();
        setAgents(agentList);
      } catch (err) {
        console.error('Error fetching agents:', err);
        setError('Failed to fetch available agents');
      }
    };
    
    fetchAgents();
  }, []);
  
  /**
   * Send a message to the appropriate agent
   * 
   * @param {string} message - User message
   * @param {string} [agentType] - Force specific agent type (optional)
   * @returns {Promise<Object>} - Chat response
   */
  const sendMessage = useCallback(async (message, agentType = null) => {
    if (!user) {
      setError('You must be logged in to chat with agents');
      return null;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Track the start time for metrics
      const startTime = Date.now();
      
      // Add user message to chat history
      const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      
      setChatHistory(prev => [...prev, userMessage]);
      
      // Send message to agent
      const response = await agentClient.chatWithAgent({
        userId: user.id,
        query: message,
        sessionId,
        agentType
      });
      
      // Calculate response time
      const responseTime = Date.now() - startTime;
      
      // Track metrics
      trackEvent('agent_chat', {
        agent_type: response.agent_type,
        agent_name: response.agent_name,
        query_length: message.length,
        response_length: response.response.length,
        response_time_ms: responseTime
      });
      
      // Update current agent
      setCurrentAgent({
        type: response.agent_type,
        name: response.agent_name
      });
      
      // Add agent response to chat history
      const agentMessage = {
        role: 'assistant',
        content: response.response,
        agent: {
          type: response.agent_type,
          name: response.agent_name
        },
        timestamp: response.timestamp,
        interactionId: response.interaction_id
      };
      
      setChatHistory(prev => [...prev, agentMessage]);
      
      return response;
    } catch (err) {
      console.error('Error sending message to agent:', err);
      setError(err.message || 'Failed to send message to agent');
      
      // Track error
      trackEvent('agent_chat_error', {
        error_message: err.message || 'Unknown error',
        query: message
      });
      
      return null;
    } finally {
      setLoading(false);
    }
  }, [user, sessionId, trackEvent]);
  
  /**
   * Clear chat history
   */
  const clearChat = useCallback(() => {
    setChatHistory([]);
    // Generate a new session ID
    setSessionId(crypto.randomUUID());
    
    // Track clear chat event
    trackEvent('clear_chat', {
      previous_session_id: sessionId
    });
  }, [sessionId, trackEvent]);
  
  return {
    agents,
    loading,
    error,
    sessionId,
    currentAgent,
    chatHistory,
    sendMessage,
    clearChat
  };
}
