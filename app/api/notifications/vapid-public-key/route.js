import { NextResponse } from 'next/server';

/**
 * VAPID Public Key API Endpoint
 * Returns the public key needed for push notification subscriptions
 * Location: /app/api/notifications/vapid-public-key/route.js
 */

export async function GET() {
  try {
    const publicKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
    
    if (!publicKey) {
      console.error('NEXT_PUBLIC_VAPID_PUBLIC_KEY is not defined in environment variables');
      return NextResponse.json(
        { error: 'VAPID public key not configured' },
        { status: 500 }
      );
    }
    
    return NextResponse.json({
      publicKey
    });
  } catch (error) {
    console.error('Error getting VAPID public key:', error);
    return NextResponse.json(
      { error: 'Failed to get VAPID public key' },
      { status: 500 }
    );
  }
} 