'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Frame, CardFrame, ContentFrame } from '@/components/ui/Frame';
import { Heading, Text, SectionTitle } from '@/components/ui/Typography';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import MetricsDisplay from '@/components/Admin/MetricsDisplay';
import UserAnalytics from '@/components/Admin/UserAnalytics';
import UsageAnalytics from '@/components/Admin/UsageAnalytics';
import { useAuth } from '@/hooks/useAuth';
import { AlertCircle, User, Clock, MessageSquare, BarChart } from 'lucide-react';

/**
 * Admin Dashboard
 * 
 * Provides system-wide metrics, user analytics, and monitoring capabilities
 * for the Massachusetts Clean Energy Ecosystem.
 * Follows ACT brand guidelines.
 * Location: /app/admin/dashboard/page.jsx
 */
export default function AdminDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('day');
  const [metrics, setMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const { user, isAdmin, isLoading: authLoading } = useAuth();
  const router = useRouter();
  
  // Redirect non-admin users
  useEffect(() => {
    if (!authLoading && (!user || !isAdmin)) {
      router.push('/');
    }
  }, [user, isAdmin, authLoading, router]);
  
  // Load metrics when time range changes
  useEffect(() => {
    if (user && isAdmin) {
      fetchMetrics(timeRange);
      fetchAlerts();
    }
  }, [timeRange, user, isAdmin]);
  
  const fetchMetrics = async (range) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/admin/metrics?timeRange=${range}`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      } else {
        console.error('Failed to fetch metrics');
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/admin/alerts');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };
  
  // If still checking authentication, show loading
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-sand-gray">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-spring-green border-t-transparent"></div>
        <p className="ml-2 text-moss-green">Loading...</p>
      </div>
    );
  }
  
  // If not admin, don't render anything (will redirect)
  if (!isAdmin) {
    return null;
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <SectionTitle>Admin Dashboard</SectionTitle>
        <div className="flex gap-2">
          <Button 
            onClick={() => setTimeRange('day')}
            variant={timeRange === 'day' ? 'primary' : 'secondary'}
            size="sm"
          >
            24 Hours
          </Button>
          <Button 
            onClick={() => setTimeRange('week')}
            variant={timeRange === 'week' ? 'primary' : 'secondary'}
            size="sm"
          >
            7 Days
          </Button>
          <Button 
            onClick={() => setTimeRange('month')}
            variant={timeRange === 'month' ? 'primary' : 'secondary'}
            size="sm"
          >
            30 Days
          </Button>
        </div>
      </div>
      
      {/* Alerts Section */}
      {alerts.length > 0 && (
        <Frame variant="highlight" className="mb-6" padding="default">
          <Heading level={3} className="mb-3">Active Alerts</Heading>
          <div className="grid gap-4">
            {alerts.map((alert, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg flex items-start ${
                  alert.severity === 'high' ? 'bg-red-100 border-l-4 border-red-500' : 'bg-seafoam-blue border-l-4 border-moss-green'
                }`}
              >
                <AlertCircle className="mr-3 text-red-500" />
                <div>
                  <Heading level={4} className="mb-1">
                    {alert.metric} Alert for {alert.endpoint}
                  </Heading>
                  <Text variant="small">
                    Current value: {alert.current_value} (Threshold: {alert.threshold})
                    <br />
                    <span className="text-xs text-moss-green">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </Text>
                </div>
              </div>
            ))}
          </div>
        </Frame>
      )}
      
      {/* Main Dashboard */}
      <Tabs defaultValue="metrics" className="space-y-6">
        <TabsList className="bg-sand-gray p-1 rounded-md">
          <TabsTrigger 
            value="metrics" 
            className="data-[state=active]:bg-spring-green data-[state=active]:text-midnight-forest px-4 py-2 rounded-md"
          >
            <BarChart size={16} className="mr-2" />
            System Metrics
          </TabsTrigger>
          <TabsTrigger 
            value="users" 
            className="data-[state=active]:bg-spring-green data-[state=active]:text-midnight-forest px-4 py-2 rounded-md"
          >
            <User size={16} className="mr-2" />
            User Analytics
          </TabsTrigger>
          <TabsTrigger 
            value="usage" 
            className="data-[state=active]:bg-spring-green data-[state=active]:text-midnight-forest px-4 py-2 rounded-md"
          >
            <Clock size={16} className="mr-2" />
            Usage Analytics
          </TabsTrigger>
          <TabsTrigger 
            value="feedback" 
            className="data-[state=active]:bg-spring-green data-[state=active]:text-midnight-forest px-4 py-2 rounded-md"
          >
            <MessageSquare size={16} className="mr-2" />
            Feedback
          </TabsTrigger>
        </TabsList>
        
        {/* System Metrics Tab */}
        <TabsContent value="metrics">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-spring-green border-t-transparent"></div>
              <p className="ml-2 text-moss-green">Loading metrics...</p>
            </div>
          ) : (
            <MetricsDisplay metrics={metrics} timeRange={timeRange} />
          )}
        </TabsContent>
        
        {/* User Analytics Tab */}
        <TabsContent value="users">
          <UserAnalytics timeRange={timeRange} />
        </TabsContent>
        
        {/* Usage Analytics Tab */}
        <TabsContent value="usage">
          <UsageAnalytics timeRange={timeRange} />
        </TabsContent>
        
        {/* Feedback Tab */}
        <TabsContent value="feedback">
          <ContentFrame title="User Feedback" variant="default">
            {metrics?.feedback ? (
              <div className="space-y-6">
                <div className="grid md:grid-cols-3 gap-4">
                  <CardFrame>
                    <div className="p-4">
                      <Text variant="caption">Average Rating</Text>
                      <Heading level={3}>{metrics.feedback.average_score.toFixed(1)}/5.0</Heading>
                    </div>
                  </CardFrame>
                  <CardFrame>
                    <div className="p-4">
                      <Text variant="caption">Total Responses</Text>
                      <Heading level={3}>{metrics.feedback.total_ratings}</Heading>
                    </div>
                  </CardFrame>
                  <CardFrame>
                    <div className="p-4">
                      <Text variant="caption">Response Rate</Text>
                      <Heading level={3}>
                        {metrics.feedback.response_rate ? `${(metrics.feedback.response_rate * 100).toFixed(1)}%` : 'N/A'}
                      </Heading>
                    </div>
                  </CardFrame>
                </div>
                
                {/* Recent Feedback */}
                <div>
                  <Heading level={3} className="mb-2">Recent Feedback</Heading>
                  {metrics.feedback.recent_items?.length > 0 ? (
                    <div className="space-y-3">
                      {metrics.feedback.recent_items.map((item, i) => (
                        <div key={i} className="border border-spring-green/20 p-4 rounded-md">
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center">
                              <Badge variant={item.score >= 4 ? 'primary' : item.score >= 3 ? 'secondary' : 'outline'}>
                                {item.score}/5
                              </Badge>
                            </div>
                            <Text variant="small" className="text-moss-green">
                              {new Date(item.timestamp).toLocaleString()}
                            </Text>
                          </div>
                          <Text>{item.feedback || 'No comments provided'}</Text>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <Text>No feedback available for the selected period</Text>
                  )}
                </div>
              </div>
            ) : (
              <Text>No feedback data available</Text>
            )}
          </ContentFrame>
        </TabsContent>
      </Tabs>
    </div>
  );
}
