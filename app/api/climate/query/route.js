import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { spawn } from 'child_process';
import path from 'path';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

export async function POST(request) {
  try {
    // Parse request body
    const body = await request.json();
    const { query, userId = 'anonymous' } = body;
    
    if (!query || query.trim() === '') {
      return NextResponse.json(
        { message: 'Query parameter is required' }, 
        { status: 400 }
      );
    }
    
    // Call the Python retriever through a subprocess
    const pythonProcess = spawn('python', [
      path.join(process.cwd(), 'scripts', 'query_climate_retriever.py'),
      query
    ]);
    
    let responseData = '';
    let errorData = '';
    
    // Collect data from stdout
    pythonProcess.stdout.on('data', (data) => {
      responseData += data.toString();
    });
    
    // Collect data from stderr
    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });
    
    // Wait for the process to complete
    const exitCode = await new Promise((resolve) => {
      pythonProcess.on('close', resolve);
    });
    
    // Check for errors
    if (exitCode !== 0 || errorData) {
      console.error(`Python process error (exit code ${exitCode}):`, errorData);
      return NextResponse.json(
        { message: 'Error processing query', error: errorData }, 
        { status: 500 }
      );
    }
    
    // Parse the JSON response
    let result;
    try {
      result = JSON.parse(responseData);
    } catch (e) {
      console.error('Error parsing JSON response:', e);
      return NextResponse.json(
        { message: 'Error parsing response', error: e.message, raw: responseData }, 
        { status: 500 }
      );
    }
    
    // Store the query and response in the database for feedback collection
    if (supabase) {
      try {
        const chatId = crypto.randomUUID();
        const messageId = crypto.randomUUID();
        
        // Store the chat
        await supabase.from('chats').insert({
          id: chatId,
          user_id: userId,
          created_at: new Date().toISOString()
        });
        
        // Store the message
        await supabase.from('messages').insert({
          id: messageId,
          chat_id: chatId,
          role: 'assistant',
          content: result.answer,
          metadata: {
            query: query,
            sources: result.sources,
            within_constraints: result.within_constraints
          },
          created_at: new Date().toISOString()
        });
        
        // Add chat_id and message_id to the response
        result.chat_id = chatId;
        result.message_id = messageId;
      } catch (dbError) {
        console.error('Error storing chat in database:', dbError);
        // Continue even if database storage fails
      }
    }
    
    return NextResponse.json(result);
    
  } catch (error) {
    console.error('Error in climate query API:', error);
    return NextResponse.json(
      { message: 'Error processing request', error: error.message }, 
      { status: 500 }
    );
  }
}
