import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { metrics_service } from '../../../../lib/monitoring/metrics_service';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * POST handler for tracking enhanced job search metrics
 * @param {Object} request - The request object
 * @returns {Promise<NextResponse>} The response
 */
export async function POST(request) {
  try {
    const data = await request.json();
    const { userId, searchData } = data;

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    // Track metrics with Python metrics service
    try {
      await metrics_service.track_enhanced_job_search(userId, searchData);
    } catch (error) {
      console.error('Error calling Python metrics service:', error);
      // Continue even if metrics service fails
    }

    // Store metrics in Supabase
    const { error } = await supabase
      .from('metrics')
      .insert({
        user_id: userId,
        event_type: 'enhanced_job_search',
        event_data: {
          query: searchData.query || '',
          result_count: (searchData.results || []).length,
          used_profile_data: !!searchData.usedProfileData,
          sectors: searchData.sectors || [],
          skills: searchData.skills || [],
          is_recommendation: !!searchData.isRecommendation,
          performance: searchData.performance || {},
          timestamp: new Date().toISOString()
        }
      });

    if (error) {
      console.error('Error storing metrics in Supabase:', error);
    }

    // Also log to search analytics if not already done by the backend
    try {
      await recordSearchAnalytics(userId, searchData);
    } catch (analyticsError) {
      console.error('Error recording search analytics:', analyticsError);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error in enhanced job search metrics API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/**
 * Record search analytics
 * @param {string} userId - User ID
 * @param {Object} searchData - Search data
 */
async function recordSearchAnalytics(userId, searchData) {
  try {
    await supabase
      .from('search_analytics')
      .insert({
        user_id: userId,
        search_query: (searchData.query || '').slice(0, 255),
        search_type: searchData.isRecommendation ? 'recommendation' : 'enhanced',
        result_count: (searchData.results || []).length,
        search_params: {
          query: searchData.query,
          sectors: searchData.sectors,
          skills: searchData.skills,
          used_profile_data: searchData.usedProfileData
        }
      })
      .execute();
  } catch (error) {
    console.error('Error inserting search analytics:', error);
    // Don't throw, just log the error
  }
} 