import { NextResponse } from 'next/server';
import { metrics_service } from '@/lib/monitoring/metrics_service';
import { auth } from '@/auth';
import supabaseAdmin from '@/lib/supabase-api';
import webpush from 'web-push';

/**
 * Notifications Registration API
 * Handles registration of push notification subscriptions
 * Location: /app/api/notifications/register/route.js
 */

// Configure web-push
webpush.setVapidDetails(
  'mailto:info@mass-clean-tech.org',
  process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
  process.env.VAPID_PRIVATE_KEY
);

export async function POST(request) {
  try {
    // Parse the request body
    const body = await request.json();
    const { subscription, user_id } = body;
    
    if (!subscription || !subscription.endpoint) {
      return NextResponse.json(
        { error: 'Invalid subscription object' },
        { status: 400 }
      );
    }
    
    // Get authenticated user
    const session = await auth();
    const authenticatedUserId = session?.user?.id;
    
    // Security check: Only allow users to register for themselves
    // or admins to register for any user
    if (authenticatedUserId && authenticatedUserId !== user_id) {
      const { data: userData } = await supabaseAdmin
        .from('profiles')
        .select('role')
        .eq('id', authenticatedUserId)
        .single();
      
      if (!userData || userData.role !== 'admin') {
        return NextResponse.json(
          { error: 'Unauthorized to register for this user' },
          { status: 403 }
        );
      }
    }
    
    // Check if subscription already exists
    const { data: existingSubscription } = await supabaseAdmin
      .from('push_subscriptions')
      .select('id')
      .eq('endpoint', subscription.endpoint)
      .eq('user_id', user_id)
      .single();
    
    if (existingSubscription) {
      // Update existing subscription
      await supabaseAdmin
        .from('push_subscriptions')
        .update({
          subscription_json: JSON.stringify(subscription),
          updated_at: new Date().toISOString()
        })
        .eq('id', existingSubscription.id);
      
      // Track update event
      await metrics_service.track_event(
        'push_subscription_updated',
        user_id,
        { endpoint: subscription.endpoint }
      );
      
      return NextResponse.json({
        success: true,
        message: 'Subscription updated successfully'
      });
    } else {
      // Create new subscription
      await supabaseAdmin
        .from('push_subscriptions')
        .insert([
          {
            user_id,
            endpoint: subscription.endpoint,
            subscription_json: JSON.stringify(subscription),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ]);
      
      // Track creation event
      await metrics_service.track_event(
        'push_subscription_created',
        user_id,
        { endpoint: subscription.endpoint }
      );
      
      // Send a welcome notification
      const payload = JSON.stringify({
        title: 'Notifications Enabled',
        body: 'You will now receive updates from the Massachusetts Clean Tech Ecosystem.',
        icon: '/icons/logo-192.png',
        data: {
          url: '/dashboard'
        }
      });
      
      try {
        await webpush.sendNotification(subscription, payload);
      } catch (pushError) {
        console.error('Error sending welcome notification:', pushError);
        // Continue even if the welcome notification fails
      }
      
      return NextResponse.json({
        success: true,
        message: 'Subscription registered successfully'
      });
    }
  } catch (error) {
    console.error('Error registering push subscription:', error);
    
    // Track error event
    await metrics_service.track_event(
      'push_subscription_error',
      'system',
      { error: error.message }
    );
    
    return NextResponse.json(
      { error: 'Failed to register subscription', message: error.message },
      { status: 500 }
    );
  }
}

export async function DELETE(request) {
  try {
    const { searchParams } = new URL(request.url);
    const endpoint = searchParams.get('endpoint');
    
    if (!endpoint) {
      return NextResponse.json(
        { error: 'Endpoint parameter is required' },
        { status: 400 }
      );
    }
    
    // Get authenticated user
    const session = await auth();
    const userId = session?.user?.id;
    
    if (!userId) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Delete the subscription
    const { error } = await supabaseAdmin
      .from('push_subscriptions')
      .delete()
      .eq('endpoint', endpoint)
      .eq('user_id', userId);
    
    if (error) {
      throw new Error(`Database error: ${error.message}`);
    }
    
    // Track deletion event
    await metrics_service.track_event(
      'push_subscription_deleted',
      userId,
      { endpoint }
    );
    
    return NextResponse.json({
      success: true,
      message: 'Subscription removed successfully'
    });
  } catch (error) {
    console.error('Error removing push subscription:', error);
    
    return NextResponse.json(
      { error: 'Failed to remove subscription', message: error.message },
      { status: 500 }
    );
  }
} 