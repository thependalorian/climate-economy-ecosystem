import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { MemoryService } from '@/lib/memory/memory-service';
import { RedisCache } from '@/lib/redis/redis-client';

export async function POST(req) {
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
    
    try {
      // Get chat history from memory service
      const history = await memoryService.search_memories(
        "",  // Empty query to get all memories
        userId,
        100,  // Get up to 100 memories
        ["chat"]  // Only get chat memories
      );
      
      // Delete each memory
      let deletedCount = 0;
      for (const item of history) {
        await memoryService.delete_memory(item.id);
        deletedCount++;
      }
      
      // Clear cache
      try {
        await redisCache.invalidatePattern(`*:${userId}:*`);
        await redisCache.delete(`history:${userId}`);
      } catch (error) {
        console.error('Cache error:', error);
        // Continue without caching
      }
      
      return NextResponse.json({ 
        success: true, 
        message: `Cleared ${deletedCount} chat messages` 
      });
    } catch (error) {
      console.error('Error clearing chat history:', error);
      return NextResponse.json(
        { error: 'Error clearing chat history', message: error.message },
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
