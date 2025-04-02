import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import { clearMemory } from '@/lib/memory';

/**
 * API Route for Clearing Chat History
 * Removes all conversation history for the user
 * Location: /app/api/assistant/clear/route.js
 */
export async function POST(request) {
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
    
    // Clear user's memory
    await clearMemory(user.id);
    
    return NextResponse.json({
      message: 'Conversation history cleared successfully'
    });
    
  } catch (error) {
    console.error('Error clearing chat history:', error);
    return NextResponse.json(
      { error: 'Failed to clear chat history' },
      { status: 500 }
    );
  }
} 