import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * API Route for Career Counseling Feature Votes
 * Handles user votes for the career counseling feature
 * Location: /app/api/feature-votes/career-counseling/route.js
 */
export async function POST() {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    
    // Get the current user
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError) throw userError;
    
    if (!user) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Check if user has already voted
    const { data: existingVote } = await supabase
      .from('feature_votes')
      .select()
      .eq('user_id', user.id)
      .eq('feature', 'career_counseling')
      .single();
    
    if (existingVote) {
      return NextResponse.json(
        { message: 'Already voted' },
        { status: 200 }
      );
    }
    
    // Record the vote
    const { error: voteError } = await supabase
      .from('feature_votes')
      .insert({
        user_id: user.id,
        feature: 'career_counseling',
        voted_at: new Date().toISOString()
      });
    
    if (voteError) throw voteError;
    
    return NextResponse.json(
      { message: 'Vote recorded successfully' },
      { status: 201 }
    );
    
  } catch (error) {
    console.error('Error recording vote:', error);
    return NextResponse.json(
      { error: 'Failed to record vote' },
      { status: 500 }
    );
  }
} 