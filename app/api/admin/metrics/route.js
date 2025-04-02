import { NextResponse } from 'next/server';
import { generateMockMetrics } from '../../../../lib/monitoring/metrics_service';

/**
 * Admin Metrics API Endpoint
 * Retrieves system-wide metrics data for the admin dashboard
 * Location: /app/api/admin/metrics/route.js
 */

export async function GET(request) {
  try {
    // Extract time range from query parameters
    const { searchParams } = new URL(request.url);
    const timeRange = searchParams.get('timeRange') || 'day';
    
    // Validate time range
    if (!['day', 'week', 'month'].includes(timeRange)) {
      return NextResponse.json(
        { error: 'Invalid time range. Must be one of: day, week, month' },
        { status: 400 }
      );
    }
    
    // In a real app, this would fetch actual metrics from a database
    // Here we're generating mock data
    const metrics = generateMockMetrics(timeRange);
    
    // Return the metrics data
    return NextResponse.json(metrics);
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return NextResponse.json(
      { error: 'Failed to fetch metrics data' },
      { status: 500 }
    );
  }
} 