import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * API Route for Chat Feedback
 * Collects user feedback on AI responses to improve quality
 * Location: /app/api/assistant/feedback/route.js
 */
export async function POST(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const requestData = await request.json();
    
    // Get feedback data - support both message and step level feedback
    const { messageId, feedback, step_id, chat_id, feedback_type, feedback_score } = requestData;
    
    // Check if this is step-level feedback or message-level feedback
    const isStepFeedback = !!step_id;
    
    if ((!messageId && !step_id) || (!feedback && !feedback_type)) {
      return NextResponse.json(
        { error: 'Message ID or Step ID, and feedback data are required' },
        { status: 400 }
      );
    }
    
    // Get user if authenticated
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError) throw userError;
    
    if (!user) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Prepare feedback data for insertion
    const feedbackData = {
      user_id: user.id,
      feedback_time: new Date().toISOString()
    };
    
    // Add appropriate fields based on feedback type
    if (isStepFeedback) {
      feedbackData.step_id = step_id;
      feedbackData.chat_id = chat_id;
      feedbackData.feedback_type = feedback_type;
      feedbackData.feedback_score = feedback_score || (feedback_type === 'positive' ? 5 : 1);
    } else {
      feedbackData.message_id = messageId;
      feedbackData.feedback_type = feedback;
    }
    
    // Store feedback in chat_feedback table
    const { data: storedFeedback, error: feedbackError } = await supabase
      .from('chat_feedback')
      .insert(feedbackData)
      .select()
      .single();
    
    if (feedbackError) throw feedbackError;
    
    // Update satisfaction score if feedback is positive
    if (feedbackData.feedback_type === 'positive') {
      await updateSatisfactionScore(supabase, user.id);
    }
    
    // Track the feedback for RLHF
    if (typeof window !== 'undefined') {
      try {
        // If we're in a client context, use the metrics service
        const { MetricsService } = await import('@/lib/monitoring/metrics_service');
        const metricsService = new MetricsService();
        
        if (isStepFeedback) {
          await metricsService.trackChatFeedback(chat_id, {
            step_id,
            feedback_type: feedback_type,
            feedback_score: feedback_score,
            is_step_feedback: true
          });
        } else {
          await metricsService.trackChatFeedback(messageId, {
            message_id: messageId,
            feedback_type: feedback,
            is_step_feedback: false
          });
        }
      } catch (error) {
        console.error('Error tracking feedback metric:', error);
        // Non-critical error, don't throw
      }
    }
    
    return NextResponse.json({
      message: 'Feedback submitted successfully',
      data: storedFeedback
    });
    
  } catch (error) {
    console.error('Error submitting feedback:', error);
    return NextResponse.json(
      { error: 'Failed to submit feedback' },
      { status: 500 }
    );
  }
}

/**
 * Update user satisfaction score
 */
async function updateSatisfactionScore(supabase, userId) {
  try {
    // Get user engagement metrics
    const { data: metrics } = await supabase
      .from('user_engagement')
      .select('*')
      .eq('user_id', userId)
      .single();
    
    if (metrics) {
      // Calculate new satisfaction score (average of recent positive feedback)
      const { data: recentFeedback } = await supabase
        .from('chat_feedback')
        .select('feedback_type, feedback_score')
        .eq('user_id', userId)
        .order('feedback_time', { ascending: false })
        .limit(10);
      
      if (recentFeedback && recentFeedback.length > 0) {
        // Calculate score from both legacy feedback_type and new feedback_score
        let totalScore = 0;
        let itemCount = 0;
        
        for (const fb of recentFeedback) {
          if (fb.feedback_score) {
            // Use numeric score if available
            totalScore += fb.feedback_score;
            itemCount++;
          } else if (fb.feedback_type) {
            // Convert feedback_type to score
            totalScore += (fb.feedback_type === 'positive' ? 5 : fb.feedback_type === 'neutral' ? 3 : 1);
            itemCount++;
          }
        }
        
        const averageScore = itemCount > 0 ? totalScore / itemCount : 3;
        const normalizedScore = Math.round((averageScore / 5) * 100); // Convert 1-5 to percentage
        
        // Update satisfaction score
        await supabase
          .from('user_engagement')
          .update({
            satisfaction_score: normalizedScore,
            updated_at: new Date().toISOString()
          })
          .eq('user_id', userId);
      }
    } else {
      // Create new engagement record with initial satisfaction score
      await supabase
        .from('user_engagement')
        .insert({
          user_id: userId,
          satisfaction_score: 100, // First feedback is positive
          updated_at: new Date().toISOString()
        });
    }
  } catch (error) {
    console.error('Error updating satisfaction score:', error);
    // Don't throw error, just log it since this is not critical
  }
} 