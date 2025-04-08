import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * GET handler for fetching all available climate sectors
 * @param {Object} request - The request object
 * @returns {Promise<NextResponse>} The response containing sectors data
 */
export async function GET() {
  try {
    // Fetch sectors data
    const { data: sectors, error } = await supabase
      .from('sectors')
      .select('*')
      .order('name');

    if (error) {
      console.error('Error fetching sectors:', error);
      return NextResponse.json({ error: 'Failed to fetch sectors' }, { status: 500 });
    }

    // Return the sectors data
    return NextResponse.json(sectors);
  } catch (error) {
    console.error('Error in sectors API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 