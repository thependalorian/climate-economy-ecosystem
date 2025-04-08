import { NextResponse } from 'next/server';
import { getToken } from 'next-auth/jwt';
import { tracingService } from '@/lib/tracing/langsmith-client';

export async function middleware(request) {
  // Create a unique run ID for tracing
  const runId = tracingService.createRunId();
  
  // Create a tracer
  const tracer = tracingService.createTracer(runId, 'middleware');
  
  try {
    // Start span
    const span = tracer.startSpan({
      name: 'middleware_request',
      inputs: { 
        path: request.nextUrl.pathname,
        method: request.method
      },
      runType: 'chain'
    });
    
    // Check if the request is for an API route
    if (request.nextUrl.pathname.startsWith('/api/')) {
      // For API routes, check authentication
      const token = await getToken({ req: request });
      
      // If no token and not a public API route, redirect to login
      if (!token && !isPublicApiRoute(request.nextUrl.pathname)) {
        span.end({
          outputs: { 
            result: 'unauthorized',
            redirect: '/api/auth/signin'
          }
        });
        
        tracer.end();
        
        return NextResponse.json(
          { error: 'Unauthorized' },
          { status: 401 }
        );
      }
    }
    
    // End span with success
    span.end({
      outputs: { 
        result: 'success'
      }
    });
    
    tracer.end();
    
    // Continue with the request
    return NextResponse.next();
  } catch (error) {
    console.error('Middleware error:', error);
    
    // Record error in trace
    try {
      const errorSpan = tracer.startSpan({
        name: 'middleware_error',
        inputs: { error: error.message },
        runType: 'chain'
      });
      
      errorSpan.end();
      tracer.end();
    } catch (tracingError) {
      console.error('Error recording tracing:', tracingError);
    }
    
    // Continue with the request despite the error
    return NextResponse.next();
  }
}

// Define which API routes are public
function isPublicApiRoute(pathname) {
  const publicRoutes = [
    '/api/auth',
    '/api/health',
    '/api/public'
  ];
  
  return publicRoutes.some(route => pathname.startsWith(route));
}

// Configure which routes use this middleware
export const config = {
  matcher: [
    '/api/:path*',
    '/dashboard/:path*',
    '/profile/:path*'
  ]
};
