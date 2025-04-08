import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Admin Metrics API Endpoint
 * Retrieves system-wide metrics data for the admin dashboard
 * Location: /app/api/admin/metrics/route.js
 */

export async function GET(request) {
  try {
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const timeRange = searchParams.get('timeRange') || '7d';
    
    // Calculate date ranges based on timeRange
    const now = new Date();
    let startDate;
    
    switch (timeRange) {
      case '30d':
        startDate = new Date(now.setDate(now.getDate() - 30));
        break;
      case '90d':
        startDate = new Date(now.setDate(now.getDate() - 90));
        break;
      case '7d':
      default:
        startDate = new Date(now.setDate(now.getDate() - 7));
        break;
    }
    
    const formattedStartDate = startDate.toISOString();
    
    // Run queries in parallel
    const [
      usersData,
      profileEnrichmentData,
      jobSearchData,
      skillsData,
      searchTermsData
    ] = await Promise.all([
      fetchUserMetrics(),
      fetchProfileEnrichmentMetrics(formattedStartDate),
      fetchJobSearchMetrics(formattedStartDate),
      fetchSkillsDistribution(),
      fetchTopSearchTerms(formattedStartDate)
    ]);
    
    // Calculate statistics
    const profileStats = calculateProfileStats(profileEnrichmentData.rawData);
    const searchStats = calculateSearchStats(jobSearchData.rawData);
    
    // Compile response data
    const responseData = {
      overview: {
        totalUsers: usersData.totalUsers,
        enrichedProfiles: usersData.enrichedProfiles,
        recentEnrichments: profileEnrichmentData.totalCount,
        recentSearches: jobSearchData.totalCount
      },
      profileEnrichment: profileEnrichmentData.chartData,
      jobSearch: jobSearchData.chartData,
      skillsDistribution: skillsData,
      topSkills: skillsData.topSkills,
      topSearchTerms: searchTermsData,
      profileStats,
      searchStats
    };
    
    return NextResponse.json(responseData);
  } catch (error) {
    console.error('Error fetching admin metrics:', error);
    return NextResponse.json({ error: 'Failed to fetch metrics data' }, { status: 500 });
  }
}

/**
 * Fetch user metrics data
 */
async function fetchUserMetrics() {
  // Get total users count
  const { count: totalUsers } = await supabase
    .from('profiles')
    .select('*', { count: 'exact', head: true });
  
  // Get count of users with enriched profiles
  const { count: enrichedProfiles } = await supabase
    .from('profiles')
    .select('*', { count: 'exact', head: true })
    .not('enrichment_data', 'is', null);
  
  return { totalUsers, enrichedProfiles };
}

/**
 * Fetch profile enrichment metrics
 */
async function fetchProfileEnrichmentMetrics(startDate) {
  // Get profile enrichment events
  const { data: enrichmentData, error } = await supabase
    .from('metrics')
    .select('*')
    .eq('event_type', 'profile_enrichment')
    .gte('created_at', startDate)
    .order('created_at', { ascending: true });
  
  if (error) throw error;
  
  // Get verification events
  const { data: verificationData, error: verificationError } = await supabase
    .from('metrics')
    .select('*')
    .eq('event_type', 'skill_verification')
    .gte('created_at', startDate)
    .order('created_at', { ascending: true });
  
  if (verificationError) throw verificationError;
  
  // Process data for charts
  const dates = getDatesInRange(startDate);
  const enrichmentCounts = getCountsByDate(enrichmentData, dates);
  const verificationCounts = getCountsByDate(verificationData, dates);
  
  return {
    chartData: {
      dates: dates.map(date => formatDate(date)),
      counts: enrichmentCounts,
      verificationCounts: verificationCounts
    },
    totalCount: enrichmentData.length,
    rawData: {
      enrichment: enrichmentData,
      verification: verificationData
    }
  };
}

/**
 * Fetch job search metrics
 */
async function fetchJobSearchMetrics(startDate) {
  // Get job search events
  const { data: searchData, error } = await supabase
    .from('metrics')
    .select('*')
    .eq('event_type', 'enhanced_job_search')
    .gte('created_at', startDate)
    .order('created_at', { ascending: true });
  
  if (error) throw error;
  
  // Get recommendation events (search events with is_recommendation = true)
  const recommendations = searchData.filter(item => 
    item.search_data && item.search_data.isRecommendation === true
  );
  
  // Process data for charts
  const dates = getDatesInRange(startDate);
  const searchCounts = getCountsByDate(searchData, dates);
  const recommendationCounts = getCountsByDate(recommendations, dates);
  
  return {
    chartData: {
      dates: dates.map(date => formatDate(date)),
      searchCounts,
      recommendationCounts
    },
    totalCount: searchData.length,
    rawData: searchData
  };
}

/**
 * Fetch skills distribution
 */
