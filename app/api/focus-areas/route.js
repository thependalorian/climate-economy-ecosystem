import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * GET handler for fetching all available climate focus areas
 * @param {Object} request - The request object
 * @returns {Promise<NextResponse>} The response containing focus areas data
 */
export async function GET() {
  try {
    // Fetch focus areas data
    const { data: focusAreas, error } = await supabase
      .from('focus_areas')
      .select('*')
      .order('name');

    if (error) {
      console.error('Error fetching focus areas:', error);
      return NextResponse.json({ error: 'Failed to fetch focus areas' }, { status: 500 });
    }

    // Return the focus areas data
    return NextResponse.json(focusAreas);
  } catch (error) {
    console.error('Error in focus areas API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 