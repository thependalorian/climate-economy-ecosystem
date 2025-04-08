import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

/**
 * API Route for Requesting Direct Connections
 * Verifies eligibility and processes connection requests to partner companies
 * Location: /app/api/connections/request/route.js
 */
export async function POST(request) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const requestData = await request.json();
    
    // Validate the request data
    if (!requestData.opportunityId) {
      return NextResponse.json(
        { error: 'Missing opportunity ID' },
        { status: 400 }
      );
    }
    
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
    
    // Get the opportunity details
    const { data: opportunity } = await supabase
      .from('opportunities')
      .select('*')
      .eq('id', requestData.opportunityId)
      .single();
    
    if (!opportunity) {
      return NextResponse.json(
        { error: 'Opportunity not found' },
        { status: 404 }
      );
    }
    
    // Get recommendation with match score
    const { data: recommendation } = await supabase
      .from('recommendations')
      .select('*')
      .eq('user_id', user.id)
      .eq('opportunity_id', requestData.opportunityId)
      .single();
    
    // Get user engagement metrics
    const { data: metrics } = await supabase
      .from('user_engagement')
      .select('*')
      .eq('user_id', user.id)
      .single();
    
    // If no metrics yet, create a new record
    if (!metrics) {
      const { data: newMetrics, error } = await supabase
        .from('user_engagement')
        .insert({
          user_id: user.id,
          recommendations_count: 0,
          recommendations_clicked: 0,
          resources_accessed: 0,
          connections_count: 0,
          connection_requests: 1,
          profile_updates: 0,
          logins_count: 1,
          satisfaction_score: 0
        })
        .select()
        .single();
        
      if (error) throw error;
      metrics = newMetrics;
    } else {
      // Update engagement metrics - increment connection requests
      const { error } = await supabase
        .from('user_engagement')
        .update({
          connection_requests: (metrics.connection_requests || 0) + 1,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', user.id);
      
      if (error) throw error;
    }
    
    // Calculate profile strength
    const profileStrength = calculateProfileStrength(profile);
    
    // Get all recommendations to calculate average match score
    const { data: allRecommendations } = await supabase
      .from('recommendations')
      .select('match_score')
      .eq('user_id', user.id);
    
    const averageMatchScore = calculateAverageMatchScore(allRecommendations);
    
    // Check eligibility
    const isProfileStrengthSufficient = profileStrength >= (finalThresholds?.profile_strength_min || 70);
    const isEngagementScoreSufficient = (metrics?.engagement_score || 0) >= (finalThresholds?.engagement_score_min || 50);
    const isMatchScoreSufficient = averageMatchScore >= (finalThresholds?.match_score_min || 75);
    
    // All criteria must be met for eligibility
    const isEligible = isProfileStrengthSufficient && isEngagementScoreSufficient && isMatchScoreSufficient;
    
    if (!isEligible) {
      return NextResponse.json(
        { 
          error: 'Not eligible for direct connection', 
          details: {
            profileStrength: { 
              current: profileStrength, 
              required: finalThresholds?.profile_strength_min || 70, 
              achieved: isProfileStrengthSufficient 
            },
            engagementScore: { 
              current: metrics?.engagement_score || 0, 
              required: finalThresholds?.engagement_score_min || 50, 
              achieved: isEngagementScoreSufficient 
            },
            matchScore: { 
              current: averageMatchScore, 
              required: finalThresholds?.match_score_min || 75, 
              achieved: isMatchScoreSufficient 
            }
          }
        },
        { status: 403 }
      );
    }
    
    // Check if connection already exists
    const { data: existingConnection } = await supabase
      .from('direct_connections')
      .select('*')
      .eq('user_id', user.id)
      .eq('opportunity_id', requestData.opportunityId)
      .single();
    
    if (existingConnection) {
      return NextResponse.json(
        { 
          message: 'Connection already requested',
          connection: existingConnection
        },
        { status: 200 }
      );
    }
    
    // Create direct connection
    const { data: connection, error: connectionError } = await supabase
      .from('direct_connections')
      .insert({
        user_id: user.id,
        opportunity_id: requestData.opportunityId,
        company_name: opportunity.company_name,
        status: 'pending',
        notes: requestData.notes || '',
        connected_at: new Date().toISOString(),
        partner_contact_id: opportunity.contact_id
      })
      .select()
      .single();
    
    if (connectionError) throw connectionError;
    
    // Update engagement metrics - increment connections count
    const { error: updateError } = await supabase
      .from('user_engagement')
      .update({
        connections_count: (metrics.connections_count || 0) + 1,
        updated_at: new Date().toISOString()
      })
      .eq('user_id', user.id);
    
    if (updateError) throw updateError;
    
    return NextResponse.json({
      message: 'Connection request submitted successfully',
      connection
    });
    
  } catch (error) {
    console.error('Error requesting connection:', error);
    return NextResponse.json(
      { error: 'Failed to request connection' },
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