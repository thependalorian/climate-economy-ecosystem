import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import { metrics_service } from './lib/monitoring/metrics_service'

/**
 * NextAuth Middleware
 * Handles authentication checks and redirects
 * Location: /middleware.js
 */

export async function middleware(req) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })

  // Refresh session if expired
  const { data: { session } } = await supabase.auth.getSession()
  const isLoggedIn = !!session
  const isAdmin = session?.user?.user_metadata?.role === 'admin'
  const { pathname } = req.nextUrl

  // Track API performance for metrics endpoints
  if (pathname.startsWith('/api/')) {
    const startTime = Date.now()
    
    // Add a response hook to track performance after the response is processed
    const originalRes = res.Response
    
    res.Response = function(...args) {
      const result = originalRes.apply(this, args)
      const statusCode = result.status
      
      // Track API performance metrics
      try {
        const duration = Date.now() - startTime
        const userId = session?.user?.id
        
        metrics_service.track_api_performance(
          pathname,
          duration,
          statusCode,
          userId,
          Object.fromEntries(req.nextUrl.searchParams)
        )
      } catch (error) {
        console.error('Error tracking API performance:', error)
      }
      
      return result
    }
  }

  // Redirect from login/register if already logged in
  if (isLoggedIn && (pathname === '/login' || pathname === '/register')) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  // Protected routes
  const protectedRoutes = [
    '/dashboard',
    '/profile',
    '/jobs/saved',
    '/training/saved'
  ]
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route))

  if (!isLoggedIn && isProtectedRoute) {
    return NextResponse.redirect(
      new URL(`/login?callbackUrl=${encodeURIComponent(pathname)}`, req.url)
    )
  }

  // Admin routes
  const adminRoutes = ['/admin']
  const isAdminRoute = adminRoutes.some(route => pathname.startsWith(route))
  if (isLoggedIn && isAdminRoute && !isAdmin) {
    return NextResponse.redirect(new URL('/', req.url))
  }

  return res
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
} 