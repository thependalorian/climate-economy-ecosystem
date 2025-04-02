import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * API Route for Chat Feedback Metrics
 * 
 * Stores and processes chat feedback metrics for RLHF and analytics
 * Location: /app/api/metrics/chat-feedback/route.js
 */
export async function POST(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const requestData = await request.json();
    
    // Get metrics data
    const { userId, chatId, feedbackData } = requestData;
    
    if (!userId || !chatId || !feedbackData) {
      return NextResponse.json(
        { error: 'User ID, chat ID, and feedback data are required' },
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
    
    // Check if user matches the provided userId
    if (user.id !== userId) {
      return NextResponse.json(
        { error: 'User ID mismatch' },
        { status: 403 }
      );
    }
    
    // Prepare metrics data
    const metricsData = {
      user_id: userId,
      event_type: 'chat_feedback',
      timestamp: new Date().toISOString(),
      properties: {
        chat_id: chatId,
        is_step_feedback: !!feedbackData.step_id,
        feedback_type: feedbackData.feedback_type || 'neutral',
        feedback_score: feedbackData.feedback_score || 3,
        step_id: feedbackData.step_id || null,
        message_id: feedbackData.message_id || null
      },
      session_id: requestData.sessionId || null
    };
    
    // Store metrics in events table
    const { data: storedMetrics, error: metricsError } = await supabase
      .from('events')
      .insert(metricsData)
      .select()
      .single();
    
    if (metricsError) throw metricsError;
    
    // Add to feedback analytics
    await updateFeedbackAnalytics(supabase, metricsData);
    
    return NextResponse.json({
      message: 'Feedback metrics recorded successfully',
      data: storedMetrics
    });
    
  } catch (error) {
    console.error('Error recording feedback metrics:', error);
    return NextResponse.json(
      { error: 'Failed to record feedback metrics' },
      { status: 500 }
    );
  }
}

/**
 * Update feedback analytics
 */
async function updateFeedbackAnalytics(supabase, metricsData) {
  try {
    // Get or create feedback analytics record
    const { data: analytics } = await supabase
      .from('feedback_analytics')
      .select('*')
      .eq('user_id', metricsData.user_id)
      .single();
    
    const feedbackType = metricsData.properties.feedback_type;
    const isStepFeedback = metricsData.properties.is_step_feedback;
    
    if (analytics) {
      // Update existing analytics
      const updates = {
        total_feedback_count: (analytics.total_feedback_count || 0) + 1,
        updated_at: new Date().toISOString()
      };
      
      // Update type-specific counters
      if (isStepFeedback) {
        updates.step_feedback_count = (analytics.step_feedback_count || 0) + 1;
        
        if (feedbackType === 'positive') {
          updates.positive_step_feedback = (analytics.positive_step_feedback || 0) + 1;
        } else if (feedbackType === 'negative') {
          updates.negative_step_feedback = (analytics.negative_step_feedback || 0) + 1;
        }
      } else {
        updates.message_feedback_count = (analytics.message_feedback_count || 0) + 1;
        
        if (feedbackType === 'positive') {
          updates.positive_message_feedback = (analytics.positive_message_feedback || 0) + 1;
        } else if (feedbackType === 'negative') {
          updates.negative_message_feedback = (analytics.negative_message_feedback || 0) + 1;
        }
      }
      
      // Update average score if provided
      if (metricsData.properties.feedback_score) {
        const currentTotal = (analytics.average_score || 3) * (analytics.total_feedback_count || 0);
        const newTotal = currentTotal + metricsData.properties.feedback_score;
        updates.average_score = newTotal / updates.total_feedback_count;
      }
      
      await supabase
        .from('feedback_analytics')
        .update(updates)
        .eq('user_id', metricsData.user_id);
    } else {
      // Create new analytics record
      const newAnalytics = {
        user_id: metricsData.user_id,
        total_feedback_count: 1,
        step_feedback_count: isStepFeedback ? 1 : 0,
        message_feedback_count: isStepFeedback ? 0 : 1,
        positive_step_feedback: isStepFeedback && feedbackType === 'positive' ? 1 : 0,
        negative_step_feedback: isStepFeedback && feedbackType === 'negative' ? 1 : 0,
        positive_message_feedback: !isStepFeedback && feedbackType === 'positive' ? 1 : 0,
        negative_message_feedback: !isStepFeedback && feedbackType === 'negative' ? 1 : 0,
        average_score: metricsData.properties.feedback_score || 3,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      await supabase
        .from('feedback_analytics')
        .insert(newAnalytics);
    }
  } catch (error) {
    console.error('Error updating feedback analytics:', error);
    // Don't throw error, just log it since this is not critical
  }
} 