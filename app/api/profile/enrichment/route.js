import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

/**
 * Profile Enrichment API
 * Handles requests to enrich user profiles with additional information
 * Location: /app/api/profile/enrichment/route.js
 */

// Convert exec to promise-based
const execAsync = promisify(exec);

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Fetch user profile from Supabase
 * @param {string} userId - User ID
 * @returns {Promise<Object>} User profile
 */
async function fetchUserProfile(userId) {
  try {
    const { data, error } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', userId)
      .single();
      
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
}

/**
 * Update user profile with enriched data
 * @param {string} userId - User ID
 * @param {Object} enrichedProfile - Enriched profile data
 * @returns {Promise<Object>} Updated user profile
 */
async function updateUserProfile(userId, enrichedProfile) {
  try {
    const { data, error } = await supabase
      .from('user_profiles')
      .update(enrichedProfile)
      .eq('id', userId)
      .select()
      .single();
      
    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Error updating user profile:', error);
    throw error;
  }
}

/**
 * Run profile enrichment using Python script
 * @param {Object} userProfile - User profile to enrich
 * @param {Object} options - Enrichment options
 * @returns {Promise<Object>} Enriched profile
 */
async function runProfileEnrichment(userProfile, options = {}) {
  try {
    // Convert profile and options to JSON string
    const profileJSON = JSON.stringify(userProfile);
    const optionsJSON = JSON.stringify(options);
    
    // Determine script path - adjust as needed based on your project structure
    const scriptPath = path.resolve(process.cwd(), 'climate_economy_ecosystem/tools/profile_enrichment.py');
    
    // Execute the Python script
    const { stdout, stderr } = await execAsync(
      `python "${scriptPath}" '${profileJSON}' '${optionsJSON}'`,
      { maxBuffer: 1024 * 1024 * 10 } // 10MB buffer for large profiles
    );
    
    if (stderr) {
      console.error('Python script error:', stderr);
    }
    
    // Parse the enriched profile from stdout
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error running profile enrichment:', error);
    throw new Error(`Failed to enrich profile: ${error.message}`);
  }
}

/**
 * POST handler for profile enrichment
 */
export async function POST(request) {
  try {
    // Get request body
    const body = await request.json();
    const { userId, options = {} } = body;
    
    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }
    
    // Fetch user profile
    const userProfile = await fetchUserProfile(userId);
    
    if (!userProfile) {
      return NextResponse.json(
        { error: 'User profile not found' },
        { status: 404 }
      );
    }
    
    // Run profile enrichment
    const enrichedProfile = await runProfileEnrichment(userProfile, options);
    
    // Update user profile
    const updatedProfile = await updateUserProfile(userId, enrichedProfile);
    
    // Return response
    return NextResponse.json({
      success: true,
      profile: updatedProfile,
      message: 'Profile enrichment completed'
    });
    
  } catch (error) {
    console.error('Error processing profile enrichment:', error);
    
    return NextResponse.json(
      { error: 'Failed to enrich profile', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * PUT handler for verifying enriched data
 */
export async function PUT(request) {
  try {
    // Get request body
    const body = await request.json();
    const { userId, verifiedData } = body;
    
    if (!userId || !verifiedData) {
      return NextResponse.json(
        { error: 'User ID and verified data are required' },
        { status: 400 }
      );
    }
    
    // Fetch user profile
    const userProfile = await fetchUserProfile(userId);
    
    if (!userProfile) {
      return NextResponse.json(
        { error: 'User profile not found' },
        { status: 404 }
      );
    }
    
    // Determine script path
    const scriptPath = path.resolve(process.cwd(), 'climate_economy_ecosystem/tools/profile_enrichment.py');
    
    // Convert data to JSON strings
    const profileJSON = JSON.stringify(userProfile);
    const verifiedDataJSON = JSON.stringify(verifiedData);
    
    // Execute the Python script with verification flag
    const { stdout, stderr } = await execAsync(
      `python "${scriptPath}" '${profileJSON}' '${verifiedDataJSON}' --verify`,
      { maxBuffer: 1024 * 1024 * 10 }
    );
    
    if (stderr) {
      console.error('Python script error:', stderr);
    }
    
    // Parse the updated profile
    const updatedProfile = JSON.parse(stdout);
    
    // Update user profile in Supabase
    const result = await updateUserProfile(userId, updatedProfile);
    
    // Return response
    return NextResponse.json({
      success: true,
      profile: result,
      message: 'Profile enrichment data verified and saved'
    });
    
  } catch (error) {
    console.error('Error verifying enriched data:', error);
    
    return NextResponse.json(
      { error: 'Failed to verify enriched data', details: error.message },
      { status: 500 }
    );
  }
} 