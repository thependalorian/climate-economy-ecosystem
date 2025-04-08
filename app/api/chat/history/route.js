import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { auth } from '@/auth';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

// Only create client if credentials are available
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

// Validate Supabase client
if (!supabase) {
  console.warn('Supabase client not initialized. Check your environment variables.');
}

export async function GET(request) {
  try {
    // Get user session
    const session = await auth();
    const userId = session?.user?.id || 'anonymous';

    // Get chat history from Supabase
    const { data, error } = await supabase
      .from('climate_memories')
      .select('*')
      .eq('user_id', userId)
      .eq('category', 'conversation')
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) {
      console.error('Error fetching chat history:', error);
      return NextResponse.json(
        { error: 'Failed to fetch chat history' },
        { status: 500 }
      );
    }

    // Format messages for the client
    const messages = data.map(item => {
      // Parse Q&A format
      const parts = item.content.split('\nA: ');
      if (parts.length === 2) {
        const question = parts[0].replace('Q: ', '');
        const answer = parts[1];

        return [
          {
            id: `${item.id}-q`,
            role: 'user',
            content: question,
            timestamp: item.created_at
          },
          {
            id: `${item.id}-a`,
            role: 'assistant',
            content: answer,
            timestamp: item.created_at,
            sources: item.metadata?.sources || []
          }
        ];
      }

      // Default format if not in Q&A format
      return {
        id: item.id,
        role: item.source === 'user' ? 'user' : 'assistant',
        content: item.content,
        timestamp: item.created_at,
        sources: item.metadata?.sources || []
      };
    });

    // Flatten the array (since some items return two messages)
    const flattenedMessages = messages.flat();

    // Sort by timestamp
    flattenedMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    return NextResponse.json({ messages: flattenedMessages });

  } catch (error) {
    console.error('Error in chat history API:', error);
    return NextResponse.json(
      { error: 'Failed to fetch chat history' },
      { status: 500 }
    );
  }
}
