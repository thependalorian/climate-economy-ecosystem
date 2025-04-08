import { useState, useEffect } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { 
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Admin Metrics Dashboard Component
 * 
 * Displays metrics for profile enrichment and job search data
 */
const AdminMetricsDashboard = () => {
  const [metricsData, setMetricsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('7d'); // 7d, 30d, 90d
  
  // Fetch metrics data
  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/admin/metrics?timeRange=${timeRange}`);
        if (!response.ok) throw new Error('Failed to fetch metrics');
        
        const data = await response.json();
        setMetricsData(data);
      } catch (err) {
        console.error('Error fetching metrics:', err);
        setError('Failed to load metrics data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMetrics();
  }, [timeRange]);
  
  // Prepare chart data for profile enrichment
  const getProfileEnrichmentChartData = () => {
    if (!metricsData || !metricsData.profileEnrichment) return null;
    
    const data = metricsData.profileEnrichment;
    
    return {
      labels: data.dates,
      datasets: [
        {
          label: 'Enrichment Count',
          data: data.counts,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        },
        {
          label: 'Verification Count',
          data: data.verificationCounts,
          backgroundColor: 'rgba(153, 102, 255, 0.2)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1
        }
      ]
    };
  };
  
  // Prepare chart data for enrichment skills
  const getSkillsDistributionChartData = () => {
    if (!metricsData || !metricsData.skillsDistribution) return null;
    
    const data = metricsData.skillsDistribution;
    
    return {
      labels: ['Technical', 'Transferable', 'Soft'],
      datasets: [
        {
          data: [data.technical, data.transferable, data.soft],
          backgroundColor: [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)'
          ],
          borderWidth: 1
        }
      ]
    };
  };
  
  // Prepare chart data for job search metrics
  const getJobSearchChartData = () => {
    if (!metricsData || !metricsData.jobSearch) return null;
    
    const data = metricsData.jobSearch;
    
    return {
      labels: data.dates,
      datasets: [
        {
          label: 'Searches',
          data: data.searchCounts,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: 'Recommendations',
          data: data.recommendationCounts,
          backgroundColor: 'rgba(255, 159, 64, 0.2)',
          borderColor: 'rgba(255, 159, 64, 1)',
          borderWidth: 1
        }
      ]
    };
  };
  
  // Render loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <div className="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{error}</span>
      </div>
    );
  }
  
  return (
    <div className="bg-base-200 p-6 rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Metrics Dashboard</h2>
        
        <div className="flex gap-2">
          <div className="btn-group">
            <button 
              className={`btn btn-sm ${timeRange === '7d' ? 'btn-active' : ''}`}
              onClick={() => setTimeRange('7d')}
            >
              7 Days
            </button>
            <button 
              className={`btn btn-sm ${timeRange === '30d' ? 'btn-active' : ''}`}
              onClick={() => setTimeRange('30d')}
            >
              30 Days
            </button>
            <button 
              className={`btn btn-sm ${timeRange === '90d' ? 'btn-active' : ''}`}
              onClick={() => setTimeRange('90d')}
            >
              90 Days
            </button>
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="tabs tabs-boxed mb-6">
        <a 
          className={`tab ${activeTab === 'overview' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </a>
        <a 
          className={`tab ${activeTab === 'profile' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profile Enrichment
        </a>
        <a 
          className={`tab ${activeTab === 'jobs' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          Job Search
        </a>
      </div>
      
      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h3 className="card-title">User Metrics</h3>
              <div className="stats shadow">
                <div className="stat">
                  <div className="stat-title">Total Users</div>
                  <div className="stat-value">{metricsData?.overview?.totalUsers || 0}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Enriched Profiles</div>
                  <div className="stat-value">{metricsData?.overview?.enrichedProfiles || 0}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h3 className="card-title">Skill Distribution</h3>
              {metricsData?.skillsDistribution && (
                <div className="h-60">
                  <Pie 
                    data={getSkillsDistributionChartData()} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false
                    }}
                  />
                </div>
              )}
            </div>
          </div>
          
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h3 className="card-title">Recent Activity</h3>
              <div className="stats shadow">
                <div className="stat">
                  <div className="stat-title">Enrichments (Last 7 Days)</div>
                  <div className="stat-value">{metricsData?.overview?.recentEnrichments || 0}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Job Searches (Last 7 Days)</div>
                  <div className="stat-value">{metricsData?.overview?.recentSearches || 0}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Profile Enrichment Tab */}
      {activeTab === 'profile' && (
        <div className="grid grid-cols-1 gap-6">
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h3 className="card-title">Profile Enrichment Trends</h3>
              {metricsData?.profileEnrichment && (
                <div className="h-80">
                  <Line 
                    data={getProfileEnrichmentChartData()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true
                        }
                      }
                    }}
                  />
                </div>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card bg-base-100 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Top Skills Added</h3>
                <div className="overflow-x-auto">
                  <table className="table table-zebra">
                    <thead>
                      <tr>
                        <th>Skill</th>
                        <th>Category</th>
                        <th>Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metricsData?.topSkills?.map((skill, index) => (
                        <tr key={index}>
                          <td>{skill.name}</td>
                          <td>
                            <span className={`badge ${
                              skill.category === 'technical' ? 'badge-primary' : 
                              skill.category === 'transferable' ? 'badge-secondary' : 
                              'badge-accent'
                            }`}>
                              {skill.category}
                            </span>
                          </td>
                          <td>{skill.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            <div className="card bg-base-100 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Enrichment Statistics</h3>
                <div className="stats stats-vertical shadow">
                  <div className="stat">
                    <div className="stat-title">Average Skills per Profile</div>
                    <div className="stat-value">{metricsData?.profileStats?.avgSkillsPerProfile?.toFixed(1) || 0}</div>
                  </div>
                  <div className="stat">
                    <div className="stat-title">Verification Rate</div>
                    <div className="stat-value">{metricsData?.profileStats?.verificationRate?.toFixed(1) || 0}%</div>
                  </div>
                  <div className="stat">
                    <div className="stat-title">Skill Modification Rate</div>
                    <div className="stat-value">{metricsData?.profileStats?.modificationRate?.toFixed(1) || 0}%</div>
                    <div className="stat-desc">Skills added or removed during verification</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Job Search Tab */}
      {activeTab === 'jobs' && (
        <div className="grid grid-cols-1 gap-6">
          <div className="card bg-base-100 shadow-lg">
            <div className="card-body">
              <h3 className="card-title">Job Search Activity</h3>
              {metricsData?.jobSearch && (
                <div className="h-80">
                  <Bar 
                    data={getJobSearchChartData()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true
                        }
                      }
                    }}
                  />
                </div>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card bg-base-100 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Top Search Terms</h3>
                <div className="overflow-x-auto">
                  <table className="table table-zebra">
                    <thead>
                      <tr>
                        <th>Term</th>
                        <th>Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metricsData?.topSearchTerms?.map((term, index) => (
                        <tr key={index}>
                          <td>{term.term}</td>
                          <td>{term.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            <div className="card bg-base-100 shadow-lg">
              <div className="card-body">
                <h3 className="card-title">Search Statistics</h3>
                <div className="stats stats-vertical shadow">
                  <div className="stat">
                    <div className="stat-title">Average Results per Search</div>
                    <div className="stat-value">{metricsData?.searchStats?.avgResultsPerSearch?.toFixed(1) || 0}</div>
                  </div>
                  <div className="stat">
                    <div className="stat-title">Profile Data Usage</div>
                    <div className="stat-value">{metricsData?.searchStats?.profileDataUsageRate?.toFixed(1) || 0}%</div>
                    <div className="stat-desc">Searches using profile data</div>
                  </div>
                  <div className="stat">
                    <div className="stat-title">Recommendation Click Rate</div>
                    <div className="stat-value">{metricsData?.searchStats?.recommendationClickRate?.toFixed(1) || 0}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMetricsDashboard; 