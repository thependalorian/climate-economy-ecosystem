import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'

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