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
