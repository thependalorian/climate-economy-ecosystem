import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * API Route for Dashboard Data
 * Fetches personalized recommendations and engagement metrics
 * Location: /app/api/dashboard/data/route.js
 */
export async function GET() {
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
    
    // Get user profile for personalization
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('user_id', user.id)
      .single();
    
    // Determine user persona type (default if not set)
    const personaType = profile?.persona || 'default';
    
    // Get connection thresholds for this persona
    const { data: thresholds } = await supabase
      .from('connection_thresholds')
      .select('*')
      .eq('persona_type', personaType)
      .single();
    
    // If not found, get default thresholds
    const finalThresholds = thresholds || await supabase
      .from('connection_thresholds')
      .select('*')
      .eq('persona_type', 'default')
      .single()
      .then(res => res.data);
    
    // Get recommended opportunities (jobs, training, etc.)
    const { data: recommendations } = await supabase
      .from('recommendations')
      .select(`
        *,
        opportunity:opportunities (
          id,
          type,
          title,
          company_name,
          location,
          description,
          url,
          contact_name,
          contact_title,
          contact_email
        )
      `)
      .eq('user_id', user.id)
      .order('created_at', { ascending: false })
      .limit(5);
    
    // Get direct connections made
    const { data: connections } = await supabase
      .from('direct_connections')
      .select(`
        *,
        partner:partner_contacts (
          company_name,
          contact_name,
          contact_title
        )
      `)
      .eq('user_id', user.id)
      .order('connected_at', { ascending: false })
      .limit(5);
    
    // Get engagement metrics
    const { data: metrics } = await supabase
      .from('user_engagement')
      .select('*')
      .eq('user_id', user.id)
      .single();
    
    // Get upcoming partner events
    const { data: events } = await supabase
      .from('partner_events')
      .select('*')
      .gte('date', new Date().toISOString())
      .limit(5)
      .order('date', { ascending: true });
    
    // Calculate profile strength
    const profileStrength = calculateProfileStrength(profile);
    
    // Determine connection eligibility 
    const eligibility = {
      profileStrength: {
        current: profileStrength,
        required: finalThresholds?.profile_strength_min || 70,
        achieved: profileStrength >= (finalThresholds?.profile_strength_min || 70)
      },
      engagementScore: {
        current: metrics?.engagement_score || 0,
        required: finalThresholds?.engagement_score_min || 50,
        achieved: (metrics?.engagement_score || 0) >= (finalThresholds?.engagement_score_min || 50)
      },
      averageMatchScore: {
        current: calculateAverageMatchScore(recommendations),
        required: finalThresholds?.match_score_min || 75,
        achieved: calculateAverageMatchScore(recommendations) >= (finalThresholds?.match_score_min || 75)
      }
    };
    
    // Overall eligibility requires all criteria to be met
    const isEligibleForDirectConnection = 
      eligibility.profileStrength.achieved && 
      eligibility.engagementScore.achieved && 
      eligibility.averageMatchScore.achieved;
    
    return NextResponse.json({
      profile,
      persona: personaType,
      engagement: {
        recommendations_received: metrics?.recommendations_count || 0,
        direct_connections: metrics?.connections_count || 0,
        resources_accessed: metrics?.resources_accessed || 0,
        satisfaction_score: metrics?.satisfaction_score || 0,
        engagement_score: metrics?.engagement_score || 0
      },
      recommendations: recommendations?.map(rec => ({
        ...rec.opportunity,
        match_score: rec.match_score,
        recommended_at: rec.created_at
      })) || [],
      recent_connections: connections || [],
      upcoming_events: events || [],
      profileStrength: profileStrength,
      connectionEligibility: {
        ...eligibility,
        isEligible: isEligibleForDirectConnection
      },
      thresholds: {
        persona: personaType,
        profile_strength_min: finalThresholds?.profile_strength_min || 70,
        engagement_score_min: finalThresholds?.engagement_score_min || 50,
        match_score_min: finalThresholds?.match_score_min || 75
      }
    });
    
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' },
      { status: 500 }
    );
  }
}

/**
 * Calculate profile strength percentage
 */
function calculateProfileStrength(profile) {
  if (!profile) return 0;
  
  const fields = [
    'full_name',
    'location',
    'bio',
    'skills',
    'experience',
    'education',
    'certifications',
    'interests'
  ];
  
  const completedFields = fields.filter(field => 
    profile[field] && 
    (Array.isArray(profile[field]) ? profile[field].length > 0 : true)
  );
  
  return Math.round((completedFields.length / fields.length) * 100);
}

/**
 * Calculate average match score across recommendations
 */
function calculateAverageMatchScore(recommendations) {
  if (!recommendations || recommendations.length === 0) {
    return 0;
  }
  
  const totalScore = recommendations.reduce((sum, rec) => sum + (rec.match_score || 0), 0);
  return Math.round(totalScore / recommendations.length);
} 