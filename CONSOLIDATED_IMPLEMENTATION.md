# Consolidated Implementation Plan

Based on our analysis of the codebase, we've identified several areas that need to be updated to use our consolidated services. Here's a detailed plan for implementing these changes:

## 1. Files to Delete

After implementing our consolidated services, we can delete these redundant files:

- `lib/memory/mock_mem0_service.py` - Replaced by our consolidated memory service
- `graph/climate_state_updated.py` - Merged into `graph/climate_state.py`

## 2. API Routes to Update

### 2.1. Update app/api/climate-chat/route.py

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import os
import time
import openai
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import consolidated services
from lib.memory.memory_service import MemoryService, ClimateMemoryEntry, MemoryServiceError
from lib.redis.redis_service import RedisService, RedisServiceError
from lib.tracing.langsmith_service import TracingService, TracingServiceError

# Import tools
from tools.base_tool import BaseTool, ToolError
from tools.ej_geospatial import EJGeospatialTool
from tools.international_credential_evaluator import InternationalCredentialEvaluator

# Load environment variables
load_dotenv()

# Initialize services
memory_service = MemoryService()
redis_service = RedisService()
tracing_service = TracingService()

# Initialize tools
ej_geospatial_tool = EJGeospatialTool()
international_credential_evaluator = InternationalCredentialEvaluator()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI()

SYSTEM_PROMPT = """You are a specialized assistant for the Massachusetts Clean Tech Ecosystem. Your purpose is to help individuals in Massachusetts find jobs, training, and resources in the clean energy economy.

You have access to information about:
1. Clean energy jobs in Massachusetts
2. Training programs and educational opportunities
3. Massachusetts climate reports and policies
4. Environmental Justice communities and resources
5. Support for international professionals

Be helpful, accurate, and focus on Massachusetts-specific information when possible.
"""

