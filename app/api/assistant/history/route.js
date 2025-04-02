import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import { getMemory } from '@/lib/memory';

/**
 * API Route for Chat History
 * Retrieves the user's conversation history from memory
 * Location: /app/api/assistant/history/route.js
 */
export async function GET(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    
    // Get user if authenticated
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError) throw userError;
    
    if (!user) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Get user's conversation history from memory
    const messages = await getMemory(user.id);
    
    return NextResponse.json({
      messages
    });
    
  } catch (error) {
    console.error('Error fetching chat history:', error);
    return NextResponse.json(
      { error: 'Failed to fetch chat history' },
      { status: 500 }
    );
  }
} 