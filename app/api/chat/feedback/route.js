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

export async function POST(request) {
  try {
    // Get user session
    const session = await auth();
    const userId = session?.user?.id || 'anonymous';

    // Get feedback data from request
    const { messageId, feedback } = await request.json();

    if (!messageId || !feedback) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Store feedback in Supabase
    const { data, error } = await supabase
      .from('feedback')
      .insert([
        {
          user_id: userId,
          message_id: messageId,
          feedback_type: feedback,
          created_at: new Date().toISOString()
        }
      ]);

    if (error) {
      console.error('Error storing feedback:', error);
      return NextResponse.json(
        { error: 'Failed to store feedback' },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });

  } catch (error) {
    console.error('Error in feedback API:', error);
    return NextResponse.json(
      { error: 'Failed to process feedback' },
      { status: 500 }
    );
  }
}
