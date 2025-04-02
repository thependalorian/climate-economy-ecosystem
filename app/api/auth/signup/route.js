import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

// Initialize Supabase client with admin privileges
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

export async function POST(request) {
  try {
    // Parse request body
    const body = await request.json();
    const { name, email, password, location, is_ej_community, is_veteran } = body;
    
    // Validate required fields
    if (!email || !password) {
      return NextResponse.json(
        { message: 'Email and password are required' },
        { status: 400 }
      );
    }
    
    // Create a new user in Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true, // Auto-confirm email for development
      user_metadata: {
        name,
        location,
        is_ej_community,
        is_veteran
      },
    });
    
    if (authError) {
      console.error('Error creating user:', authError);
      return NextResponse.json(
        { message: authError.message },
        { status: 400 }
      );
    }
    
    // Create user profile in the database
    const { data: profileData, error: profileError } = await supabase
      .from('user_profiles')
      .insert({
        user_id: authData.user.id,
        name: name || email.split('@')[0], // Use name or fallback to email username
        email,
        location,
        is_ej_community: is_ej_community || false,
        is_veteran: is_veteran || false,
        preferences: {},
      })
      .select();
      
    if (profileError) {
      console.error('Error creating user profile:', profileError);
      // Don't fail the signup if profile creation fails
      // We can sync profile later
    }
    
    // Identify user as from EJ community or veteran for special onboarding
    let special_status = [];
    if (is_ej_community) special_status.push('ej_community');
    if (is_veteran) special_status.push('veteran');
    
    return NextResponse.json({
      message: 'User created successfully',
      userId: authData.user.id,
      special_status
    });
  } catch (error) {
    console.error('Signup error:', error);
    return NextResponse.json(
      { message: 'An error occurred during sign up' },
      { status: 500 }
    );
  }
}

// Handle OPTIONS requests for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
} 