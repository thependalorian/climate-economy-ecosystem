# Supabase SSR Integration Guide

This guide explains how Supabase has been integrated with Next.js using Server-Side Rendering (SSR) for enhanced security, performance, and developer experience.

## Overview

Our implementation leverages Supabase's Auth Helpers for Next.js to securely handle sessions and data fetching on both the client and server side. This approach provides:

1. **Enhanced security** - API keys and tokens remain on the server
2. **Improved performance** - Data is pre-fetched on the server
3. **Better user experience** - Reduced loading states and flashes of unauthenticated content
4. **Type safety** - TypeScript integration throughout the codebase

## Implementation Architecture

### Core Files

The implementation consists of several key files:

| File | Purpose |
|------|---------|
| [`lib/supabase-server.js`](../lib/supabase-server.js) | Server-side Supabase client creation and utility functions |
| [`lib/supabase-client.js`](../lib/supabase-client.js) | Client-side Supabase client creation and utility functions |
| [`middleware.js`](../middleware.js) | Route protection and session refreshing |
| [`app/layout.jsx`](../app/layout.jsx) | Root layout with Provider configuration |

### Authentication Flow

1. **Session Management**:
   - Sessions are stored in cookies using the `createServerComponentClient` and `createClientComponentClient` from `@supabase/auth-helpers-nextjs`
   - The middleware automatically refreshes sessions on each request

2. **Route Protection**:
   - Protected routes (dashboard, profile, etc.) are defined in the middleware
   - Unauthenticated users are redirected to the login page with a redirect URL

3. **Server-Side Data Fetching**:
   - Server components use `createServerSupabaseClient()` to fetch data
   - This creates a Supabase client with proper cookie handling

## Usage Examples

### Server Component

```jsx
// Example server component
import { createServerSupabaseClient, getServerUser } from '@/lib/supabase-server';
import { redirect } from 'next/navigation';

export default async function Dashboard() {
  // Get the current user
  const user = await getServerUser();
  
  // Redirect if not authenticated
  if (!user) {
    redirect('/login?redirect=/dashboard');
  }
  
  // Fetch data from Supabase
  const supabase = createServerSupabaseClient();
  const { data: notifications } = await supabase
    .from('notifications')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(5);
  
  // Render with server-fetched data
  return (
    <div>
      <h1>Welcome, {user.email}</h1>
      <NotificationList notifications={notifications} />
    </div>
  );
}
```

### Client Component

```jsx
'use client';

import { useState, useEffect } from 'react';
import { getNotifications } from '@/lib/supabase-client';

export default function NotificationsTab() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadNotifications() {
      const data = await getNotifications();
      setNotifications(data);
      setLoading(false);
    }
    
    loadNotifications();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      {notifications.map(notification => (
        <div key={notification.id}>
          <h3>{notification.title}</h3>
          <p>{notification.message}</p>
        </div>
      ))}
    </div>
  );
}
```

## Utility Functions

### Server-Side Utilities

- `createServerSupabaseClient()` - Create a Supabase client for server components
- `getServerUser()` - Get the current authenticated user
- `getServerNotifications(userId, options)` - Fetch notifications for a user

### Client-Side Utilities

- `createClientSupabaseClient()` - Create a Supabase client for client components
- `signInWithEmail(email, password)` - Sign in with email and password
- `signOut()` - Sign out the current user
- `signUpWithEmail(email, password, metadata)` - Register a new user
- `getCurrentUser()` - Get the current authenticated user
- `getNotifications(options)` - Fetch notifications for the current user
- `markNotificationsAsRead(notificationIds, markAllRead)` - Mark notifications as read

## Best Practices

1. **Use server components wherever possible**
   - Server components provide better performance and security
   - Only use client components when you need interactivity

2. **Handle server errors gracefully**
   - Provide fallback UI for server errors
   - Use client-side error boundaries

3. **Avoid mixing server and client data fetching for the same resource**
   - Decide whether data should be fetched on the server or client
   - Use server components for initial data and client components for updates

4. **Follow Supabase Row Level Security (RLS) best practices**
   - Define RLS policies for all tables
   - Use policies to restrict access to data based on the user's ID

## Security Considerations

1. **API Keys**
   - The service role key is only used server-side and never exposed to the client
   - The public anon key is used for client-side requests with RLS protection

2. **Authentication**
   - All authentication happens through secure PKCE flows
   - Sessions are stored in HTTP-only cookies
   - The middleware refreshes sessions automatically

3. **Data Access**
   - Row Level Security (RLS) policies protect data on the database level
   - Server-side requests use appropriate policies for data access

## ACT Brand Integration

All components follow the ACT brand guidelines with:

1. **Color Palette**
   - Primary: Spring Green (#B2DE26)
   - Dark: Midnight Forest (#001818)
   - Secondary: Moss Green (#394816)
   - Light backgrounds: Seafoam Blue (#E0FFFF) and Sand Gray (#EBE9E1)

2. **Typography**
   - Helvetica for headings with -20 tracking and 32pt leading (for 28pt text)
   - Inter for body text with 1.5 line height

3. **Visual Elements**
   - Frame elements from the logo to highlight key content
   - Open brackets for layout structuring
   - Consistent photography guidelines

## Additional Resources

- [Supabase Auth Helpers Documentation](https://supabase.com/docs/guides/auth/auth-helpers/nextjs)
- [Next.js Server Components Documentation](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [ACT Brand Guidelines](../brand.md) 