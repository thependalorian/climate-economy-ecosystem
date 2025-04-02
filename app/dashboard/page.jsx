"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ClimateChat from '../../components/ClimateChat';
import { useAuth } from '../../hooks/useAuth';
import supabase from '../../lib/supabase-client';
import { Frame, CardFrame, ContentFrame } from '../../components/ui/Frame';
import { Button } from '../../components/ui/Button';
import { Heading, Text, SectionTitle } from '../../components/ui/Typography';
import { Badge } from '../../components/ui/badge';
import { FileText, Briefcase, GraduationCap, User, Bell, Calendar, ChevronRight } from 'lucide-react';

/**
 * Dashboard Page
 * Client-side dashboard with user information and latest notifications.
 * This page follows the ACT brand guidelines.
 * Location: /app/dashboard/page.jsx
 */
export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();

  // Redirect to login if no user
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login?redirect=/dashboard');
    }
  }, [user, authLoading, router]);

  // Fetch user data and notifications
  useEffect(() => {
    if (user) {
      fetchUserData();
    }
  }, [user]);

  const fetchUserData = async () => {
    setIsLoading(true);
    try {
      // Fetch user profile
      const { data: profileData } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();

      // Fetch notifications
      const { data: notificationData } = await supabase
        .from('notifications')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(5);

      // Fetch climate news
      const { data: newsData } = await supabase
        .from('climate_news')
        .select('*')
        .order('published_at', { ascending: false })
        .limit(3);

      // Update state
      setProfile(profileData);
      setNotifications(notificationData || []);
      setNews(newsData || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading state
  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-spring-green border-t-transparent"></div>
        <p className="ml-3 text-moss-green font-medium">Loading your dashboard...</p>
      </div>
    );
  }

  // Render dashboard once data is loaded
  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Welcome Banner */}
      <Frame variant="highlight" padding="large" showBrackets={true} className="mb-10 bg-seafoam-blue">
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-16 h-16 bg-spring-green/30 rounded-full flex items-center justify-center">
            <User size={32} className="text-midnight-forest" />
          </div>
          <div>
            <Heading level={2} className="text-midnight-forest">
              Welcome back, {profile?.full_name || user?.email?.split('@')[0] || 'User'}
            </Heading>
            <Text variant="large" className="text-moss-green">
              Your clean energy career dashboard
            </Text>
          </div>
        </div>
      </Frame>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* User profile card */}
        <div className="md:col-span-1 space-y-8">
          <CardFrame variant="primary" padding="default" className="bg-white">
            <CardHeader>
              <Heading level={3} className="text-moss-green">Your Profile</Heading>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div>
                <Text className="text-xs uppercase font-medium text-moss-green/70">Name</Text>
                <Text className="font-medium">{profile?.full_name || user?.email || 'Loading...'}</Text>
              </div>
              
              {profile?.location && (
                <div>
                  <Text className="text-xs uppercase font-medium text-moss-green/70">Location</Text>
                  <Text className="font-medium">{profile.location}</Text>
                </div>
              )}
              
              {profile?.industry && (
                <div>
                  <Text className="text-xs uppercase font-medium text-moss-green/70">Industry</Text>
                  <Text className="font-medium">{profile.industry}</Text>
                </div>
              )}
            </CardContent>
            
            <CardFooter>
              <Button
                variant="primary"
                size="md"
                onClick={() => router.push('/profile')}
                className="w-full"
              >
                Edit Profile
              </Button>
            </CardFooter>
          </CardFrame>
          
          {/* Quick Actions */}
          <ContentFrame title="Quick Actions" variant="default" className="bg-white">
            <div className="space-y-3">
              <ActionCard
                title="Update Resume"
                description="Upload or update your resume for better job matches"
                icon={<FileText size={24} className="text-moss-green" />}
                link="/resume-upload"
              />
              
              <ActionCard
                title="Browse Jobs"
                description="Find clean energy opportunities in Massachusetts"
                icon={<Briefcase size={24} className="text-moss-green" />}
                link="/jobs"
              />
              
              <ActionCard
                title="Schedule Counseling"
                description="Book a session with a career counselor"
                icon={<Calendar size={24} className="text-moss-green" />}
                link="/counselor"
              />
            </div>
          </ContentFrame>
        </div>
        
        {/* Main content area */}
        <div className="md:col-span-2 space-y-8">
          {/* Notifications section */}
          <ContentFrame title="Recent Notifications" variant="default" className="bg-white">
            <div className="flex justify-between items-center mb-4">
              <Link href="/notifications" className="text-sm text-moss-green hover:text-spring-green transition-colors">
                View All Notifications
              </Link>
            </div>
            
            {/* Client-rendered notifications */}
            {notifications.length > 0 ? (
              <div className="space-y-4">
                {notifications.map(notification => (
                  <div 
                    key={notification.id} 
                    className={`p-4 rounded-md border ${notification.read ? 'bg-white border-sand-gray' : 'bg-white border-l-4 border-spring-green'}`}
                  >
                    <div className="flex items-start">
                      <Bell size={20} className={notification.read ? 'text-moss-green/50 mr-3' : 'text-spring-green mr-3'} />
                      <div>
                        <Heading level={4}>{notification.title}</Heading>
                        <Text className="mt-1">{notification.message}</Text>
                        {notification.link && (
                          <Link 
                            href={notification.link}
                            className="text-sm text-moss-green hover:text-spring-green transition-colors mt-2 inline-block"
                          >
                            View Details
                          </Link>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-sand-gray/30 rounded-md p-6 text-center">
                <Bell size={32} className="text-moss-green/50 mx-auto mb-3" />
                <Text className="text-moss-green">No new notifications</Text>
              </div>
            )}
          </ContentFrame>
          
          {/* Climate news section */}
          <ContentFrame title="Climate Economy News" variant="default" className="bg-white">
            {news && news.length > 0 ? (
              <div className="space-y-6">
                {news.map(item => (
                  <div key={item.id} className="border-b border-sand-gray pb-6 last:border-0 last:pb-0">
                    <Heading level={4} className="text-moss-green mb-2">{item.title}</Heading>
                    <Text className="mb-3">{item.summary}</Text>
                    <div className="flex justify-between items-center">
                      <Badge variant="muted" size="sm">
                        {new Date(item.published_at).toLocaleDateString()}
                      </Badge>
                      {item.url && (
                        <a 
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-moss-green hover:text-spring-green transition-colors inline-flex items-center"
                        >
                          Read More
                          <ChevronRight size={16} className="ml-1" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-sand-gray/30 rounded-md p-6 text-center">
                <Text className="text-moss-green">No news available</Text>
              </div>
            )}
          </ContentFrame>
        </div>
      </div>
    </div>
  );
}

function ActionCard({ title, description, icon, link }) {
  const router = useRouter();
  
  return (
    <div 
      className="border border-spring-green/20 rounded-lg p-4 hover:shadow-act transition-shadow cursor-pointer bg-white"
      onClick={() => router.push(link)}
    >
      <div className="flex items-start">
        <div className="p-2 bg-spring-green/10 rounded-full mr-3">
          {icon}
        </div>
        <div className="flex-1">
          <Heading level={4} className="mb-1">{title}</Heading>
          <Text variant="small">{description}</Text>
        </div>
        <ChevronRight size={18} className="text-moss-green self-center" />
      </div>
    </div>
  );
}

function CardHeader({ children, className }) {
  return (
    <div className={`p-5 border-b border-spring-green/10 ${className || ''}`}>
      {children}
    </div>
  );
}

function CardContent({ children, className }) {
  return (
    <div className={`p-5 ${className || ''}`}>
      {children}
    </div>
  );
}

function CardFooter({ children, className }) {
  return (
    <div className={`p-5 border-t border-spring-green/10 bg-sand-gray/10 ${className || ''}`}>
      {children}
    </div>
  );
}

