# Agent Integration Documentation

This document outlines the integration of specialized agents into the Climate Economy Ecosystem platform. It covers the agent architecture, state management, API endpoints, middleware, and frontend components.

## Table of Contents

1. [Agent Architecture](#agent-architecture)
2. [Prompt System](#prompt-system)
3. [State Management](#state-management)
4. [API Endpoints](#api-endpoints)
5. [Middleware](#middleware)
6. [Frontend Integration](#frontend-integration)
7. [Tracking and Metrics](#tracking-and-metrics)
8. [Deployment Considerations](#deployment-considerations)

## Agent Architecture

The Climate Economy Ecosystem uses a specialized agent architecture with four distinct agent personas:

### Agent Personas

1. **Pendo (Main Climate Economy Assistant)**
   - Primary assistant for general climate economy queries
   - Comprehensive knowledge of Massachusetts clean energy sector

2. **Jasmine (Environmental Justice Community Specialist)**
   - Specialized in Gateway Cities and EJ communities
   - Expertise in transportation barriers, community-based approaches
   - Supports diverse educational backgrounds (vocational, trades, university, workforce reentry)

3. **Marcus (Military Transition Specialist)**
   - Specialized in veteran transition to clean energy careers
   - Expertise in military skill translation, veteran benefits
   - Support for veteran entrepreneurship

4. **Miguel (International Credential Specialist)**
   - Specialized in international credential evaluation
   - Expertise in regulatory requirements, cultural integration
   - Support for international professionals entering the US workforce

### Agent Router

The `AgentRouter` class in `lib/agents/agent_router.py` handles:

1. Determining which agent should handle a query based on user profile and query content
2. Selecting the appropriate specialized prompt
3. Tracking agent interactions for metrics and improvement
4. Managing state across interactions

## Prompt System

The prompt system is organized into specialized modules:

1. **Agent Personas (`prompts/agent_personas.py`)**
   - Defines each agent's persona, backstory, expertise, and personality
   - Includes example outputs and constraints

2. **EJ Prompts (`prompts/ej_prompts.py`)**
   - Specialized prompts for Environmental Justice communities
   - Includes prompts for different educational backgrounds
   - Addresses transportation, community resources, and multilingual support

3. **Military Prompts (`prompts/military_prompts.py`)**
   - Specialized prompts for military transition
   - Includes skill translation, education benefits, entrepreneurship

4. **International Prompts (`prompts/international_prompts.py`)**
   - Specialized prompts for international professionals
   - Includes credential evaluation, cultural integration, resume adaptation

All prompts include strict constraints:
- Only recommend ecosystem partners
- Always reference sources
- Focus on Massachusetts-specific opportunities
- Provide realistic timelines and costs

## State Management

State management is handled through several services:

1. **Memory Service (`lib/memory/memory_service.py`)**
   - Stores user profiles, chat history, and agent interactions
   - Provides persistence across sessions
   - Enables personalized agent selection

2. **Redis Service (`lib/redis/redis_service.py`)**
   - Caches agent selections and frequently used data
   - Improves performance for repeated queries
   - Enables session management

3. **Tracing Service (`lib/tracing/langsmith_service.py`)**
   - Tracks agent interactions for monitoring and debugging
   - Enables performance analysis
   - Supports continuous improvement of agents

## API Endpoints

The agent system exposes the following API endpoints:

1. **Chat with Agent (`POST /api/climate-chat/agent`)**
   - Routes user queries to the appropriate agent
   - Returns agent responses with metadata
   - Supports forcing specific agent types

2. **List Agents (`GET /api/climate-chat/agents`)**
   - Returns a list of available agents
   - Includes agent names and types

API implementation is in `app/api/climate-chat/agent_route.py`.

## Middleware

The middleware layer handles:

1. **Authentication**
   - Ensures users are authenticated before accessing agents
   - Associates queries with user profiles

2. **Tracing**
   - Tracks API calls and agent interactions
   - Enables performance monitoring

3. **Error Handling**
   - Provides consistent error responses
   - Logs errors for debugging

Middleware implementation is in `middleware.js`.

## Frontend Integration

The frontend integration includes:

1. **Agent Client (`lib/client/agent-client.js`)**
   - JavaScript client for interacting with agent API
   - Handles authentication, tracing, and error handling

2. **useAgent Hook (`hooks/useAgent.js`)**
   - React hook for using agents in components
   - Manages chat state, history, and sessions

3. **AgentChat Component (`components/AgentChat.jsx`)**
   - React component for chatting with agents
   - Displays agent avatars and responses
   - Handles message submission and history

## Tracking and Metrics

The agent system includes comprehensive tracking:

1. **Interaction Tracking**
   - Tracks which agent handled each query
   - Records query and response content
   - Measures response times

2. **Session Tracking**
   - Groups interactions into sessions
   - Enables analysis of conversation flows

3. **User Tracking**
   - Associates interactions with user profiles
   - Enables personalized agent selection

4. **Performance Metrics**
   - Measures response times and quality
   - Identifies areas for improvement

## Deployment Considerations

When deploying the agent system:

1. **Environment Variables**
   - Set `LANGSMITH_API_KEY` for tracing
   - Configure `REDIS_URL` for caching
   - Set `OPENAI_API_KEY` for LLM access

2. **Database Migrations**
   - Ensure Supabase tables are set up for agent tracking
   - Run migrations before deploying

3. **Scaling**
   - Configure Redis for high availability
   - Set appropriate timeouts for LLM calls
   - Consider load balancing for high traffic

4. **Monitoring**
   - Set up alerts for agent errors
   - Monitor response times and quality
   - Track usage patterns for capacity planning
