'use client';

import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
import { format, parseISO, subDays } from 'date-fns';

// Register required Chart.js components
Chart.register(...registerables);

/**
 * RLHF Metrics Dashboard
 * 
 * Displays metrics and analytics for Reinforcement Learning from Human Feedback
 */
export default function RLHFMetricsDashboard() {
  const [feedbackData, setFeedbackData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('7d'); // 7d, 30d, 90d
  
  // Load feedback data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`/api/admin/metrics/rlhf?timeRange=${timeRange}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch RLHF metrics');
        }
        
        const data = await response.json();
        setFeedbackData(data);
      } catch (err) {
        console.error('Error fetching RLHF metrics:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [timeRange]);
  
  // For demo purposes, generate mock data if needed
  const getMockData = () => {
    const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
    const dates = Array.from({ length: days }, (_, i) => format(subDays(new Date(), i), 'yyyy-MM-dd'));
    
    return {
      summary: {
        totalFeedback: 412,
        stepFeedback: 267,
        messageFeedback: 145,
        averageScore: 4.2,
        positivePercentage: 78,
        userParticipation: 65
      },
      trends: {
        dailyFeedback: dates.map((date, i) => ({
          date,
          stepFeedback: Math.floor(Math.random() * 20) + 5,
          messageFeedback: Math.floor(Math.random() * 15) + 3
        })),
        dailyScores: dates.map((date, i) => ({
          date,
          averageScore: 3 + Math.random() * 2
        }))
      },
      distribution: {
        scoreDistribution: {
          1: 15,
          2: 32,
          3: 84,
          4: 156,
          5: 125
        },
        feedbackTypes: {
          positive: 312,
          negative: 100
        },
        stepVsMessage: {
          step: 267,
          message: 145
        }
      }
    };
  };
  
  // Use mock data for now
  const data = feedbackData || getMockData();
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error:</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }
  
  // Prepare chart data
  const feedbackTrendData = {
    labels: data.trends.dailyFeedback.map(d => d.date).reverse(),
    datasets: [
      {
        label: 'Step Feedback',
        data: data.trends.dailyFeedback.map(d => d.stepFeedback).reverse(),
        borderColor: '#4D7C0F',
        backgroundColor: 'rgba(77, 124, 15, 0.1)',
        fill: true
      },
      {
        label: 'Message Feedback',
        data: data.trends.dailyFeedback.map(d => d.messageFeedback).reverse(),
        borderColor: '#166534',
        backgroundColor: 'rgba(22, 101, 52, 0.1)',
        fill: true
      }
    ]
  };
  
  const scoreDistributionData = {
    labels: Object.keys(data.distribution.scoreDistribution),
    datasets: [
      {
        label: 'Score Distribution',
        data: Object.values(data.distribution.scoreDistribution),
        backgroundColor: [
          '#FECACA', // 1 - light red
          '#FED7AA', // 2 - light orange
          '#FEF3C7', // 3 - light yellow
          '#DCFCE7', // 4 - light green
          '#BBF7D0'  // 5 - green
        ]
      }
    ]
  };
  
  const feedbackTypeData = {
    labels: ['Positive', 'Negative'],
    datasets: [
      {
        label: 'Feedback Types',
        data: [data.distribution.feedbackTypes.positive, data.distribution.feedbackTypes.negative],
        backgroundColor: ['#BBF7D0', '#FECACA']
      }
    ]
  };
  
  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-midnight-forest">RLHF Metrics Dashboard</h2>
        
        <div className="btn-group">
          <button 
            className={`btn btn-sm ${timeRange === '7d' ? 'btn-active' : ''}`}
            onClick={() => setTimeRange('7d')}
          >
            7d
          </button>
          <button 
            className={`btn btn-sm ${timeRange === '30d' ? 'btn-active' : ''}`}
            onClick={() => setTimeRange('30d')}
          >
            30d
          </button>
          <button 
            className={`btn btn-sm ${timeRange === '90d' ? 'btn-active' : ''}`}
            onClick={() => setTimeRange('90d')}
          >
            90d
          </button>
        </div>
      </div>
      
      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-2">Total Feedback</h3>
          <div className="flex items-end">
            <span className="text-3xl font-bold">{data.summary.totalFeedback}</span>
            <div className="ml-4 text-sm">
              <div className="flex items-center">
                <span className="inline-block w-3 h-3 bg-spring-green rounded-full mr-1"></span>
                <span>Step: {data.summary.stepFeedback}</span>
              </div>
              <div className="flex items-center">
                <span className="inline-block w-3 h-3 bg-moss-green rounded-full mr-1"></span>
                <span>Message: {data.summary.messageFeedback}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-2">Average Score</h3>
          <div className="flex items-end">
            <span className="text-3xl font-bold">{data.summary.averageScore.toFixed(1)}</span>
            <span className="ml-1 mb-1">/5</span>
            <span className="ml-4 text-sm text-green-600">
              {data.summary.positivePercentage}% positive
            </span>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-2">User Participation</h3>
          <div className="flex items-end">
            <span className="text-3xl font-bold">{data.summary.userParticipation}%</span>
            <span className="ml-4 text-sm">
              of users provide feedback
            </span>
          </div>
        </div>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Feedback Trend</h3>
          <div className="h-64">
            <Line 
              data={feedbackTrendData} 
              options={{
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true
                  }
                }
              }}
            />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Score Distribution</h3>
          <div className="h-64">
            <Bar 
              data={scoreDistributionData} 
              options={{
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true
                  }
                }
              }}
            />
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Feedback Types</h3>
          <div className="h-64 flex justify-center">
            <div className="w-1/2 h-full">
              <Doughnut 
                data={feedbackTypeData} 
                options={{
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Top Improvement Areas</h3>
          <ul className="divide-y">
            <li className="py-3">
              <div className="flex justify-between">
                <span>Query understanding</span>
                <span className="font-semibold">24% negative feedback</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                <div className="bg-red-300 h-2.5 rounded-full" style={{ width: '24%' }}></div>
              </div>
            </li>
            <li className="py-3">
              <div className="flex justify-between">
                <span>Job recommendations</span>
                <span className="font-semibold">18% negative feedback</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                <div className="bg-red-300 h-2.5 rounded-full" style={{ width: '18%' }}></div>
              </div>
            </li>
            <li className="py-3">
              <div className="flex justify-between">
                <span>Response formatting</span>
                <span className="font-semibold">12% negative feedback</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                <div className="bg-red-300 h-2.5 rounded-full" style={{ width: '12%' }}></div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
} 