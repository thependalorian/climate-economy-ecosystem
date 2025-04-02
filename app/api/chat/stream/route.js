import { NextResponse } from 'next/server';
import { metrics_service } from '@/lib/monitoring/metrics_service';
import { auth } from '@/auth';
import { createLangSmithClient, LangChainTracer } from 'langsmith';
import { OpenAI } from 'openai';
import { v4 as uuidv4 } from 'uuid';
import { createClient } from '@supabase/supabase-js';

/**
 * Streaming Chat API Endpoint
 * Provides real-time token-by-token chat responses with
 * integrated LangSmith tracing and metrics tracking.
 * Location: /app/api/chat/stream/route.js
 */

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Initialize LangSmith client
const langsmith = createLangSmithClient({
  apiKey: process.env.LANGSMITH_API_KEY,
  projectName: 'climate-economy-chat'
});

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// System prompt
const SYSTEM_PROMPT = `You are a specialized assistant for the Massachusetts Clean Tech Ecosystem. Your purpose is to help individuals in Massachusetts find jobs, training, and resources in the clean energy economy.

Special considerations:
1. For Veterans: Help translate military experience to clean energy careers
2. For International Professionals: Help evaluate overseas credentials for Massachusetts 
3. For Environmental Justice Communities: Prioritize opportunities in Gateway Cities

Focus on Massachusetts-specific information whenever possible. If you don't have specific Massachusetts information, clearly indicate this.

Your tone should be helpful, informative, and encouraging.

Format your responses using markdown for better readability. Use bullet points, headers, and other formatting when appropriate.
`;

export async function POST(request) {
  // Create a unique run ID for tracing
  const runId = uuidv4();
  const tracer = new LangChainTracer({
    projectName: 'climate-economy-chat',
    client: langsmith,
    run_id: runId,
    name: 'streaming_chat'
  });
  
  // Start timing
  const startTime = Date.now();
  
  try {
    // Track this as a trace
    await tracer.startTrace({
      name: 'streaming_chat_request',
      input: { 
        headers: request.headers,
        method: request.method
      }
    });
    
    // Get user session for authentication
    const session = await auth();
    const userId = session?.user?.id || 'anonymous';
    
    // Extract query and model from request
    const body = await request.json();
    const { query, model = 'gpt-4o' } = body;
    
    if (!query || query.trim() === '') {
      await tracer.endTrace({
        output: { error: 'Missing query parameter' },
        error: new Error('Missing query parameter')
      });
      return NextResponse.json(
        { message: 'Query parameter is required' }, 
        { status: 400 }
      );
    }
    
    // Track search event
    await metrics_service.track_event(
      'streaming_chat',
      userId,
      {
        query,
        model,
        is_streaming: true
      }
    );
    
    // Get relevant context for the query
    const contextStep = await tracer.trackStep('retrieve_context', {
      input: { query }
    });
    
    const context = await getRelevantContext(query, tracer);
    
    await tracer.endStep(contextStep, {
      output: { 
        contextCount: context.length,
        sources: context.map(c => c.source)
      }
    });
    
    // Format context for the prompt
    const contextText = context
      .map(item => `Source: ${item.source}\n${item.content}`)
      .join('\n\n');
    
    // Create messages array for the chat completion
    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: `Massachusetts Clean Energy Query: ${query}\n\nRelevant Context:\n${contextText}` }
    ];
    
    // Create a stream from OpenAI
    const streamStep = await tracer.trackStep('generate_stream', {
      input: { 
        model,
        messages: messages.map(m => ({ role: m.role, content: m.content.substring(0, 100) + '...' }))
      }
    });
    
    const stream = await openai.chat.completions.create({
      model,
      messages,
      stream: true,
      temperature: 0.7,
      max_tokens: 1500
    });
    
    // Create a readable stream to return to the client
    const encoder = new TextEncoder();
    let responseText = '';
    let tokenCount = 0;
    
    const readableStream = new ReadableStream({
      async start(controller) {
        // Process each chunk from OpenAI
        for await (const chunk of stream) {
          if (chunk.choices[0]?.delta?.content) {
            const content = chunk.choices[0].delta.content;
            responseText += content;
            tokenCount++;
            
            // Send the chunk to the client
            controller.enqueue(encoder.encode(content));
          }
        }
        
        // Send the sources at the end as JSON
        const sources = context.map(item => ({
          source: item.source,
          url: item.metadata?.url || '',
          relevance: item.relevance_score || 0
        }));
        
        controller.enqueue(encoder.encode(`\n\nSOURCES:${JSON.stringify(sources)}`));
        controller.close();
        
        // End the streaming step
        await tracer.endStep(streamStep, {
          output: { 
            tokenCount,
            responseLength: responseText.length
          }
        });
        
        // Calculate performance metrics
        const endTime = Date.now();
        const duration = endTime - startTime;
        
        // Track API performance
        await metrics_service.track_api_performance(
          '/api/chat/stream',
          duration,
          200,
          userId,
          { query, model }
        );
        
        // Store the chat in memory (asynchronously, don't wait)
        storeChat(userId, query, responseText);
        
        // End trace with results
        await tracer.endTrace({
          output: {
            responseLength: responseText.length,
            tokenCount,
            duration_ms: duration,
            context: {
              count: context.length,
              sources: context.map(c => c.source)
            }
          }
        });
      }
    });
    
    // Return the stream
    return new Response(readableStream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      }
    });
  } catch (error) {
    console.error('Streaming chat error:', error);
    
    // End tracing with error
    await tracer.endTrace({
      output: { error: error.message },
      error
    });
    
    // Return error response
    return NextResponse.json(
      { message: 'Error generating response', error: error.message },
      { status: 500 }
    );
  }
}