async def get_relevant_context(query: str, user_id: str, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get relevant context from memory and web search for the climate chat"""
    try:
        # Create a trace for context retrieval
        with tracing_service.trace(
            name="get_relevant_context",
            run_id=run_id or tracing_service.create_run_id(),
            inputs={"query": query, "user_id": user_id}
        ) as trace_run:
            # Try to get cached context first
            try:
                cache_key = f"context:{user_id}:{query}"
                cached_context = await redis_service.get(cache_key)
                if cached_context:
                    trace_run.end(outputs={"source": "cache", "context_count": len(cached_context)})
                    return cached_context
            except RedisServiceError:
                # Continue if Redis is unavailable
                pass
            
            context = []
            
            # First, try to get information from memory
            try:
                # Search user's memories
                memory_results = await memory_service.search_memories(
                    query=query,
                    user_id=user_id,
                    limit=5,
                    categories=["report", "job", "training"]
                )
                
                # Add memory results to context
                for result in memory_results:
                    context.append({
                        "source": "memory",
                        "content": result["content"],
                        "metadata": result["metadata"],
                        "relevance_score": result.get("relevance_score", 0.0)
                    })
                    
            except MemoryServiceError as e:
                # Log the error but continue
                print(f"Error searching memories: {str(e)}")
            
            # If we have EJ community data, add it to the context
            try:
                # Get user profile
                user_profile = await memory_service.get_user_profile(user_id)
                
                if user_profile and user_profile.is_ej_community and user_profile.location:
                    # Get EJ community data
                    ej_data = await ej_geospatial_tool.run(
                        action="get_community_profile",
                        city=user_profile.location
                    )
                    
                    if ej_data:
                        context.append({
                            "source": "ej_data",
                            "content": f"The user is from {user_profile.location}, which is an Environmental Justice community with the following characteristics: {json.dumps(ej_data)}",
                            "metadata": {"type": "ej_community_data"},
                            "relevance_score": 0.9  # High relevance for personalized data
                        })
            except Exception as e:
                # Log the error but continue
                print(f"Error getting EJ data: {str(e)}")
            
            # If we have international professional data, add it to the context
            try:
                if user_profile and user_profile.has_international_credentials and user_profile.origin_country:
                    # Get international credential data
                    credential_data = user_profile.international_credentials
                    
                    if credential_data:
                        context.append({
                            "source": "international_data",
                            "content": f"The user is an international professional from {user_profile.origin_country} with credentials that may need evaluation: {json.dumps(credential_data)}",
                            "metadata": {"type": "international_credential_data"},
                            "relevance_score": 0.9  # High relevance for personalized data
                        })
            except Exception as e:
                # Log the error but continue
                print(f"Error getting international data: {str(e)}")
            
            # Sort by relevance score
            context.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Limit to top 5 most relevant items
            context = context[:5]
            
            # Cache the context in Redis if available
            try:
                cache_key = f"context:{user_id}:{query}"
                await redis_service.set(cache_key, context, 3600)  # Cache for 1 hour
            except RedisServiceError:
                # Continue if Redis is unavailable
                pass
            
            # End the trace with the final context
            trace_run.end(outputs={
                "context_count": len(context),
                "sources": [item["source"] for item in context]
            })
            
            return context
    except Exception as e:
        print(f"Error getting relevant context: {str(e)}")
        # If there's an error, return an empty context
        return []

async def chat_completion_with_streaming(query: str, user_id: str, stream_tokens: bool = False):
    """Generate a chat completion with optional streaming"""
    # Create a run ID for tracing
    run_id = tracing_service.create_run_id()
    
    try:
        # Create a trace for the chat completion
        with tracing_service.trace(
            name="climate_chat_completion",
            run_id=run_id,
            inputs={"query": query, "user_id": user_id, "stream_tokens": stream_tokens}
        ) as trace_run:
            start_time = time.time()
            
            # Get relevant context
            context = await get_relevant_context(query, user_id, run_id)
            
            # Format context for the prompt
            context_text = ""
            for item in context:
                source = item["source"]
                content = item["content"]
                context_text += f"[{source}]\n{content}\n\n"
            
            # Create messages for the chat completion
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"Context information:\n{context_text}"},
                {"role": "user", "content": query}
            ]
            
            # Generate completion
            if stream_tokens:
                # Stream the response
                completion_stream = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    stream=True
                )
                
                # Define the generator function for streaming
                async def generate():
                    try:
                        # Start the response
                        yield "data: {\"type\": \"start\", \"run_id\": \"" + run_id + "\"}\n\n"
                        
                        # Stream the tokens
                        full_response = ""
                        for chunk in completion_stream:
                            if chunk.choices and chunk.choices[0].delta.content:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                        
                        # End the response
                        end_time = time.time()
                        duration_ms = int((end_time - start_time) * 1000)
                        
                        # Store the response in memory
                        try:
                            memory_entry = ClimateMemoryEntry(
                                content=full_response,
                                user_id=user_id,
                                category="chat",
                                metadata={
                                    "query": query,
                                    "timestamp": time.time(),
                                    "context_sources": [item["source"] for item in context]
                                }
                            )
                            await memory_service.add_memory(memory_entry)
                        except MemoryServiceError as e:
                            print(f"Error storing chat in memory: {str(e)}")
                        
                        # End the trace
                        trace_run.end(outputs={
                            "response_length": len(full_response),
                            "response_time_ms": duration_ms
                        })
                        
                        yield f"data: {json.dumps({'type': 'end', 'duration_ms': duration_ms})}\n\n"
                    except Exception as e:
                        error_msg = str(e)
                        print(f"Error in streaming: {error_msg}")
                        yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                
                return generate()
            else:
                # Generate the full response at once
                completion = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7
                )
                
                response = completion.choices[0].message.content
                
                # Store the response in memory
                try:
                    memory_entry = ClimateMemoryEntry(
                        content=response,
                        user_id=user_id,
                        category="chat",
                        metadata={
                            "query": query,
                            "timestamp": time.time(),
                            "context_sources": [item["source"] for item in context]
                        }
                    )
                    await memory_service.add_memory(memory_entry)
                except MemoryServiceError as e:
                    print(f"Error storing chat in memory: {str(e)}")
                
                # End the trace
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                trace_run.end(outputs={
                    "response_length": len(response),
                    "response_time_ms": duration_ms
                })
                
                return {
                    "response": response,
                    "run_id": run_id,
                    "duration_ms": duration_ms
                }
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat completion: {error_msg}")
        return {
            "error": "Error generating response",
            "message": error_msg
        }

@app.post("/api/climate-chat")
async def climate_chat(request: Request):
    """API endpoint for climate chat"""
    try:
        # Parse request
        data = await request.json()
        query = data.get("query")
        user_id = data.get("user_id")
        stream_tokens = data.get("stream_tokens", False)
        
        # Validate request
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Generate response
        if stream_tokens:
            # Return streaming response
            return StreamingResponse(
                chat_completion_with_streaming(query, user_id, True),
                media_type="text/event-stream"
            )
        else:
            # Return regular response
            return await chat_completion_with_streaming(query, user_id, False)
    except Exception as e:
        # Handle errors
        error_msg = str(e)
        print(f"Error in climate chat endpoint: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
```

### 2.2. Update app/api/assistant/chat/route.js

```javascript
import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { MemoryService } from '@/lib/memory/memory-service';
import { RedisCache } from '@/lib/redis/redis-client';
import { tracingService } from '@/lib/tracing/langsmith-client';

export async function POST(req) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // Parse request
    const { query, stream = false } = await req.json();
    const userId = session.user.id;
    
    // Validate request
    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }
    
    // Initialize services
    const memoryService = new MemoryService();
    const redisCache = new RedisCache();
    
    // Create a unique run ID for tracing
    const runId = tracingService.createRunId();
    
    // Try to get cached response
    try {
      const cacheKey = `chat:${userId}:${query}`;
      const cachedResponse = await redisCache.get(cacheKey);
      if (cachedResponse) {
        return NextResponse.json({ 
          response: cachedResponse.response,
          cached: true 
        });
      }
    } catch (error) {
      console.error('Cache error:', error);
      // Continue without caching
    }
    
    // Create a tracer
    const tracer = tracingService.createTracer(runId, 'chat_response');
    
    try {
      // Make API call to the Python backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/climate-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          user_id: userId,
          stream_tokens: stream
        }),
      });
      
      // Handle streaming response
      if (stream) {
        // Return the streaming response
        return new Response(response.body, {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
          },
        });
      }
      
      // Handle regular response
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error from backend');
      }
      
      const data = await response.json();
      
      // Try to cache the response
      try {
        await redisCache.set(`chat:${userId}:${query}`, data, 3600);
      } catch (error) {
        console.error('Cache error:', error);
        // Continue without caching
      }
      
      // End trace
      tracer.end();
      
      return NextResponse.json(data);
    } catch (error) {
      console.error('Error in chat:', error);
      
      // Record error in trace
      try {
        const errorSpan = tracer.startSpan({
          name: 'error',
          inputs: { error: error.message },
          runType: 'chain'
        });
        
        errorSpan.end();
        tracer.end();
      } catch (tracingError) {
        console.error('Error recording tracing:', tracingError);
      }
      
      return NextResponse.json(
        { error: 'Error generating response', message: error.message },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Unhandled error:', error);
    return NextResponse.json(
      { error: 'Unhandled error', message: error.message },
      { status: 500 }
    );
  }
}
```

### 2.3. Update app/api/assistant/history/route.js

```javascript
import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { MemoryService } from '@/lib/memory/memory-service';
import { RedisCache } from '@/lib/redis/redis-client';

export async function GET(req) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // Get user ID
    const userId = session.user.id;
    
    // Initialize services
    const memoryService = new MemoryService();
    const redisCache = new RedisCache();
    
    // Try to get cached history
    try {
      const cacheKey = `history:${userId}`;
      const cachedHistory = await redisCache.get(cacheKey);
      if (cachedHistory) {
        return NextResponse.json({ 
          history: cachedHistory,
          cached: true 
        });
      }
    } catch (error) {
      console.error('Cache error:', error);
      // Continue without caching
    }
    
    try {
      // Get chat history from memory service
      const history = await memoryService.search_memories(
        "",  // Empty query to get all memories
        userId,
        20,  // Limit to 20 most recent
        ["chat"]  // Only get chat memories
      );
      
      // Format history
      const formattedHistory = history.map(item => ({
        id: item.id,
        query: item.metadata?.query || "",
        response: item.content,
        timestamp: item.metadata?.timestamp || new Date().toISOString()
      }));
      
      // Sort by timestamp (newest first)
      formattedHistory.sort((a, b) => b.timestamp - a.timestamp);
      
      // Try to cache the history
      try {
        await redisCache.set(`history:${userId}`, formattedHistory, 300);  // Cache for 5 minutes
      } catch (error) {
        console.error('Cache error:', error);
        // Continue without caching
      }
      
      return NextResponse.json({ history: formattedHistory });
    } catch (error) {
      console.error('Error getting chat history:', error);
      return NextResponse.json(
        { error: 'Error getting chat history', message: error.message },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Unhandled error:', error);
    return NextResponse.json(
      { error: 'Unhandled error', message: error.message },
      { status: 500 }
    );
  }
}
```

### 2.4. Update app/api/assistant/clear/route.js

```javascript
import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { MemoryService } from '@/lib/memory/memory-service';
import { RedisCache } from '@/lib/redis/redis-client';

export async function POST(req) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // Get user ID
    const userId = session.user.id;
    
    // Initialize services
    const memoryService = new MemoryService();
    const redisCache = new RedisCache();
    
    try {
      // Get chat history from memory service
      const history = await memoryService.search_memories(
        "",  // Empty query to get all memories
        userId,
        100,  // Get up to 100 memories
        ["chat"]  // Only get chat memories
      );
      
      // Delete each memory
      let deletedCount = 0;
      for (const item of history) {
        await memoryService.delete_memory(item.id);
        deletedCount++;
      }
      
      // Clear cache
      try {
        await redisCache.invalidatePattern(`*:${userId}:*`);
        await redisCache.delete(`history:${userId}`);
      } catch (error) {
        console.error('Cache error:', error);
        // Continue without caching
      }
      
      return NextResponse.json({ 
        success: true, 
        message: `Cleared ${deletedCount} chat messages` 
      });
    } catch (error) {
      console.error('Error clearing chat history:', error);
      return NextResponse.json(
        { error: 'Error clearing chat history', message: error.message },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Unhandled error:', error);
    return NextResponse.json(
      { error: 'Unhandled error', message: error.message },
      { status: 500 }
    );
  }
}
```

## 3. Middleware Updates

### 3.1. Update middleware.js

```javascript
import { NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { tracingService } from '@/lib/tracing/langsmith-client';

export async function middleware(request) {
  // Create a unique run ID for tracing
  const runId = tracingService.createRunId();
  
  // Create a tracer
  const tracer = tracingService.createTracer(runId, 'middleware');
  
  try {
    // Start span
    const span = tracer.startSpan({
      name: 'middleware_request',
      inputs: { 
        path: request.nextUrl.pathname,
        method: request.method
      },
      runType: 'chain'
    });
    
    // Check if the request is for an API route
    if (request.nextUrl.pathname.startsWith('/api/')) {
      // For API routes, check authentication
      const token = await getToken({ req: request });
      
      // If no token and not a public API route, redirect to login
      if (!token && !isPublicApiRoute(request.nextUrl.pathname)) {
        span.end({
          outputs: { 
            result: 'unauthorized',
            redirect: '/api/auth/signin'
          }
        });
        
        tracer.end();
        
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }
    }
    
    // End span with success
    span.end({
      outputs: { 
        result: 'success'
      }
    });
    
    tracer.end();
    
    // Continue with the request
    return NextResponse.next();
  } catch (error) {
    console.error('Middleware error:', error);
    
    // Record error in trace
    try {
      const errorSpan = tracer.startSpan({
        name: 'middleware_error',
        inputs: { error: error.message },
        runType: 'chain'
      });
      
      errorSpan.end();
      tracer.end();
    } catch (tracingError) {
      console.error('Error recording tracing:', tracingError);
    }
    
    // Continue with the request despite the error
    return NextResponse.next();
  }
}

// Define which API routes are public
function isPublicApiRoute(pathname) {
  const publicRoutes = [
    '/api/auth',
    '/api/health',
    '/api/public'
  ];
  
  return publicRoutes.some(route => pathname.startsWith(route));
}

// Configure which routes use this middleware
export const config = {
  matcher: [
    '/api/:path*',
    '/dashboard/:path*',
    '/profile/:path*'
  ]
};
```

## 4. Hooks Updates

### 4.1. Update hooks/useMetrics.js

```javascript
import { useCallback } from 'react';
import { tracingService } from '@/lib/tracing/langsmith-client';

export function useMetrics() {
  const trackEvent = useCallback(async (eventName, eventData) => {
    try {
      // Create a unique run ID for tracing
      const runId = tracingService.createRunId();
      
      // Log the event
      await tracingService.logLlmCall(
        'metrics',
        eventName,
        JSON.stringify(eventData),
        runId,
        { event_type: 'client_side_metric' }
      );
      
      // Also send to backend API
      await fetch('/api/metrics/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_name: eventName,
          event_data: eventData,
          run_id: runId
        }),
      });
    } catch (error) {
      console.error('Error tracking metric:', error);
      // Silently fail - metrics should not break the app
    }
  }, []);
  
  const trackPageView = useCallback((page) => {
    trackEvent('page_view', { page });
  }, [trackEvent]);
  
  const trackSearch = useCallback((query, resultsCount) => {
    trackEvent('search', { query, results_count: resultsCount });
  }, [trackEvent]);
  
  const trackChatCompletion = useCallback((query, responseTimeMs) => {
    trackEvent('chat_completion', { query, response_time_ms: responseTimeMs });
  }, [trackEvent]);
  
  const trackError = useCallback((errorType, errorMessage) => {
    trackEvent('error', { error_type: errorType, error_message: errorMessage });
  }, [trackEvent]);
  
  return {
    trackEvent,
    trackPageView,
    trackSearch,
    trackChatCompletion,
    trackError
  };
}
```

### 4.2. Update hooks/useAuth.js

```javascript
import { useSession, signIn, signOut } from 'next-auth/react';
import { useCallback } from 'react';
import { tracingService } from '@/lib/tracing/langsmith-client';

export function useAuth() {
  const { data: session, status } = useSession();
  
  const login = useCallback(async (provider = 'google') => {
    try {
      // Track login attempt
      const runId = tracingService.createRunId();
      tracingService.logLlmCall(
        'auth',
        'login_attempt',
        provider,
        runId,
        { auth_action: 'login_attempt' }
      );
      
      // Perform login
      await signIn(provider);
      
      // Track successful login
      tracingService.logLlmCall(
        'auth',
        'login_success',
        provider,
        runId,
        { auth_action: 'login_success' }
      );
    } catch (error) {
      console.error('Login error:', error);
      
      // Track login error
      tracingService.logLlmCall(
        'auth',
        'login_error',
        error.message,
        null,
        { auth_action: 'login_error' }
      );
      
      throw error;
    }
  }, []);
  
  const logout = useCallback(async () => {
    try {
      // Track logout
      tracingService.logLlmCall(
        'auth',
        'logout',
        '',
        null,
        { auth_action: 'logout' }
      );
      
      // Perform logout
      await signOut();
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }, []);
  
  return {
    session,
    status,
    isAuthenticated: status === 'authenticated',
    isLoading: status === 'loading',
    user: session?.user,
    login,
    logout
  };
}
```

## 5. Implementation Steps

1. Create the consolidated service files:
   - `lib/memory/memory_service.py`
   - `lib/redis/redis_service.py`
   - `lib/tracing/langsmith_service.py`
   - `lib/redis/redis-client.js`
   - `lib/tracing/langsmith-client.js`

2. Update the base tool class:
   - `tools/base_tool.py`

3. Update the EJ Geospatial Tool:
   - `tools/ej_geospatial.py`

4. Update the International Credential Evaluator:
   - `tools/international_credential_evaluator.py`

5. Update the API routes:
   - `app/api/climate-chat/route.py`
   - `app/api/assistant/chat/route.js`
   - `app/api/assistant/history/route.js`
   - `app/api/assistant/clear/route.js`

6. Update the middleware and hooks:
   - `middleware.js`
   - `hooks/useMetrics.js`
   - `hooks/useAuth.js`

7. Delete redundant files:
   - `lib/memory/mock_mem0_service.py`
   - `graph/climate_state_updated.py`

8. Test the implementation:
   - Test each API route
   - Test error handling
   - Test performance with and without caching
   - Test tracing functionality

This implementation plan ensures that we have a robust, consolidated codebase with proper error handling and no mock fallbacks.
