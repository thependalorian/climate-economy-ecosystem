import { createClient } from '@supabase/supabase-js';
import { metrics_service } from '@/lib/monitoring/metrics_service';
import { getSession } from 'next-auth/react';

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * API endpoint for submitting user feedback
 * 
 * Collects user satisfaction ratings, feedback comments, and analyzes
 * feedback content for product improvement insights.
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Get user session
    const session = await getSession({ req });
    const userId = session?.user?.id;
    
    if (!userId) {
      return res.status(401).json({ message: 'User must be logged in to submit feedback' });
    }
    
    // Extract feedback data from request
    const { 
      satisfaction_score, 
      feedback,
      session_id,
      page_url,
      context = {} 
    } = req.body;
    
    // Validate required fields
    if (!satisfaction_score || satisfaction_score < 1 || satisfaction_score > 5) {
      return res.status(400).json({ message: 'Valid satisfaction score (1-5) is required' });
    }
    
    if (!session_id) {
      return res.status(400).json({ message: 'Session ID is required' });
    }
    
    // Store feedback in user_satisfaction table
    const { data: satisfactionData, error: satisfactionError } = await supabase
      .from('user_satisfaction')
      .insert([
        {
          user_id: userId,
          session_id,
          satisfaction_score,
          feedback
        }
      ])
      .select();
      
    if (satisfactionError) {
      console.error('Error storing user satisfaction:', satisfactionError);
      return res.status(500).json({ message: 'Error storing feedback', error: satisfactionError.message });
    }
    
    // Track feedback event
    await metrics_service.track_event(
      'feedback_submitted', 
      userId, 
      {
        satisfaction_score,
        has_text_feedback: !!feedback,
        page_url,
        ...context
      }
    );
    
    // If feedback text is provided, analyze it
    if (feedback && feedback.trim()) {
      const satisfactionId = satisfactionData[0].id;
      
      // Analyze feedback using AI
      const analysis = await metrics_service.analyze_user_feedback(feedback);
      
      // Store analysis results
      await supabase
        .from('feedback_analysis')
        .insert([
          {
            satisfaction_id: satisfactionId,
            sentiment: analysis.sentiment,
            categories: analysis.categories,
            action_items: analysis.action_items,
            summary: analysis.summary
          }
        ]);
      
      // For high-priority feedback (negative with action items),
      // create alert for product team
      if (
        analysis.sentiment === 'negative' && 
        satisfaction_score <= 2 && 
        analysis.action_items?.length > 0
      ) {
        await createFeedbackAlert(userId, satisfactionId, analysis, feedback);
      }
    }
    
    // Return success
    return res.status(200).json({ 
      message: 'Feedback submitted successfully',
      thankyou_message: getFeedbackThankyouMessage(satisfaction_score)
    });
  } catch (error) {
    console.error('Error processing feedback:', error);
    return res.status(500).json({ message: 'Error processing feedback', error: error.message });
  }
}

/**
 * Create a feedback alert for urgent negative feedback
 */
async function createFeedbackAlert(userId, satisfactionId, analysis, feedback) {
  try {
    // Get user details
    const { data: userData } = await supabase
      .from('user_profiles')
      .select('email, name, user_type')
      .eq('id', userId)
      .single();
    
    // Create alert entry
    await supabase
      .from('feedback_alerts')
      .insert([
        {
          satisfaction_id: satisfactionId,
          user_id: userId,
          user_email: userData?.email,
          user_type: userData?.user_type,
          categories: analysis.categories,
          summary: analysis.summary,
          feedback_text: feedback,
          priority: 'high',
          status: 'new'
        }
      ]);
      
    // Could also send notification via email, Slack, etc.
    
  } catch (error) {
    console.error('Error creating feedback alert:', error);
    // Don't fail the feedback submission if alert creation fails
  }
}

/**
 * Get a personalized thank you message based on score
 */
function getFeedbackThankyouMessage(score) {
  if (score >= 4) {
    return "Thank you for your positive feedback! We're glad you're having a great experience.";
  } else if (score === 3) {
    return "Thank you for your feedback. We're constantly working to improve your experience.";
  } else {
    return "Thank you for your feedback. We take your concerns seriously and will work to address them.";
  }
} 