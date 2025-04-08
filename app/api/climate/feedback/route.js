import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { auth } from '@/auth';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

export async function POST(request) {
  try {
    // Get user session
    const session = await auth();
    const userId = session?.user?.id || 'anonymous';
    
    // Parse request body
    const body = await request.json();
    const { 
      messageId, 
      feedbackType = 'rating', 
      rating, 
      isPositive, 
      comment, 
      aspect,
      comparisonId,
      preferredMessageId,
      rejectedMessageId
    } = body;
    
    // Validate required fields
    if (!messageId && !(preferredMessageId && rejectedMessageId)) {
      return NextResponse.json(
        { message: 'Message ID is required' }, 
        { status: 400 }
      );
    }
    
    if (!supabase) {
      return NextResponse.json(
        { message: 'Database connection not available' }, 
        { status: 500 }
      );
    }
    
    // Prepare feedback data based on feedback type
    let feedbackData;
    
    switch (feedbackType) {
      case 'rating':
        if (rating === undefined) {
          return NextResponse.json(
            { message: 'Rating is required for rating feedback' }, 
            { status: 400 }
          );
        }
        feedbackData = {
          message_id: messageId,
          user_id: userId,
          feedback_type: 'rating',
          rating: rating,
          comment: comment,
          created_at: new Date().toISOString()
        };
        break;
        
      case 'thumbs':
        if (isPositive === undefined) {
          return NextResponse.json(
            { message: 'isPositive is required for thumbs feedback' }, 
            { status: 400 }
          );
        }
        feedbackData = {
          message_id: messageId,
          user_id: userId,
          feedback_type: 'thumbs',
          rating: isPositive ? 5 : 1,
          comment: comment,
          created_at: new Date().toISOString()
        };
        break;
        
      case 'text':
        if (!comment) {
          return NextResponse.json(
            { message: 'Comment is required for text feedback' }, 
            { status: 400 }
          );
        }
        feedbackData = {
          message_id: messageId,
          user_id: userId,
          feedback_type: 'text',
          comment: comment,
          created_at: new Date().toISOString()
        };
        break;
        
      case 'specific':
        if (!aspect || rating === undefined) {
          return NextResponse.json(
            { message: 'Aspect and rating are required for specific feedback' }, 
            { status: 400 }
          );
        }
        feedbackData = {
          message_id: messageId,
          user_id: userId,
          feedback_type: 'specific',
          aspect: aspect,
          rating: rating,
          comment: comment,
          created_at: new Date().toISOString()
        };
        break;
        
      case 'comparison':
        if (!preferredMessageId || !rejectedMessageId) {
          return NextResponse.json(
            { message: 'Preferred and rejected message IDs are required for comparison feedback' }, 
            { status: 400 }
          );
        }
        
        // Generate a unique comparison ID if not provided
        const uniqueComparisonId = comparisonId || crypto.randomUUID();
        
        // Create two feedback entries for comparison
        const preferredFeedback = {
          message_id: preferredMessageId,
          user_id: userId,
          feedback_type: 'comparison',
          rating: 5,
          comparison_id: uniqueComparisonId,
          comment: comment ? `Preferred: ${comment}` : 'Preferred response',
          created_at: new Date().toISOString()
        };
        
        const rejectedFeedback = {
          message_id: rejectedMessageId,
          user_id: userId,
          feedback_type: 'comparison',
          rating: 1,
          comparison_id: uniqueComparisonId,
          comment: comment ? `Rejected: ${comment}` : 'Rejected response',
          created_at: new Date().toISOString()
        };
        
        // Insert both feedback entries
        const { data, error } = await supabase
          .from('chat_feedback')
          .insert([preferredFeedback, rejectedFeedback]);
          
        if (error) {
          console.error('Error storing comparison feedback:', error);
          return NextResponse.json(
            { message: 'Error storing feedback', error: error.message }, 
            { status: 500 }
          );
        }
        
        return NextResponse.json({ 
          success: true, 
          comparisonId: uniqueComparisonId 
        });
        
      default:
        return NextResponse.json(
          { message: `Unsupported feedback type: ${feedbackType}` }, 
          { status: 400 }
        );
    }
    
    // Insert feedback into database
    const { data, error } = await supabase
      .from('chat_feedback')
      .insert(feedbackData);
      
    if (error) {
      console.error('Error storing feedback:', error);
      return NextResponse.json(
        { message: 'Error storing feedback', error: error.message }, 
        { status: 500 }
      );
    }
    
    // Update feedback metrics
    try {
      // Check if metrics entry exists
      const { data: metricsData, error: metricsError } = await supabase
        .from('feedback_metrics')
        .select('*')
        .eq('message_id', messageId)
        .single();
        
      if (metricsError && metricsError.code !== 'PGRST116') {
        console.error('Error checking feedback metrics:', metricsError);
      }
      
      // Get all feedback for this message
      const { data: feedbackItems, error: feedbackError } = await supabase
        .from('chat_feedback')
        .select('*')
        .eq('message_id', messageId);
        
      if (feedbackError) {
        console.error('Error fetching feedback items:', feedbackError);
      } else {
        // Calculate metrics
        const ratings = feedbackItems
          .filter(item => item.rating !== null && item.rating !== undefined)
          .map(item => item.rating);
          
        const avgRating = ratings.length > 0 
          ? ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length 
          : null;
          
        const metricsEntry = {
          message_id: messageId,
          feedback_count: feedbackItems.length,
          average_rating: avgRating,
          updated_at: new Date().toISOString()
        };
        
        if (metricsData) {
          // Update existing metrics
          const { error: updateError } = await supabase
            .from('feedback_metrics')
            .update(metricsEntry)
            .eq('message_id', messageId);
            
          if (updateError) {
            console.error('Error updating feedback metrics:', updateError);
          }
        } else {
          // Insert new metrics
          metricsEntry.created_at = new Date().toISOString();
          
          const { error: insertError } = await supabase
            .from('feedback_metrics')
            .insert(metricsEntry);
            
          if (insertError) {
            console.error('Error inserting feedback metrics:', insertError);
          }
        }
      }
    } catch (metricsError) {
      console.error('Error processing feedback metrics:', metricsError);
      // Continue even if metrics update fails
    }
    
    return NextResponse.json({ success: true });
    
  } catch (error) {
    console.error('Error in climate feedback API:', error);
    return NextResponse.json(
      { message: 'Error processing feedback', error: error.message }, 
      { status: 500 }
    );
  }
}
