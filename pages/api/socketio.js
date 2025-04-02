import { Server } from 'socket.io';
import { createAdapter } from '@socket.io/redis-adapter';
import Redis from 'ioredis';
import { getSession } from 'next-auth/react';
import { metrics_service } from '@/lib/monitoring/metrics_service';

/**
 * Socket.IO Server
 * 
 * Provides real-time communication capabilities for notifications
 * and other real-time features. Uses Redis for multi-instance support.
 */

// Create Redis clients for Socket.IO adapter
const pubClient = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  username: process.env.REDIS_USERNAME,
  password: process.env.REDIS_PASSWORD,
  tls: {}
});

const subClient = pubClient.duplicate();

// Store connected users
const connectedUsers = new Map();

// Socket.IO server instance
let io;

export default async function handler(req, res) {
  // Check if Socket.IO server is already initialized
  if (!res.socket.server.io) {
    console.log('Initializing Socket.IO server...');
    
    // Create new Socket.IO server
    io = new Server(res.socket.server, {
      path: '/api/socketio',
      addTrailingSlash: false,
      cors: {
        origin: process.env.NEXTAUTH_URL,
        methods: ['GET', 'POST'],
        credentials: true
      }
    });
    
    // Set up Redis adapter
    io.adapter(createAdapter(pubClient, subClient));
    
    // Handle connection
    io.on('connection', async (socket) => {
      const userId = socket.handshake.query.userId;
      
      // Track connection in metrics
      metrics_service.track_event(
        'socket_connection',
        userId,
        {
          socketId: socket.id,
          userAgent: socket.handshake.headers['user-agent']
        }
      );
      
      console.log(`Socket connected: ${socket.id} for user: ${userId}`);
      
      // Add user to connected users map
      if (userId) {
        // Store multiple sockets for the same user (multiple tabs/devices)
        if (!connectedUsers.has(userId)) {
          connectedUsers.set(userId, new Set());
        }
        connectedUsers.get(userId).add(socket.id);
        
        // Join user-specific room for targeted messages
        socket.join(`user:${userId}`);
      }
      
      // Handle disconnect
      socket.on('disconnect', () => {
        console.log(`Socket disconnected: ${socket.id}`);
        
        // Remove from connected users map
        if (userId && connectedUsers.has(userId)) {
          connectedUsers.get(userId).delete(socket.id);
          
          // Clean up if no more connections for this user
          if (connectedUsers.get(userId).size === 0) {
            connectedUsers.delete(userId);
          }
        }
        
        // Track disconnection in metrics
        metrics_service.track_event(
          'socket_disconnection',
          userId,
          { socketId: socket.id }
        );
      });
    });
    
    // Store io instance on the server object
    res.socket.server.io = io;
  } else {
    // Reuse existing Socket.IO server
    io = res.socket.server.io;
  }
  
  // Return success response
  res.status(200).json({ success: true });
}

/**
 * Send a notification to a specific user
 */
export const sendNotificationToUser = async (userId, notification) => {
  if (!io) {
    console.error('Socket.IO server not initialized');
    return false;
  }
  
  // Emit to user-specific room
  io.to(`user:${userId}`).emit('notification', notification);
  
  // Track notification send event
  metrics_service.track_event(
    'notification_sent',
    userId,
    {
      notification_id: notification.id,
      notification_type: notification.type,
      delivery_method: 'socket'
    }
  );
  
  return true;
};

/**
 * Send a bulk update notification to a user
 * Used when there are many new notifications or for silent updates
 */
export const sendBulkUpdateToUser = async (userId, data) => {
  if (!io) {
    console.error('Socket.IO server not initialized');
    return false;
  }
  
  // Emit to user-specific room
  io.to(`user:${userId}`).emit('notifications:update', data);
  
  return true;
};

/**
 * Check if a user is currently connected
 */
export const isUserConnected = (userId) => {
  return connectedUsers.has(userId) && connectedUsers.get(userId).size > 0;
};

/**
 * Get the count of currently connected users
 */
export const getConnectedUsersCount = () => {
  return connectedUsers.size;
};

/**
 * Send a broadcast notification to all connected users
 */
export const broadcastNotification = async (notification) => {
  if (!io) {
    console.error('Socket.IO server not initialized');
    return false;
  }
  
  io.emit('system:notification', notification);
  
  // Track broadcast event
  metrics_service.track_event(
    'notification_broadcast',
    'system',
    {
      notification_id: notification.id,
      notification_type: notification.type,
      recipients_count: getConnectedUsersCount()
    }
  );
  
  return true;
}; 