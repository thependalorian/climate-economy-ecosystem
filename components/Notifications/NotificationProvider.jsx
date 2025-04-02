'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useToast } from '../ui/use-toast';
import io from 'socket.io-client';

/**
 * Notification Context
 * 
 * Provides global state and functions for managing notifications
 * with real-time updates using Socket.IO
 */
export const NotificationContext = createContext({
  notifications: [],
  unreadCount: 0,
  pushEnabled: false,
  isLoading: false,
  fetchNotifications: () => {},
  markAsRead: () => {},
  markAllAsRead: () => {},
  deleteNotification: () => {},
  deleteReadNotifications: () => {},
  enablePushNotifications: () => {},
  disablePushNotifications: () => {},
});

/**
 * NotificationProvider Component
 * 
 * Wraps the application with notification context and handles
 * real-time updates and push notification registration.
 */
export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [pushEnabled, setPushEnabled] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const { data: session } = useSession();
  const { toast } = useToast();
  
  // Initialize Socket.IO connection when session is available
  useEffect(() => {
    if (session?.user?.id) {
      // Connect to Socket.IO server
      const socketInstance = io({
        path: '/api/socketio',
        query: { userId: session.user.id }
      });
      
      setSocket(socketInstance);
      
      // Check if push notifications are already enabled
      checkPushEnabled();
      
      // Cleanup on unmount
      return () => {
        socketInstance.disconnect();
      };
    }
  }, [session]);
  
  // Listen for real-time notification events
  useEffect(() => {
    if (!socket) return;
    
    // New notification received
    socket.on('notification', (notification) => {
      // Add to notifications list
      setNotifications(prev => [notification, ...prev]);
      
      // Increment unread count
      setUnreadCount(prev => prev + 1);
      
      // Show toast for new notification
      toast({
        title: notification.title,
        description: notification.message,
        type: notification.type === 'error' ? 'error' : 'default',
      });
    });
    
    // Listen for bulk notification updates (e.g., when there are many new notifications)
    socket.on('notifications:update', (data) => {
      if (data.unreadCount !== undefined) {
        setUnreadCount(data.unreadCount);
      }
      
      // Fetch latest notifications when notified of updates
      fetchNotifications();
    });
    
    return () => {
      socket.off('notification');
      socket.off('notifications:update');
    };
  }, [socket]);
  
  // Fetch notifications
  const fetchNotifications = async (limit = 20, offset = 0, includeRead = true) => {
    if (!session?.user) return;
    
    setIsLoading(true);
    
    try {
      const response = await fetch(
        `/api/notifications?limit=${limit}&offset=${offset}&includeRead=${includeRead}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch notifications');
      }
      
      const data = await response.json();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unreadCount || 0);
      
      return data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to load notifications'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Mark a notification as read
  const markAsRead = async (id) => {
    try {
      const response = await fetch('/api/notifications', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notification_ids: [id]
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to mark notification as read');
      }
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === id ? { ...notif, read: true } : notif
        )
      );
      
      // Update unread count
      setUnreadCount(prev => Math.max(0, prev - 1));
      
      return true;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to update notification'
      });
      return false;
    }
  };
  
  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      const response = await fetch('/api/notifications', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mark_all_read: true
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to mark all notifications as read');
      }
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, read: true }))
      );
      
      // Update unread count
      setUnreadCount(0);
      
      return true;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to update notifications'
      });
      return false;
    }
  };
  
  // Delete a notification
  const deleteNotification = async (id) => {
    try {
      const response = await fetch('/api/notifications', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notification_ids: [id]
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete notification');
      }
      
      // Update local state
      const deletedNotification = notifications.find(n => n.id === id);
      setNotifications(prev => prev.filter(notif => notif.id !== id));
      
      // Update unread count if the deleted notification was unread
      if (deletedNotification && !deletedNotification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      
      return true;
    } catch (error) {
      console.error('Error deleting notification:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to delete notification'
      });
      return false;
    }
  };
  
  // Delete all read notifications
  const deleteReadNotifications = async () => {
    try {
      const response = await fetch('/api/notifications', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          delete_all_read: true
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete read notifications');
      }
      
      // Update local state - keep only unread notifications
      setNotifications(prev => prev.filter(notif => !notif.read));
      
      return true;
    } catch (error) {
      console.error('Error deleting read notifications:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to delete notifications'
      });
      return false;
    }
  };
  
  // Check if push notifications are enabled
  const checkPushEnabled = async () => {
    try {
      // Check if service workers are supported
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.log('Push notifications not supported');
        setPushEnabled(false);
        return false;
      }
      
      // Check if there's an existing subscription
      const registration = await navigator.serviceWorker.ready;
      const existingSubscription = await registration.pushManager.getSubscription();
      
      if (existingSubscription) {
        setSubscription(existingSubscription);
        setPushEnabled(true);
        return true;
      }
      
      setPushEnabled(false);
      return false;
    } catch (error) {
      console.error('Error checking push notification status:', error);
      setPushEnabled(false);
      return false;
    }
  };
  
  // Enable push notifications
  const enablePushNotifications = async () => {
    try {
      // Check if service workers and push are supported
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        toast.error({
          title: 'Not Supported',
          description: 'Push notifications are not supported in your browser'
        });
        return false;
      }
      
      // Register service worker if needed
      let registration;
      try {
        // Check if we already have a service worker
        registration = await navigator.serviceWorker.ready;
      } catch (e) {
        // Register the service worker if not already registered
        registration = await navigator.serviceWorker.register('/service-worker.js');
        await navigator.serviceWorker.ready;
      }
      
      // Get permission for push notifications
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        toast.error({
          title: 'Permission Denied',
          description: 'You need to allow notifications to receive updates'
        });
        return false;
      }
      
      // Get the server's public key for VAPID
      const response = await fetch('/api/notifications/vapid-public-key');
      if (!response.ok) {
        throw new Error('Could not get VAPID public key');
      }
      
      const { publicKey } = await response.json();
      
      // Subscribe to push notifications
      const subscriptionOptions = {
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey)
      };
      
      const pushSubscription = await registration.pushManager.subscribe(subscriptionOptions);
      setSubscription(pushSubscription);
      
      // Send the subscription to our server
      const saveResponse = await fetch('/api/notifications/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          subscription: pushSubscription,
          user_id: session.user.id
        })
      });
      
      if (!saveResponse.ok) {
        throw new Error('Failed to save subscription on server');
      }
      
      setPushEnabled(true);
      
      toast.success({
        title: 'Success',
        description: 'Push notifications have been enabled',
      });
      
      return true;
    } catch (error) {
      console.error('Error enabling push notifications:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to enable push notifications'
      });
      return false;
    }
  };
  
  // Disable push notifications
  const disablePushNotifications = async () => {
    try {
      if (subscription) {
        // Unsubscribe from push services
        await subscription.unsubscribe();
        
        // Notify server to remove subscription
        await fetch('/api/notifications/unregister', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: session.user.id
          })
        });
        
        setSubscription(null);
        setPushEnabled(false);
        
        toast.success({
          title: 'Success',
          description: 'Push notifications have been disabled',
        });
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error disabling push notifications:', error);
      toast.error({
        title: 'Error',
        description: 'Failed to disable push notifications'
      });
      return false;
    }
  };
  
  // Helper function to convert the base64 public key to a UInt8Array
  const urlBase64ToUint8Array = (base64String) => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  };
  
  // Context value
  const contextValue = {
    notifications,
    unreadCount,
    pushEnabled,
    isLoading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    deleteReadNotifications,
    enablePushNotifications,
    disablePushNotifications
  };
  
  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
}

/**
 * Hook for using the notification context
 */
export const useNotifications = () => useContext(NotificationContext); 