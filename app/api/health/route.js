import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

/**
 * Health Check API Endpoint
 * 
 * This endpoint provides health status information for the application
 * and its dependencies (database, OpenAI API, storage).
 * 
 * @route GET /api/health
 * @returns {Object} Health status information
 */
export async function GET() {
  const startTime = Date.now();
  const healthStatus = {
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    services: {
      database: { status: 'unknown' },
      openai: { status: 'unknown' },
      storage: { status: 'unknown' }
    }
  };

  // Check database connection
  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY
    );
    
    const { data, error } = await supabase.from('migrations').select('*').limit(1);
    
    if (error) throw error;
    
    healthStatus.services.database = {
      status: 'ok',
      latency: `${Date.now() - startTime}ms`
    };
  } catch (error) {
    healthStatus.services.database = {
      status: 'error',
      message: error.message,
      latency: `${Date.now() - startTime}ms`
    };
    healthStatus.status = 'degraded';
  }
  
  // Check OpenAI API
  try {
    const openaiStartTime = Date.now();
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      }
    });
    
    if (!response.ok) throw new Error(`OpenAI API returned ${response.status}`);
    
    healthStatus.services.openai = {
      status: 'ok',
      latency: `${Date.now() - openaiStartTime}ms`
    };
  } catch (error) {
    healthStatus.services.openai = {
      status: 'error',
      message: error.message,
      latency: `${Date.now() - startTime}ms`
    };
    healthStatus.status = 'degraded';
  }
  
  // Check storage
  try {
    const storageStartTime = Date.now();
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.SUPABASE_SERVICE_KEY
    );
    
    const { data, error } = await supabase.storage.getBucket('user-documents');
    
    if (error) {
      // If bucket doesn't exist, try to create it
      if (error.message.includes('The resource was not found')) {
        const { data: createData, error: createError } = await supabase.storage.createBucket('user-documents', {
          public: false
        });
        
        if (createError) throw createError;
      } else {
        throw error;
      }
    }
    
    healthStatus.services.storage = {
      status: 'ok',
      latency: `${Date.now() - storageStartTime}ms`
    };
  } catch (error) {
    healthStatus.services.storage = {
      status: 'error',
      message: error.message,
      latency: `${Date.now() - startTime}ms`
    };
    healthStatus.status = 'degraded';
  }
  
  // Check Redis if enabled
  if (process.env.ENABLE_REDIS_CACHE === 'true') {
    try {
      const redisStartTime = Date.now();
      
      // Import Redis client dynamically
      const { createClient } = await import('redis');
      
      const redisClient = createClient({
        url: `redis://${process.env.REDIS_USERNAME}:${process.env.REDIS_PASSWORD}@${process.env.REDIS_HOST}:${process.env.REDIS_PORT}`
      });
      
      await redisClient.connect();
      await redisClient.ping();
      await redisClient.disconnect();
      
      healthStatus.services.redis = {
        status: 'ok',
        latency: `${Date.now() - redisStartTime}ms`
      };
    } catch (error) {
      healthStatus.services.redis = {
        status: 'error',
        message: error.message,
        latency: `${Date.now() - startTime}ms`
      };
      healthStatus.status = 'degraded';
    }
  }
  
  // Calculate total response time
  healthStatus.responseTime = `${Date.now() - startTime}ms`;
  
  // Set appropriate status code based on health status
  const statusCode = healthStatus.status === 'ok' ? 200 : 503;
  
  return NextResponse.json(healthStatus, { status: statusCode });
}
