import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { MemoryService } from '@/lib/memory/memory-service';
import { RedisCache } from '@/lib/redis/redis-client';

export async function GET(req) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // Get user ID
    const userId = session.user.id;
    
    // Initialize services
    const memoryService = new MemoryService();
    const redisCache = new RedisCache();
    
    // Try to get cached history
    try {
      const cacheKey = `history:${userId}`;
      const cachedHistory = await redisCache.get(cacheKey);
      if (cachedHistory) {
        return NextResponse.json({ 
          history: cachedHistory,
          cached: true 
        });
      }
    } catch (error) {
      console.error('Cache error:', error);
      // Continue without caching
    }
    
    try {
      // Get chat history from memory service
      const history = await memoryService.search_memories(
        "",  // Empty query to get all memories
        userId,
        20,  // Limit to 20 most recent
        ["chat"]  // Only get chat memories
      );
      
      // Format history
      const formattedHistory = history.map(item => ({
        id: item.id,
        query: item.metadata?.query || "",
        response: item.content,
        timestamp: item.metadata?.timestamp || new Date().toISOString()
      }));
      
      // Sort by timestamp (newest first)
      formattedHistory.sort((a, b) => b.timestamp - a.timestamp);
      
      // Try to cache the history
      try {
        await redisCache.set(`history:${userId}`, formattedHistory, 300);  // Cache for 5 minutes
      } catch (error) {
        console.error('Cache error:', error);
        // Continue without caching
      }
      
      return NextResponse.json({ history: formattedHistory });
    } catch (error) {
      console.error('Error getting chat history:', error);
      return NextResponse.json(
        { error: 'Error getting chat history', message: error.message },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Unhandled error:', error);
    return NextResponse.json(
      { error: 'Unhandled error', message: error.message },
      { status: 500 }
    );
  }
}
