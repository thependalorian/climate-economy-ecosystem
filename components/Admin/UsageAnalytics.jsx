'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

/**
 * UsageAnalytics Component
 * Displays platform usage analytics and metrics in the admin dashboard
 * Location: /components/Admin/UsageAnalytics.jsx
 */

const UsageAnalytics = ({ timeRange }) => {
  const [usageData, setUsageData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUsageData = async () => {
      setIsLoading(true);
      try {
        // In a real app, this would fetch data from an API
        // For now, we'll simulate it with mock data
        const mockData = generateMockData(timeRange);
        setUsageData(mockData);
      } catch (error) {
        console.error('Error fetching usage analytics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsageData();
  }, [timeRange]);

  // Generate mock data for demonstration
  const generateMockData = (range) => {
    // Colors for charts
    const COLORS = ['#B2DE26', '#394816', '#001818', '#E0FFFF', '#EBE9E1'];

    // Features data
    const features = [
      { name: 'Climate Chat', count: Math.floor(Math.random() * 500) + 300 },
      { name: 'Resume Analysis', count: Math.floor(Math.random() * 300) + 200 },
      { name: 'Job Search', count: Math.floor(Math.random() * 400) + 150 },
      { name: 'Training Paths', count: Math.floor(Math.random() * 250) + 100 },
      { name: 'Skill Assessment', count: Math.floor(Math.random() * 200) + 50 }
    ];

    // Locations data with Gateway Cities focus
    const locations = [
      { name: 'Boston', count: Math.floor(Math.random() * 200) + 150 },
      { name: 'Worcester', count: Math.floor(Math.random() * 150) + 80 },
      { name: 'Springfield', count: Math.floor(Math.random() * 120) + 60 },
      { name: 'Lowell', count: Math.floor(Math.random() * 100) + 50 },
      { name: 'Brockton', count: Math.floor(Math.random() * 80) + 40 },
      { name: 'New Bedford', count: Math.floor(Math.random() * 70) + 30 },
      { name: 'Fall River', count: Math.floor(Math.random() * 60) + 25 },
      { name: 'Lawrence', count: Math.floor(Math.random() * 50) + 20 }
    ];

    // Access methods
    const accessMethods = [
      { name: 'Desktop', value: Math.floor(Math.random() * 60) + 40 },
      { name: 'Mobile', value: Math.floor(Math.random() * 40) + 20 },
      { name: 'Tablet', value: Math.floor(Math.random() * 20) + 5 }
    ];

    return {
      features,
      locations,
      accessMethods,
      colors: COLORS
    };
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-spring-green border-t-transparent"></div>
          <p className="mt-2 text-moss-green">Loading usage data...</p>
        </div>
      </div>
    );
  }

  if (!usageData) {
    return (
      <div className="text-center py-8">
        <p className="text-midnight-forest">No usage data available</p>
      </div>
    );
  }

  return (
    <div className="grid gap-6">
      {/* Feature Usage */}
      <Card>
        <CardHeader>
          <CardTitle className="font-heading text-xl tracking-tightest leading-title text-midnight-forest">Feature Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={usageData.features}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#B2DE26" name="Usage Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Location Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="font-heading text-xl tracking-tightest leading-title text-midnight-forest">Gateway Cities Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={usageData.locations}
                  margin={{ top: 5, right: 30, left: 90, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="name" />
                  <Tooltip />
                  <Bar dataKey="count" fill="#394816" name="User Count" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Access Methods */}
        <Card>
          <CardHeader>
            <CardTitle className="font-heading text-xl tracking-tightest leading-title text-midnight-forest">Access Methods</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={usageData.accessMethods}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={80}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    dataKey="value"
                  >
                    {usageData.accessMethods.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={usageData.colors[index % usageData.colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UsageAnalytics; 