async function fetchSkillsDistribution() {
  // Get skills from profile enrichment metrics
  const { data, error } = await supabase
    .from('metrics')
    .select('*')
    .eq('event_type', 'profile_enrichment')
    .order('created_at', { ascending: false });
  
  if (error) throw error;
  
  // Count skills by category
  let technical = 0;
  let transferable = 0;
  let soft = 0;
  
  // Track individual skills
  const skillsCount = {};
  
  data.forEach(item => {
    if (item.enrichment_data && item.enrichment_data.skills) {
      const skills = item.enrichment_data.skills;
      
      // Count by category
      if (skills.technical) {
        technical += Object.keys(skills.technical).length;
        
        // Count individual skills
        Object.keys(skills.technical).forEach(skill => {
          skillsCount[skill] = (skillsCount[skill] || 0) + 1;
          skillsCount[`${skill}_category`] = 'technical';
        });
      }
      
      if (skills.transferable) {
        transferable += Object.keys(skills.transferable).length;
        
        // Count individual skills
        Object.keys(skills.transferable).forEach(skill => {
          skillsCount[skill] = (skillsCount[skill] || 0) + 1;
          skillsCount[`${skill}_category`] = 'transferable';
        });
      }
      
      if (skills.soft) {
        soft += Object.keys(skills.soft).length;
        
        // Count individual skills
        Object.keys(skills.soft).forEach(skill => {
          skillsCount[skill] = (skillsCount[skill] || 0) + 1;
          skillsCount[`${skill}_category`] = 'soft';
        });
      }
    }
  });
  
  // Get top skills
  const topSkills = Object.keys(skillsCount)
    .filter(key => !key.endsWith('_category'))
    .map(skill => ({
      name: skill,
      count: skillsCount[skill],
      category: skillsCount[`${skill}_category`]
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
  
  return {
    technical,
    transferable,
    soft,
    topSkills
  };
}

/**
 * Fetch top search terms
 */
async function fetchTopSearchTerms(startDate) {
  // Get job search events
  const { data, error } = await supabase
    .from('metrics')
    .select('*')
    .eq('event_type', 'enhanced_job_search')
    .gte('created_at', startDate);
  
  if (error) throw error;
  
  // Count search terms
  const termCounts = {};
  
  data.forEach(item => {
    if (item.search_data && item.search_data.query) {
      const query = item.search_data.query.trim().toLowerCase();
      if (query && query.length > 0) {
        termCounts[query] = (termCounts[query] || 0) + 1;
      }
    }
  });
  
  // Get top terms
  const topTerms = Object.keys(termCounts)
    .map(term => ({
      term,
      count: termCounts[term]
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
  
  return topTerms;
}

/**
 * Calculate profile statistics
 */
function calculateProfileStats(data) {
  if (!data || !data.enrichment || !data.verification) {
    return {
      avgSkillsPerProfile: 0,
      verificationRate: 0,
      modificationRate: 0
    };
  }
  
  const { enrichment, verification } = data;
  
  // Calculate average skills per profile
  let totalSkills = 0;
  let profilesWithSkills = 0;
  
  enrichment.forEach(item => {
    if (item.enrichment_data && item.enrichment_data.skills) {
      const skills = item.enrichment_data.skills;
      let skillCount = 0;
      
      if (skills.technical) skillCount += Object.keys(skills.technical).length;
      if (skills.transferable) skillCount += Object.keys(skills.transferable).length;
      if (skills.soft) skillCount += Object.keys(skills.soft).length;
      
      if (skillCount > 0) {
        totalSkills += skillCount;
        profilesWithSkills++;
      }
    }
  });
  
  const avgSkillsPerProfile = profilesWithSkills > 0 ? totalSkills / profilesWithSkills : 0;
  
  // Calculate verification rate
  const verificationRate = enrichment.length > 0 ? (verification.length / enrichment.length) * 100 : 0;
  
  // Calculate modification rate
  let totalModified = 0;
  
  verification.forEach(item => {
    if (item.verification_data) {
      const { added_count = 0, removed_count = 0 } = item.verification_data;
      if (added_count > 0 || removed_count > 0) {
        totalModified++;
      }
    }
  });
  
  const modificationRate = verification.length > 0 ? (totalModified / verification.length) * 100 : 0;
  
  return {
    avgSkillsPerProfile,
    verificationRate,
    modificationRate
  };
}

/**
 * Calculate search statistics
 */
function calculateSearchStats(data) {
  if (!data || data.length === 0) {
    return {
      avgResultsPerSearch: 0,
      profileDataUsageRate: 0,
      recommendationClickRate: 0
    };
  }
  
  // Calculate average results per search
  let totalResults = 0;
  
  data.forEach(item => {
    if (item.search_data && item.search_data.results) {
      totalResults += item.search_data.results;
    }
  });
  
  const avgResultsPerSearch = data.length > 0 ? totalResults / data.length : 0;
  
  // Calculate profile data usage rate
  const searchesUsingProfileData = data.filter(item => 
    item.search_data && item.search_data.usedProfileData === true
  ).length;
  
  const profileDataUsageRate = data.length > 0 ? (searchesUsingProfileData / data.length) * 100 : 0;
  
  // Calculate recommendation click rate
  const recommendations = data.filter(item => 
    item.search_data && item.search_data.isRecommendation === true
  ).length;
  
  const totalRecommendationsShown = data.filter(item => 
    item.search_data && item.search_data.recommendationsShown && item.search_data.recommendationsShown > 0
  ).reduce((total, item) => total + item.search_data.recommendationsShown, 0);
  
  const recommendationClickRate = totalRecommendationsShown > 0 ? 
    (recommendations / totalRecommendationsShown) * 100 : 0;
  
  return {
    avgResultsPerSearch,
    profileDataUsageRate,
    recommendationClickRate
  };
}

/**
 * Helper function to get dates in range
 */
function getDatesInRange(startDateString) {
  const dates = [];
  const startDate = new Date(startDateString);
  const endDate = new Date();
  
  let currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

/**
 * Helper function to get counts by date
 */
function getCountsByDate(data, dates) {
  const counts = new Array(dates.length).fill(0);
  
  data.forEach(item => {
    const itemDate = new Date(item.created_at);
    
    for (let i = 0; i < dates.length; i++) {
      if (
        itemDate.getDate() === dates[i].getDate() &&
        itemDate.getMonth() === dates[i].getMonth() &&
        itemDate.getFullYear() === dates[i].getFullYear()
      ) {
        counts[i]++;
        break;
      }
    }
  });
  
  return counts;
}

/**
 * Helper function to format date as MM/DD
 */
function formatDate(date) {
  return `${date.getMonth() + 1}/${date.getDate()}`;
} 