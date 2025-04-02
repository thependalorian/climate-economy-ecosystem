import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { metrics_service } from '../../../../lib/monitoring/metrics_service';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * POST handler for tracking profile enrichment metrics
 * @param {Object} request - The request object
 * @returns {Promise<NextResponse>} The response
 */
export async function POST(request) {
  try {
    const data = await request.json();
    const { userId, enrichmentData } = data;

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    // Track metrics with Python metrics service
    try {
      await metrics_service.track_profile_enrichment(userId, enrichmentData);
    } catch (error) {
      console.error('Error calling Python metrics service:', error);
      // Continue even if metrics service fails
    }

    // Store metrics in Supabase
    const { error } = await supabase
      .from('metrics')
      .insert({
        user_id: userId,
        event_type: 'profile_enrichment',
        event_data: {
          status: enrichmentData.status || 'unknown',
          skill_count: countSkills(enrichmentData.skills),
          data_sources: (enrichmentData.data_sources || []).length,
          is_verified: !!enrichmentData.is_verified,
          timestamp: new Date().toISOString()
        }
      });

    if (error) {
      console.error('Error storing metrics in Supabase:', error);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error in profile enrichment metrics API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/**
 * Count skills from all categories
 * @param {Object} skills - Skills object with categories as keys
 * @returns {number} Total number of skills
 */
function countSkills(skills) {
  if (!skills) return 0;
  
  return Object.values(skills).reduce((total, categorySkills) => {
    return total + (Array.isArray(categorySkills) ? categorySkills.length : 0);
  }, 0);
} 