/**
 * Get relevant context for the query from multiple sources
 */
async function getRelevantContext(query, tracer) {
  const context = [];
  
  try {
    // Get database results first
    const dbStep = await tracer.trackStep('database_retrieval', {
      input: { query }
    });
    
    try {
      // Calculate embedding for vector search
      const { data: embedding } = await supabase.functions.invoke('embed-text', {
        body: { text: query }
      });
      
      if (embedding?.vector) {
        // Perform vector search
        const { data: matches, error } = await supabase
          .from('climate_memories')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(5)
          .order('similarity', { ascending: false })
          .rpc('match_climate_memories', {
            query_embedding: embedding.vector,
            match_threshold: 0.6,
            match_count: 5
          });
        
        if (matches && !error) {
          // Add database results to context
          for (const match of matches) {
            context.push({
              source: 'database',
              content: match.content,
              metadata: match.metadata || {},
              relevance_score: match.similarity,
              category: match.category
            });
          }
        }
      }
      
      await tracer.endStep(dbStep, {
        output: { resultCount: context.length }
      });
    } catch (dbError) {
      console.error('Database search error:', dbError);
      await tracer.endStep(dbStep, {
        output: { error: dbError.message },
        error: dbError
      });
    }
    
    // If we don't have enough database results, supplement with web search
    if (context.length < 3) {
      const webStep = await tracer.trackStep('web_search', {
        input: { query }
      });
      
      try {
        // Append Massachusetts if not already in query
        let searchQuery = query;
        if (!query.toLowerCase().includes('massachusetts') && 
            !query.toLowerCase().includes('mass') && 
            !query.toLowerCase().includes('ma')) {
          searchQuery = `${query} Massachusetts`;
        }
        
        // Call Serper API for web search
        const response = await fetch('https://google.serper.dev/search', {
          method: 'POST',
          headers: {
            'X-API-KEY': process.env.SERPER_API_KEY,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            q: searchQuery,
            num: 5
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // Add web results to context
          if (data.organic && data.organic.length > 0) {
            data.organic.forEach((item, index) => {
              // Calculate a score (decreasing by position)
              const positionScore = 1 - (index * 0.1);
              
              context.push({
                source: 'web',
                content: `Title: ${item.title}\nSnippet: ${item.snippet}\nURL: ${item.link}`,
                metadata: { url: item.link },
                relevance_score: positionScore
              });
            });
          }
        }
        
        await tracer.endStep(webStep, {
          output: { 
            resultCount: context.length - (context.filter(c => c.source === 'database').length)
          }
        });
      } catch (webError) {
        console.error('Web search error:', webError);
        await tracer.endStep(webStep, {
          output: { error: webError.message },
          error: webError
        });
      }
    }
    
    // Sort by relevance score
    context.sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0));
    
    // Limit to top 5 most relevant items
    return context.slice(0, 5);
  } catch (error) {
    console.error('Error getting relevant context:', error);
    return [];
  }
}

/**
 * Store the chat in memory for later retrieval
 */
async function storeChat(userId, query, response) {
  try {
    // Store in Supabase
    await supabase
      .from('climate_memories')
      .insert([
        {
          user_id: userId,
          content: `Q: ${query}\nA: ${response}`,
          category: 'conversation',
          source: 'assistant',
          metadata: { 
            is_conversation: true,
            timestamp: new Date().toISOString()
          }
        }
      ]);
  } catch (error) {
    console.error('Error storing chat:', error);
  }
} 