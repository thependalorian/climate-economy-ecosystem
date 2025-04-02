import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import OpenAI from 'openai';
import { getCache, setCache } from '@/lib/redis';
import { 
  getMemory, 
  addToMemory, 
  buildMemoryContext
} from '@/lib/memory';
import { 
  assistantTools, 
  searchKnowledgeBase, 
  getUserProfile,
  checkConnectionEligibility
} from '@/lib/assistant/tools';

/**
 * API Route for Chat Assistant
 * Processes user questions and returns AI responses with relevant sources
 * Uses function calling to route vector search through the assistant
 * Location: /app/api/assistant/chat/route.js
 */
export async function POST(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const requestData = await request.json();
    
    // Get the message and chat history
    const { message, history = [] } = requestData;
    
    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }
    
    // Get user if authenticated
    const { data: { user } } = await supabase.auth.getUser();
    
    // Get user profile for personalization if authenticated
    let userProfile = null;
    if (user) {
      const { data: profile } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();
      userProfile = profile;
    }
    
    // Check cache for similar questions - only for anonymous users or if no memory exists
    let cachedResponse = null;
    if (!user) {
      const simpleCacheKey = `chat:${message.toLowerCase().trim().slice(0, 15)}`;
      cachedResponse = await getCache(simpleCacheKey);
    }
    
    if (cachedResponse) {
      return NextResponse.json({
        response: cachedResponse.response,
        sources: cachedResponse.sources || [],
        fromCache: true
      });
    }
    
    // Build memory context if user is authenticated
    let memoryContext = '';
    if (user) {
      memoryContext = await buildMemoryContext(user.id, userProfile);
    }
    
    // Create OpenAI client
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    
    // Prepare conversation history
    const formattedHistory = history.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
    
    // Create system message with context
    const systemMessage = {
      role: "system",
      content: buildSystemPrompt(userProfile, memoryContext)
    };
    
    // Create messages array
    const messages = [
      systemMessage,
      ...formattedHistory,
      { role: "user", content: message }
    ];
    
    // Track sources found via function calls
    let sources = [];
    
    // Create the chat completion with function calling
    const completion = await openai.chat.completions.create({
      model: "gpt-4-turbo",
      messages,
      tools: assistantTools,
      temperature: 0.7,
      max_tokens: 1000,
      tool_choice: "auto"
    });
    
    let response = completion.choices[0].message;
    
    // Check if the model wanted to call a function
    if (response.tool_calls) {
      // Handle each tool call
      const toolResults = await Promise.all(
        response.tool_calls.map(async (toolCall) => {
          const functionName = toolCall.function.name;
          let functionResult = null;
          
          // Parse arguments
          const args = JSON.parse(toolCall.function.arguments);
          
          // Call appropriate function
          switch (functionName) {
            case "search_knowledge_base":
              functionResult = await searchKnowledgeBase(args);
              // Add to sources
              if (Array.isArray(functionResult) && !functionResult.error) {
                sources = functionResult;
              }
              break;
            case "get_user_profile":
              if (user && args.user_id === user.id) {
                functionResult = await getUserProfile(args);
              } else {
                functionResult = { error: "Unauthorized to access this profile" };
              }
              break;
            case "check_connection_eligibility":
              if (user && args.user_id === user.id) {
                functionResult = await checkConnectionEligibility(args);
              } else {
                functionResult = { error: "Unauthorized to check eligibility" };
              }
              break;
            default:
              functionResult = { error: "Unknown function" };
          }
          
          return {
            tool_call_id: toolCall.id,
            role: "tool",
            name: functionName,
            content: JSON.stringify(functionResult)
          };
        })
      );
      
      // Add tool results to messages
      messages.push(response);
      messages.push(...toolResults);
      
      // Get a new response from the model
      const secondCompletion = await openai.chat.completions.create({
        model: "gpt-4-turbo",
        messages,
        temperature: 0.7,
        max_tokens: 1000
      });
      
      response = secondCompletion.choices[0].message;
    }
    
    // Save to memory if user is authenticated
    if (user) {
      // Save user message
      await addToMemory(user.id, {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      });
      
      // Save assistant response
      await addToMemory(user.id, {
        role: 'assistant',
        content: response.content,
        timestamp: new Date().toISOString(),
        sources: sources
      });
      
      // Update user engagement metrics
      await updateEngagement(supabase, user.id);
    } else {
      // Cache response for anonymous users
      const simpleCacheKey = `chat:${message.toLowerCase().trim().slice(0, 15)}`;
      await setCache(simpleCacheKey, {
        response: response.content,
        sources,
        timestamp: new Date().toISOString()
      }, 86400); // 24 hours
    }
    
    // Return the response
    return NextResponse.json({
      response: response.content,
      sources: sources.length > 0 ? sources : []
    });
    
  } catch (error) {
    console.error('Error in chat API:', error);
    return NextResponse.json(
      { error: 'Failed to process message', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * Build system prompt for the assistant
 */
function buildSystemPrompt(userProfile, memoryContext = '') {
  let prompt = `You are a helpful assistant for the Climate Economy Ecosystem, helping users navigate career opportunities in clean energy and climate technology, particularly in Massachusetts.

Your capabilities:
1. Search the knowledge base for relevant information using the search_knowledge_base function
2. Access user profiles with get_user_profile for personalized assistance
3. Check if users are eligible to connect with partners using check_connection_eligibility

Always provide helpful, accurate, and concise information. When you don't know the answer or need more information, use the appropriate function to find relevant content.

For questions about companies, jobs, or training programs, always search the knowledge base first.`;

  // Add memory context if available
  if (memoryContext) {
    prompt += `\n\n${memoryContext}`;
  }
  
  // Add information about the user if available
  if (userProfile) {
    prompt += `\n\nYou're speaking with a user who has the following profile:
- Name: ${userProfile.full_name || 'Not provided'}
- Skills: ${userProfile.skills?.join(', ') || 'Not specified'}
- Experience: ${userProfile.experience || 'Not specified'}
- Interests: ${userProfile.interests?.join(', ') || 'Not specified'}
- Location: ${userProfile.location || 'Not specified'}
- Education: ${userProfile.education || 'Not specified'}
- Career goals: ${userProfile.career_goals || 'Not specified'}

Tailor your responses to this user's background and interests.`;
  }
  
  return prompt;
}

/**
 * Update user engagement metrics
 */
async function updateEngagement(supabase, userId) {
  try {
    // Check if user has engagement record
    const { data: existingMetrics } = await supabase
      .from('user_engagement')
      .select('*')
      .eq('user_id', userId)
      .single();
    
    if (existingMetrics) {
      // Update existing record
      await supabase
        .from('user_engagement')
        .update({
          recommendations_clicked: existingMetrics.recommendations_clicked + 1,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId);
    } else {
      // Create new record
      await supabase
        .from('user_engagement')
        .insert({
          user_id: userId,
          recommendations_clicked: 1
        });
    }
  } catch (error) {
    console.error('Error updating engagement metrics:', error);
    // Don't throw error, just log it since this is not critical
  }
} 