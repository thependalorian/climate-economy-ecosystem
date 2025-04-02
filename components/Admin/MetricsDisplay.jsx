'use client';

import { Card, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';

/**
 * Metrics Display Component
 * 
 * Visualizes system metrics for the admin dashboard including:
 * - API performance
 * - User engagement
 * - System health
 */
export default function MetricsDisplay({ metrics, timeRange }) {
  if (!metrics) {
    return (
      <div className="text-center py-12">
        <p>No metrics data available</p>
      </div>
    );
  }

  // Generate formatted data for charts
  const formatApiPerformanceData = () => {
    if (!metrics.api_performance) return [];
    
    // Sort by average duration
    return Object.entries(metrics.api_performance.endpoints || {})
      .map(([endpoint, data]) => ({
        name: endpoint.replace('/api/', ''),
        avgDuration: data.avg_duration_ms,
        p95Duration: data.p95_duration_ms,
        errorRate: data.error_rate * 100,
        requests: data.total_requests
      }))
      .sort((a, b) => b.avgDuration - a.avgDuration)
      .slice(0, 8); // Take top 8 slowest endpoints
  };
  
  const formatUserActivityData = () => {
    if (!metrics.user_activity) return [];
    
    return Object.entries(metrics.user_activity.event_type_counts || {})
      .map(([type, count]) => ({
        name: type,
        value: count
      }))
      .sort((a, b) => b.value - a.value);
  };
  
  const formatSatisfactionData = () => {
    if (!metrics.satisfaction) return [];
    
    return Object.entries(metrics.satisfaction.score_distribution || {})
      .map(([score, count]) => ({
        name: `${score} Star${score > 1 ? 's' : ''}`,
        value: count
      }));
  };
  
  // Format time range for display
  const getTimeRangeLabel = () => {
    switch (timeRange) {
      case 'day': return 'Last 24 Hours';
      case 'week': return 'Last 7 Days';
      case 'month': return 'Last 30 Days';
      default: return 'Custom Range';
    }
  };
  
  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
  
  // Data for charts
  const apiPerformanceData = formatApiPerformanceData();
  const userActivityData = formatUserActivityData();
  const satisfactionData = formatSatisfactionData();
  
  return (
    <div className="grid gap-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <CardDescription>Total API Requests</CardDescription>
            <div className="flex justify-between items-center mt-2">
              <CardTitle className="text-3xl">{metrics.api_performance?.total_requests.toLocaleString()}</CardTitle>
              <span className="text-muted-foreground text-sm">{getTimeRangeLabel()}</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <CardDescription>Active Users</CardDescription>
            <div className="flex justify-between items-center mt-2">
              <CardTitle className="text-3xl">{metrics.user_activity?.active_users.toLocaleString()}</CardTitle>
              <span className="text-muted-foreground text-sm">{getTimeRangeLabel()}</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <CardDescription>Average Response Time</CardDescription>
            <div className="flex justify-between items-center mt-2">
              <CardTitle className="text-3xl">{metrics.api_performance?.avg_duration_ms.toFixed(0)} ms</CardTitle>
              <span className={metrics.api_performance?.avg_duration_ms > 300 ? "text-red-500" : "text-green-500"}>
                {metrics.api_performance?.avg_duration_ms > 300 ? "⚠️ Slow" : "✓ Good"}
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <CardDescription>Error Rate</CardDescription>
            <div className="flex justify-between items-center mt-2">
              <CardTitle className="text-3xl">{(metrics.api_performance?.error_rate * 100).toFixed(2)}%</CardTitle>
              <span className={metrics.api_performance?.error_rate > 0.01 ? "text-red-500" : "text-green-500"}>
                {metrics.api_performance?.error_rate > 0.01 ? "⚠️ High" : "✓ Good"}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* API Performance Chart */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between items-center mb-4">
            <CardTitle>API Performance by Endpoint</CardTitle>
            <CardDescription>{getTimeRangeLabel()}</CardDescription>
          </div>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={apiPerformanceData}
                margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45} 
                  textAnchor="end"
                  height={60}
                  interval={0}
                />
                <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                <Tooltip />
                <Bar yAxisId="left" dataKey="avgDuration" name="Avg Duration (ms)" fill="#8884d8" />
                <Bar yAxisId="left" dataKey="p95Duration" name="P95 Duration (ms)" fill="#a4a1e5" />
                <Bar yAxisId="right" dataKey="errorRate" name="Error Rate (%)" fill="#ff8042" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
      
      {/* User Activity Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex justify-between items-center mb-4">
              <CardTitle>User Activity by Event Type</CardTitle>
              <CardDescription>{getTimeRangeLabel()}</CardDescription>
            </div>
            
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={userActivityData}
                    cx="50%"
                    cy="50%"
                    labelLine={true}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {userActivityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        
        {/* User Satisfaction Chart */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex justify-between items-center mb-4">
              <CardTitle>User Satisfaction Ratings</CardTitle>
              <CardDescription>{getTimeRangeLabel()}</CardDescription>
            </div>
            
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={satisfactionData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" name="Count" fill="#8884d8">
                    {satisfactionData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={index === 4 ? '#4CAF50' : index === 3 ? '#8BC34A' : index === 2 ? '#FFC107' : index === 1 ? '#FF9800' : '#F44336'} 
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Status Code Distribution */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex justify-between items-center mb-4">
            <CardTitle>HTTP Status Code Distribution</CardTitle>
            <CardDescription>{getTimeRangeLabel()}</CardDescription>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(metrics.api_performance?.status_code_counts || {}).map(([code, count]) => (
              <div 
                key={code} 
                className={`p-4 rounded-lg ${
                  code.startsWith('2') ? 'bg-green-100' : 
                  code.startsWith('3') ? 'bg-blue-100' : 
                  code.startsWith('4') ? 'bg-yellow-100' : 
                  'bg-red-100'
                }`}
              >
                <p className="text-sm font-medium">Status {code}</p>
                <p className="text-2xl font-bold">{count.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">
                  {(count / metrics.api_performance.total_requests * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 