import { NextResponse } from 'next/server';
import { getActiveAlerts } from '../../../../lib/monitoring/metrics_service';

/**
 * Admin Alerts API Endpoint
 * Retrieves active system alerts for the admin dashboard
 * Location: /app/api/admin/alerts/route.js
 */

export async function GET() {
  try {    
    // Get active alerts using the metrics service
    const alerts = getActiveAlerts();
    
    // Return the alerts data
    return NextResponse.json({ alerts });
  } catch (error) {
    console.error('Error fetching alerts:', error);
    return NextResponse.json(
      { error: 'Failed to fetch alerts data' },
      { status: 500 }
    );
  }
} 