'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

/**
 * UserAnalytics Component
 * Displays user-related analytics and metrics in the admin dashboard
 * Location: /components/Admin/UserAnalytics.jsx
 */

const UserAnalytics = ({ timeRange }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      try {
        // In a real app, this would fetch data from an API
        // For now, we'll simulate it with mock data
        const mockData = generateMockData(timeRange);
        setAnalyticsData(mockData);
      } catch (error) {
        console.error('Error fetching user analytics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  // Generate mock data for demonstration
  const generateMockData = (range) => {
    // Generate different data based on time range
    const days = range === 'day' ? 1 : range === 'week' ? 7 : 30;
    const signups = [];
    const engagement = [];
    const retention = [];
    const userTypes = {
      'Veterans': Math.floor(Math.random() * 20) + 10,
      'International Professionals': Math.floor(Math.random() * 25) + 15,
      'Students': Math.floor(Math.random() * 30) + 20,
      'Career Changers': Math.floor(Math.random() * 15) + 10,
      'EJ Community Residents': Math.floor(Math.random() * 10) + 5
    };

    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (days - i - 1));
      
      signups.push({
        date: date.toISOString().split('T')[0],
        value: Math.floor(Math.random() * 20) + 5
      });
      
      engagement.push({
        date: date.toISOString().split('T')[0],
        sessions: Math.floor(Math.random() * 50) + 30,
        actions: Math.floor(Math.random() * 150) + 50
      });
      
      retention.push({
        date: date.toISOString().split('T')[0],
        value: Math.random() * 0.2 + 0.7 // 70-90% retention
      });
    }

    return {
      signups,
      engagement,
      retention,
      userTypes
    };
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-spring-green border-t-transparent"></div>
          <p className="mt-2 text-moss-green">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="text-center py-8">
        <p className="text-midnight-forest">No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      {/* New Users */}
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-xl tracking-tightest leading-title text-midnight-forest">User Signups</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analyticsData.signups}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="value" fill="#B2DE26" stroke="#394816" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* User Engagement */}
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-xl tracking-tightest leading-title text-midnight-forest">User Engagement</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData.engagement}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="sessions" stroke="#394816" />
                <Line type="monotone" dataKey="actions" stroke="#B2DE26" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* User Types */}
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-xl tracking-tightest leading-title text-midnight-forest">User Types Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(analyticsData.userTypes).map(([type, count]) => (
              <div key={type} className="bg-seafoam-blue p-4 rounded-lg text-center">
                <h3 className="font-heading text-lg mb-2">{type}</h3>
                <p className="text-3xl font-bold text-moss-green">{count}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserAnalytics; 