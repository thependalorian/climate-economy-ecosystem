import { createClient } from '@supabase/supabase-js';
import { getSession } from 'next-auth/react';
import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import { metrics_service } from '@/lib/monitoring/metrics_service';

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Notifications API
 * 
 * Provides endpoints for managing user notifications:
 * - GET: Retrieve notifications for a user
 * - POST: Create a new notification
 * - PUT: Mark notifications as read
 * - DELETE: Delete notifications
 */

// GET endpoint to retrieve notifications
export async function GET(request) {
  try {
    // Get user session for authentication
    const session = await getSession({ req: request });
    
    // Check if user is authenticated
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized access' },
        { status: 401 }
      );
    }
    
    const userId = session.user.id;
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '20');
    const offset = parseInt(searchParams.get('offset') || '0');
    const includeRead = searchParams.get('includeRead') === 'true';
    
    // Track metrics for API call
    await metrics_service.track_api_performance(
      '/api/notifications',
      0, // Will update duration at the end
      200,
      userId,
      { method: 'GET', limit, offset, includeRead }
    );
    
    // Start timing the request
    const startTime = Date.now();
    
    // Build the query
    let query = supabase
      .from('notifications')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);
    
    // Filter by read status if includeRead is false
    if (!includeRead) {
      query = query.eq('read', false);
    }
    
    // Execute the query
    const { data: notifications, error } = await query;
    
    if (error) {
      console.error('Error fetching notifications:', error);
      
      await metrics_service.track_api_performance(
        '/api/notifications',
        Date.now() - startTime,
        500,
        userId,
        { method: 'GET', error: error.message }
      );
      
      return NextResponse.json(
        { error: 'Failed to fetch notifications' },
        { status: 500 }
      );
    }
    
    // Also get the count of unread notifications for the badge count
    const { count: unreadCount, error: countError } = await supabase
      .from('notifications')
      .select('*', { count: 'exact' })
      .eq('user_id', userId)
      .eq('read', false);
    
    if (countError) {
      console.error('Error counting unread notifications:', countError);
    }
    
    // Calculate the duration and update metrics
    const duration = Date.now() - startTime;
    await metrics_service.track_api_performance(
      '/api/notifications',
      duration,
      200,
      userId,
      { 
        method: 'GET', 
        count: notifications?.length || 0,
        duration_ms: duration 
      }
    );
    
    // Return the notifications and unread count
    return NextResponse.json({
      notifications: notifications || [],
      unreadCount: unreadCount || 0,
      metadata: {
        limit,
        offset,
        duration_ms: duration
      }
    });
  } catch (error) {
    console.error('Unexpected error in notifications GET:', error);
    return NextResponse.json(
      { error: 'Server error' },
      { status: 500 }
    );
  }
}

// POST endpoint to create a new notification
export async function POST(request) {
  try {
    // Start timing the request
    const startTime = Date.now();
    
    // Parse the request body
    const body = await request.json();
    const { 
      user_id, 
      title, 
      message, 
      type = 'info', 
      link = null,
      metadata = {}
    } = body;
    
    // Validate required fields
    if (!user_id || !title || !message) {
      return NextResponse.json(
        { error: 'Missing required fields: user_id, title, and message are required' },
        { status: 400 }
      );
    }
    
    // Check if the request is authorized
    // This could be from an admin, system, or authenticated service
    const session = await getSession({ req: request });
    const isSystem = body.sender === 'system' && body.system_key === process.env.NOTIFICATION_SYSTEM_KEY;
    
    // Only allow notifications to be created by authenticated users for themselves or by the system
    if (!session?.user && !isSystem) {
      return NextResponse.json(
        { error: 'Unauthorized access' },
        { status: 401 }
      );
    }
    
    // If it's a user, they can only create notifications for themselves
    if (session?.user && !isSystem && session.user.id !== user_id) {
      return NextResponse.json(
        { error: 'Unauthorized: You can only create notifications for yourself' },
        { status: 403 }
      );
    }
    
    // Generate a unique ID for the notification
    const notification_id = uuidv4();
    
    // Create the notification
    const { data, error } = await supabase
      .from('notifications')
      .insert([
        {
          id: notification_id,
          user_id,
          title,
          message,
          type,
          link,
          read: false,
          metadata,
          created_at: new Date().toISOString()
        }
      ])
      .select();
    
    if (error) {
      console.error('Error creating notification:', error);
      
      await metrics_service.track_api_performance(
        '/api/notifications',
        Date.now() - startTime,
        500,
        user_id,
        { method: 'POST', error: error.message }
      );
      
      return NextResponse.json(
        { error: 'Failed to create notification' },
        { status: 500 }
      );
    }
    
    // Calculate the duration and update metrics
    const duration = Date.now() - startTime;
    await metrics_service.track_api_performance(
      '/api/notifications',
      duration,
      201,
      user_id,
      { 
        method: 'POST', 
        notification_id,
        type,
        duration_ms: duration 
      }
    );
    
    // Track event for the notification creation
    await metrics_service.track_event(
      'notification_created',
      user_id,
      {
        notification_id,
        type,
        has_link: !!link
      }
    );
    
    // Return the created notification
    return NextResponse.json({
      success: true,
      notification: data[0],
      message: 'Notification created successfully'
    }, { status: 201 });
  } catch (error) {
    console.error('Unexpected error in notifications POST:', error);
    return NextResponse.json(
      { error: 'Server error' },
      { status: 500 }
    );
  }
}

