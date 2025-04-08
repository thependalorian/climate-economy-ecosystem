import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * GET handler for fetching a user's profile data
 * @param {Object} request - The request object
 * @param {Object} context - The context containing params
 * @returns {Promise<NextResponse>} The response containing profile data
 */
export async function GET(request, { params }) {
  try {
    const { userId } = params;

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    // Fetch user profile
    const { data: profile, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single();

    if (error) {
      console.error('Error fetching profile:', error);
      return NextResponse.json({ error: 'Failed to fetch user profile' }, { status: 500 });
    }

    if (!profile) {
      return NextResponse.json({ error: 'Profile not found' }, { status: 404 });
    }

    // Return the profile data
    return NextResponse.json(profile);
  } catch (error) {
    console.error('Error in profile API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/**
 * PATCH handler for updating a user's profile data
 * @param {Object} request - The request object
 * @param {Object} context - The context containing params
 * @returns {Promise<NextResponse>} The response containing updated profile data
 */
export async function PATCH(request, { params }) {
  try {
    const { userId } = params;
    
    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }
    
    const requestData = await request.json();
    
    // Update the profile
    const { data: updatedProfile, error } = await supabase
      .from('profiles')
      .update(requestData)
      .eq('id', userId)
      .select()
      .single();
      
    if (error) {
      console.error('Error updating profile:', error);
      return NextResponse.json({ error: 'Failed to update user profile' }, { status: 500 });
    }
    
    return NextResponse.json(updatedProfile);
  } catch (error) {
    console.error('Error in profile update API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 