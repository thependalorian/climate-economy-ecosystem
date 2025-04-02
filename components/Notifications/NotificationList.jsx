'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  Info, 
  AlertCircle, 
  CheckCircle2,
  Briefcase,
  GraduationCap,
  Clock,
  Check,
  Trash2
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { markNotificationsAsRead } from '@/lib/supabase-client';

/**
 * NotificationList Component
 * 
 * Displays a list of notifications with options to mark as read or delete.
 * This component can be used in both client and server components as it
 * handles client-side interactivity for server-rendered data.
 * 
 * @param {Object} props
 * @param {Array} props.notifications - Array of notification objects
 * @param {Function} props.onUpdate - Callback function when notifications are updated
 * @param {boolean} props.interactive - Whether to show interactive controls (mark as read, etc.)
 */
export default function NotificationList({ 
  notifications = [], 
  onUpdate,
  interactive = true
}) {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  
  // Mark a notification as read
  const handleMarkAsRead = async (id) => {
    setLoading(true);
    
    try {
      const success = await markNotificationsAsRead([id]);
      
      if (success) {
        // Call onUpdate callback if provided
        if (onUpdate) {
          onUpdate();
        }
        
        toast({
          title: 'Notification marked as read',
          variant: 'default'
        });
      } else {
        throw new Error('Failed to mark notification as read');
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
      toast({
        title: 'Error',
        description: 'Failed to mark notification as read',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Mark all notifications as read
  const handleMarkAllAsRead = async () => {
    setLoading(true);
    
    try {
      const success = await markNotificationsAsRead([], true);
      
      if (success) {
        // Call onUpdate callback if provided
        if (onUpdate) {
          onUpdate();
        }
        
        toast({
          title: 'All notifications marked as read',
          variant: 'default'
        });
      } else {
        throw new Error('Failed to mark all notifications as read');
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      toast({
        title: 'Error',
        description: 'Failed to mark all notifications as read',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Get the notification icon based on type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 size={16} className="text-green-500" />;
      case 'warning':
        return <AlertCircle size={16} className="text-amber-500" />;
      case 'error':
        return <AlertCircle size={16} className="text-red-500" />;
      case 'job':
        return <Briefcase size={16} className="text-[#394816]" />;
      case 'training':
        return <GraduationCap size={16} className="text-[#394816]" />;
      case 'info':
      default:
        return <Info size={16} className="text-[#394816]" />;
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
  
  // Render empty state if no notifications
  if (notifications.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>No notifications</p>
      </div>
    );
  }
  
  // Render notifications list
  return (
    <div className="space-y-4">
      {/* Controls for interactive mode */}
      {interactive && notifications.some(n => !n.read) && (
        <div className="flex justify-end mb-2">
          <button
            onClick={handleMarkAllAsRead}
            disabled={loading}
            className="inline-flex items-center text-sm text-[#394816] hover:underline"
          >
            <Check size={14} className="mr-1" />
            Mark all as read
          </button>
        </div>
      )}
      
      {/* Notifications list */}
      <div className="space-y-3">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`p-3 rounded-lg ${
              notification.read 
                ? 'bg-white' 
                : 'bg-white border-l-4 border-[#B2DE26]'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="mt-1">
                {getNotificationIcon(notification.type)}
              </div>
              
              <div className="flex-grow">
                <div className="flex justify-between items-baseline">
                  <h3 className="font-medium text-[#001818]">
                    {notification.title}
                  </h3>
                  <span className="text-xs text-muted-foreground flex items-center">
                    <Clock size={12} className="mr-1" />
                    {formatRelativeTime(notification.created_at)}
                  </span>
                </div>
                
                <p className="text-sm mt-1">
                  {notification.message}
                </p>
                
                {notification.link && (
                  <div className="mt-2">
                    <Link
                      href={notification.link}
                      className="text-xs text-[#394816] hover:underline"
                      onClick={() => {
                        if (!notification.read) {
                          handleMarkAsRead(notification.id);
                        }
                      }}
                    >
                      View details
                    </Link>
                  </div>
                )}
              </div>
              
              {/* Interactive controls */}
              {interactive && !notification.read && (
                <button
                  onClick={() => handleMarkAsRead(notification.id)}
                  disabled={loading}
                  className="text-muted-foreground hover:text-[#394816] transition-colors"
                  title="Mark as read"
                >
                  <Check size={16} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 