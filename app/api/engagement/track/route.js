import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * API Route for Engagement Tracking
 * Records various user engagement metrics for personalization
 * Location: /app/api/engagement/track/route.js
 */
export async function POST(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const requestData = await request.json();
    
    // Get tracking data
    const { action, data = {} } = requestData;
    
    if (!action) {
      return NextResponse.json(
        { error: 'Action is required' },
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
    
    // Get existing metrics or create new record
    const { data: metrics } = await supabase
      .from('user_engagement')
      .select('*')
      .eq('user_id', user.id)
      .single();
    
    // Prepare update data based on action
    const updateData = prepareUpdateData(action, data, metrics);
    
    if (metrics) {
      // Update existing record
      const { data: updatedMetrics, error } = await supabase
        .from('user_engagement')
        .update(updateData)
        .eq('user_id', user.id)
        .select()
        .single();
      
      if (error) throw error;
      
      return NextResponse.json({
        message: 'Engagement tracked successfully',
        data: updatedMetrics
      });
      
    } else {
      // Create new record
      const { data: newMetrics, error } = await supabase
        .from('user_engagement')
        .insert({
          user_id: user.id,
          ...updateData
        })
        .select()
        .single();
      
      if (error) throw error;
      
      return NextResponse.json({
        message: 'Engagement record created',
        data: newMetrics
      });
    }
    
  } catch (error) {
    console.error('Error tracking engagement:', error);
    return NextResponse.json(
      { error: 'Failed to track engagement' },
      { status: 500 }
    );
  }
}

/**
 * Prepare update data based on action type
 */
function prepareUpdateData(action, data, metrics) {
  // Initialize with defaults from existing metrics or empty object
  const baseMetrics = metrics || {
    recommendations_count: 0,
    recommendations_clicked: 0,
    resources_accessed: 0,
    connections_count: 0,
    connection_requests: 0,
    profile_updates: 0,
    logins_count: 0,
    satisfaction_score: 0
  };
  
  // Create a copy to modify
  const updateData = { ...baseMetrics };
  
  // Set updated_at timestamp
  updateData.updated_at = new Date().toISOString();
  
  // Update specific fields based on action
  switch (action) {
    case 'login':
      updateData.logins_count = (baseMetrics.logins_count || 0) + 1;
      break;
      
    case 'message_sent':
      // No specific counter for messages, could use recommendations_clicked
      // as a proxy for engagement with the assistant
      updateData.recommendations_clicked = (baseMetrics.recommendations_clicked || 0) + 1;
      break;
      
    case 'recommendation_viewed':
      updateData.recommendations_count = (baseMetrics.recommendations_count || 0) + 1;
      break;
      
    case 'recommendation_clicked':
      updateData.recommendations_clicked = (baseMetrics.recommendations_clicked || 0) + 1;
      break;
      
    case 'resource_accessed':
      updateData.resources_accessed = (baseMetrics.resources_accessed || 0) + 1;
      break;
      
    case 'connection_requested':
      updateData.connection_requests = (baseMetrics.connection_requests || 0) + 1;
      break;
      
    case 'connection_made':
      updateData.connections_count = (baseMetrics.connections_count || 0) + 1;
      break;
      
    case 'profile_updated':
      updateData.profile_updates = (baseMetrics.profile_updates || 0) + 1;
      break;
      
    case 'feedback_provided':
      // If positive feedback, can use it to calculate satisfaction
      if (data.isPositive) {
        // This is a simplified approach; a more sophisticated one could
        // calculate a rolling average based on recent feedback
        updateData.satisfaction_score = Math.min(
          100, 
          (baseMetrics.satisfaction_score || 0) + 5
        );
      }
      break;
      
    default:
      // No changes for unknown actions
      break;
  }
  
  return updateData;
} 