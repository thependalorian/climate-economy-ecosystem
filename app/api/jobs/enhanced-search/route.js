import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

/**
 * Enhanced Job Search API
 * Handles requests for job searches with user profile enrichment data
 * Location: /app/api/jobs/enhanced-search/route.js
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
 * Run enhanced job search using Python script
 * @param {Object} userProfile - User profile
 * @param {Object} searchParams - Search parameters
 * @returns {Promise<Object>} Search results
 */
async function runEnhancedJobSearch(userProfile, searchParams) {
  try {
    // Convert profile and search params to JSON strings
    const profileJSON = JSON.stringify(userProfile);
    const paramsJSON = JSON.stringify(searchParams);
    
    // Determine script path
    const scriptPath = path.resolve(process.cwd(), 'climate_economy_ecosystem/tools/enhanced_job_search.py');
    
    // Execute the Python script
    const { stdout, stderr } = await execAsync(
      `python "${scriptPath}" '${profileJSON}' '${paramsJSON}' search`,
      { maxBuffer: 1024 * 1024 * 10 } // 10MB buffer for large results
    );
    
    if (stderr) {
      console.error('Python script error:', stderr);
    }
    
    // Parse the results from stdout
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error running enhanced job search:', error);
    throw new Error(`Failed to search jobs: ${error.message}`);
  }
}

/**
 * Run job recommendations using Python script
 * @param {Object} userProfile - User profile
 * @param {number} limit - Maximum number of recommendations
 * @returns {Promise<Object>} Recommendations
 */
async function runJobRecommendations(userProfile, limit = 10) {
  try {
    // Convert profile to JSON string
    const profileJSON = JSON.stringify(userProfile);
    const paramsJSON = JSON.stringify({ limit });
    
    // Determine script path
    const scriptPath = path.resolve(process.cwd(), 'climate_economy_ecosystem/tools/enhanced_job_search.py');
    
    // Execute the Python script with recommendations flag
    const { stdout, stderr } = await execAsync(
      `python "${scriptPath}" '${profileJSON}' '${paramsJSON}' recommendations`,
      { maxBuffer: 1024 * 1024 * 10 }
    );
    
    if (stderr) {
      console.error('Python script error:', stderr);
    }
    
    // Parse the results from stdout
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error running job recommendations:', error);
    throw new Error(`Failed to get recommendations: ${error.message}`);
  }
}

/**
 * POST handler for enhanced job search
 */
export async function POST(request) {
  try {
    // Get request body
    const body = await request.json();
    const { userId, searchParams = {}, recommendations = false } = body;
    
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
    
    // Run either job search or recommendations
    let results;
    if (recommendations) {
      // Get limit from search params
      const limit = searchParams.limit || 10;
      results = await runJobRecommendations(userProfile, limit);
    } else {
      // Run enhanced job search
      results = await runEnhancedJobSearch(userProfile, searchParams);
    }
    
    // Record search in analytics
    await recordSearchAnalytics(userId, searchParams, results.count);
    
    // Return response
    return NextResponse.json({
      success: true,
      ...results,
      user_id: userId
    });
    
  } catch (error) {
    console.error('Error processing enhanced job search:', error);
    
    return NextResponse.json(
      { error: 'Failed to search jobs', details: error.message, jobs: [], count: 0 },
      { status: 500 }
    );
  }
}

/**
 * GET handler for job recommendations
 */
export async function GET(request) {
  try {
    // Get URL parameters
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const limit = parseInt(searchParams.get('limit') || '10', 10);
    
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
    
    // Get job recommendations
    const recommendations = await runJobRecommendations(userProfile, limit);
    
    // Return response
    return NextResponse.json({
      success: true,
      jobs: recommendations,
      count: recommendations.length,
      user_id: userId
    });
    
  } catch (error) {
    console.error('Error processing job recommendations:', error);
    
    return NextResponse.json(
      { error: 'Failed to get job recommendations', details: error.message, jobs: [], count: 0 },
      { status: 500 }
    );
  }
}

/**
 * Record search analytics in Supabase
 * @param {string} userId - User ID
 * @param {Object} searchParams - Search parameters
 * @param {number} resultCount - Number of results
 */
async function recordSearchAnalytics(userId, searchParams, resultCount) {
  try {
    // Create analytics record
    const analyticsData = {
      user_id: userId,
      search_query: searchParams.query || '',
      search_type: 'enhanced_job_search',
      result_count: resultCount,
      search_params: searchParams,
      created_at: new Date().toISOString()
    };
    
    // Save to Supabase
    await supabase
      .from('search_analytics')
      .insert(analyticsData);
      
  } catch (error) {
    // Log error but don't fail the request
    console.error('Error recording search analytics:', error);
  }
} 