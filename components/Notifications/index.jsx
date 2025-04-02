'use client';

import { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { 
  Bell, 
  BellOff, 
  Check, 
  Trash2, 
  ChevronDown, 
  X, 
  Info, 
  AlertCircle, 
  CheckCircle2,
  Briefcase,
  GraduationCap
} from 'lucide-react';
import { 
  Popover, 
  PopoverContent, 
  PopoverTrigger 
} from '@/components/ui/popover';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';
import Link from 'next/link';

/**
 * Notifications Component
 * 
 * Displays user notifications with real-time updates.
 * Provides functionality to mark as read and delete notifications.
 */
export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const { data: session } = useSession();
  const { toast } = useToast();
  const popoverRef = useRef(null);
  
  // Fetch notifications on mount and session change
  useEffect(() => {
    if (session?.user) {
      fetchNotifications();
    }
  }, [session]);
  
  // Setup polling for new notifications every 30 seconds
  useEffect(() => {
    if (!session?.user) return;
    
    const interval = setInterval(() => {
      if (!isOpen) { // Only poll for new notifications when the popover is closed
        fetchUnreadCount();
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, [session, isOpen]);
  
  // Fetch all notifications
  const fetchNotifications = async () => {
    if (!session?.user) return;
    
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/notifications');
      
      if (!response.ok) {
        throw new Error('Failed to fetch notifications');
      }
      
      const data = await response.json();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unreadCount || 0);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      toast({
        title: 'Error',
        description: 'Failed to load notifications',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fetch only unread count (lightweight)
  const fetchUnreadCount = async () => {
    if (!session?.user) return;
    
    try {
      const response = await fetch('/api/notifications?limit=0');
      
      if (!response.ok) {
        throw new Error('Failed to fetch notification count');
      }
      
      const data = await response.json();
      setUnreadCount(data.unreadCount || 0);
    } catch (error) {
      console.error('Error fetching notification count:', error);
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
    } catch (error) {
      console.error('Error marking notification as read:', error);
      toast({
        title: 'Error',
        description: 'Failed to update notification',
        variant: 'destructive'
      });
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
      
      toast({
        title: 'Success',
        description: 'All notifications marked as read',
        variant: 'default'
      });
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      toast({
        title: 'Error',
        description: 'Failed to update notifications',
        variant: 'destructive'
      });
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
    } catch (error) {
      console.error('Error deleting notification:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete notification',
        variant: 'destructive'
      });
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
      
      toast({
        title: 'Success',
        description: 'All read notifications deleted',
        variant: 'default'
      });
    } catch (error) {
      console.error('Error deleting read notifications:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete notifications',
        variant: 'destructive'
      });
    }
  };
  
  // Handle popover open/close
  const handleOpenChange = (open) => {
    setIsOpen(open);
    
    // Fetch latest notifications when opening
    if (open) {
      fetchNotifications();
    }
  };
  
  // Get the notification icon based on type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={16} className="text-success" />;
      case 'warning':
        return <AlertCircle size={16} className="text-warning" />;
      case 'error':
        return <AlertCircle size={16} className="text-destructive" />;
      case 'job':
        return <Briefcase size={16} className="text-primary" />;
      case 'training':
        return <GraduationCap size={16} className="text-secondary" />;
      case 'info':
      default:
        return <Info size={16} className="text-muted-foreground" />;
    }
  };
  
  // Format the relative time (e.g., "2 hours ago")
  const formatRelativeTime = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) {
      return 'just now';
    }
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
      return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    }
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    }
    
    const days = Math.floor(hours / 24);
    if (days < 7) {
      return `${days} day${days === 1 ? '' : 's'} ago`;
    }
    
    // For older notifications, show the actual date
    return date.toLocaleDateString();
  };
  
  return (
    <Popover open={isOpen} onOpenChange={handleOpenChange} align="end">
      <PopoverTrigger>
        <Button 
          variant="tertiary" 
          size="sm" 
          className="relative hover:bg-seafoam-blue"
          aria-label="Notifications"
        >
          {unreadCount > 0 ? (
            <>
              <Bell size={20} />
              <Badge 
                className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs"
                variant="primary"
              >
                {unreadCount > 9 ? '9+' : unreadCount}
              </Badge>
            </>
          ) : (
            <BellOff size={20} className="text-moss-green" />
          )}
        </Button>
      </PopoverTrigger>
      
      <PopoverContent 
        className="w-80 md:w-96 max-h-[80vh] flex flex-col p-0" 
      >
        <div className="flex items-center justify-between p-4 border-b border-sand-gray bg-seafoam-blue">
          <h3 className="font-heading text-midnight-forest">Notifications</h3>
          <div className="flex gap-1">
            {notifications.some(n => !n.read) && (
              <Button 
                variant="tertiary" 
                size="xs" 
                onClick={markAllAsRead}
                aria-label="Mark all as read"
              >
                <Check size={16} className="mr-1" />
                <span className="text-xs">Mark all read</span>
              </Button>
            )}
            {notifications.some(n => n.read) && (
              <Button 
                variant="tertiary" 
                size="xs" 
                onClick={deleteReadNotifications}
                aria-label="Delete read notifications"
              >
                <Trash2 size={16} className="mr-1" />
                <span className="text-xs">Clear read</span>
              </Button>
            )}
          </div>
        </div>
        
        <div className="overflow-y-auto flex-grow divide-y divide-sand-gray">
          {isLoading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin h-6 w-6 border-2 border-spring-green border-t-transparent rounded-full"></div>
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-moss-green">
              <BellOff size={24} className="mx-auto mb-2" />
              <p>No notifications</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <div 
                key={notification.id} 
                className={cn(
                  "p-3 hover:bg-seafoam-blue/40 relative",
                  !notification.read && "bg-spring-green/10"
                )}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {getNotificationIcon(notification.type)}
                  </div>
                  
                  <div className="flex-grow pr-8">
                    <div className="flex justify-between items-baseline">
                      <h4 className="font-heading text-midnight-forest text-sm tracking-tightest">
                        {notification.title}
                      </h4>
                      <span className="text-xs text-moss-green">
                        {formatRelativeTime(notification.created_at)}
                      </span>
                    </div>
                    
                    <p className="text-sm mt-1 text-midnight-forest font-inter leading-body">
                      {notification.message}
                    </p>
                    
                    {notification.link && (
                      <div className="mt-2">
                        <Link href={notification.link} passHref>
                          <Button 
                            variant="tertiary" 
                            size="xs" 
                            className="h-auto p-0 text-xs"
                            onClick={() => {
                              if (!notification.read) {
                                markAsRead(notification.id);
                              }
                            }}
                          >
                            View details
                          </Button>
                        </Link>
                      </div>
                    )}
                  </div>
                  
                  <div className="absolute top-1 right-1 flex gap-1">
                    {!notification.read && (
                      <Button
                        size="xs"
                        variant="tertiary"
                        className="h-6 w-6 p-1 text-moss-green hover:text-spring-green"
                        onClick={() => markAsRead(notification.id)}
                        aria-label="Mark as read"
                      >
                        <Check size={14} />
                      </Button>
                    )}
                    
                    <Button
                      size="xs"
                      variant="tertiary"
                      className="h-6 w-6 p-1 text-moss-green hover:text-red-500"
                      onClick={() => deleteNotification(notification.id)}
                      aria-label="Delete notification"
                    >
                      <X size={14} />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        
        {notifications.length > 0 && (
          <div className="p-2 border-t border-sand-gray text-center bg-seafoam-blue/50">
            <Button
              variant="tertiary"
              size="xs"
              className="text-xs text-moss-green"
              onClick={() => {
                setIsOpen(false);
                // Navigate to notifications page with all history
                // Implement when notifications page is available
              }}
            >
              View all notifications
              <ChevronDown size={14} className="ml-1" />
            </Button>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
} 