// PUT endpoint to mark notifications as read
export async function PUT(request) {
  try {
    // Start timing the request
    const startTime = Date.now();
    
    // Get user session for authentication
    const session = await getSession({ req: request });
    
    // Check if user is authenticated
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized access' },
        { status: 401 }
      );
    }
    
    const userId = session.user.id;
    
    // Parse the request body
    const body = await request.json();
    const { 
      notification_ids,
      mark_all_read = false
    } = body;
    
    // Validate the request
    if (!mark_all_read && (!notification_ids || !Array.isArray(notification_ids) || notification_ids.length === 0)) {
      return NextResponse.json(
        { error: 'Missing notification_ids or mark_all_read parameter' },
        { status: 400 }
      );
    }
    
    let updateResult;
    
    // Mark all notifications as read if requested
    if (mark_all_read) {
      updateResult = await supabase
        .from('notifications')
        .update({ read: true, updated_at: new Date().toISOString() })
        .eq('user_id', userId)
        .eq('read', false);
    } else {
      // Otherwise mark specific notifications as read
      updateResult = await supabase
        .from('notifications')
        .update({ read: true, updated_at: new Date().toISOString() })
        .in('id', notification_ids)
        .eq('user_id', userId); // Ensure the user can only update their own notifications
    }
    
    const { error } = updateResult;
    
    if (error) {
      console.error('Error marking notifications as read:', error);
      
      await metrics_service.track_api_performance(
        '/api/notifications',
        Date.now() - startTime,
        500,
        userId,
        { method: 'PUT', error: error.message }
      );
      
      return NextResponse.json(
        { error: 'Failed to mark notifications as read' },
        { status: 500 }
      );
    }
    
    // Calculate the duration and update metrics
    const duration = Date.now() - startTime;
    await metrics_service.track_api_performance(
      '/api/notifications',
      duration,
      200,
      userId,
      { 
        method: 'PUT', 
        mark_all_read,
        notification_count: mark_all_read ? 'all' : notification_ids.length,
        duration_ms: duration 
      }
    );
    
    // Track event for the notification update
    await metrics_service.track_event(
      'notifications_marked_read',
      userId,
      {
        mark_all_read,
        count: mark_all_read ? 'all' : notification_ids.length
      }
    );
    
    // Return success response
    return NextResponse.json({
      success: true,
      message: mark_all_read 
        ? 'All notifications marked as read' 
        : `${notification_ids.length} notification(s) marked as read`
    });
  } catch (error) {
    console.error('Unexpected error in notifications PUT:', error);
    return NextResponse.json(
      { error: 'Server error' },
      { status: 500 }
    );
  }
}

// DELETE endpoint to delete notifications
export async function DELETE(request) {
  try {
    // Start timing the request
    const startTime = Date.now();
    
    // Get user session for authentication
    const session = await getSession({ req: request });
    
    // Check if user is authenticated
    if (!session?.user) {
      return NextResponse.json(
        { error: 'Unauthorized access' },
        { status: 401 }
      );
    }
    
    const userId = session.user.id;
    
    // Parse the request body
    const body = await request.json();
    const { 
      notification_ids,
      delete_all_read = false,
      delete_all = false
    } = body;
    
    // Validate the request
    if (!delete_all_read && !delete_all && (!notification_ids || !Array.isArray(notification_ids) || notification_ids.length === 0)) {
      return NextResponse.json(
        { error: 'Missing notification_ids, delete_all_read, or delete_all parameter' },
        { status: 400 }
      );
    }
    
    let deleteResult;
    
    if (delete_all) {
      // Delete all notifications for the user
      deleteResult = await supabase
        .from('notifications')
        .delete()
        .eq('user_id', userId);
    } else if (delete_all_read) {
      // Delete all read notifications for the user
      deleteResult = await supabase
        .from('notifications')
        .delete()
        .eq('user_id', userId)
        .eq('read', true);
    } else {
      // Delete specific notifications
      deleteResult = await supabase
        .from('notifications')
        .delete()
        .in('id', notification_ids)
        .eq('user_id', userId); // Ensure the user can only delete their own notifications
    }
    
    const { error } = deleteResult;
    
    if (error) {
      console.error('Error deleting notifications:', error);
      
      await metrics_service.track_api_performance(
        '/api/notifications',
        Date.now() - startTime,
        500,
        userId,
        { method: 'DELETE', error: error.message }
      );
      
      return NextResponse.json(
        { error: 'Failed to delete notifications' },
        { status: 500 }
      );
    }
    
    // Calculate the duration and update metrics
    const duration = Date.now() - startTime;
    await metrics_service.track_api_performance(
      '/api/notifications',
      duration,
      200,
      userId,
      { 
        method: 'DELETE', 
        delete_all,
        delete_all_read,
        notification_count: delete_all ? 'all' : (delete_all_read ? 'all_read' : notification_ids.length),
        duration_ms: duration 
      }
    );
    
    // Track event for the notification deletion
    await metrics_service.track_event(
      'notifications_deleted',
      userId,
      {
        delete_all,
        delete_all_read,
        count: delete_all ? 'all' : (delete_all_read ? 'all_read' : notification_ids.length)
      }
    );
    
    // Return success response
    return NextResponse.json({
      success: true,
      message: delete_all 
        ? 'All notifications deleted' 
        : (delete_all_read 
            ? 'All read notifications deleted' 
            : `${notification_ids.length} notification(s) deleted`)
    });
  } catch (error) {
    console.error('Unexpected error in notifications DELETE:', error);
    return NextResponse.json(
      { error: 'Server error' },
      { status: 500 }
    );
  }
} 