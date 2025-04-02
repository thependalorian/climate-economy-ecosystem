import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { metrics_service } from '../../../../lib/monitoring/metrics_service';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * POST handler for tracking skill verification metrics
 * @param {Object} request - The request object
 * @returns {Promise<NextResponse>} The response
 */
export async function POST(request) {
  try {
    const data = await request.json();
    const { userId, verificationData } = data;

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    // Track metrics with Python metrics service
    try {
      await metrics_service.track_skill_verification(userId, verificationData);
    } catch (error) {
      console.error('Error calling Python metrics service:', error);
      // Continue even if metrics service fails
    }

    // Store metrics in Supabase
    const { error } = await supabase
      .from('metrics')
      .insert({
        user_id: userId,
        event_type: 'skill_verification',
        event_data: {
          verified_count: verificationData.verifiedCount || 0,
          added_count: verificationData.addedCount || 0,
          removed_count: verificationData.removedCount || 0,
          categories: verificationData.categories || [],
          timestamp: new Date().toISOString()
        }
      });

    if (error) {
      console.error('Error storing metrics in Supabase:', error);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error in skill verification metrics API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 