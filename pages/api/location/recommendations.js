import { createClient } from '@supabase/supabase-js';
import { exec } from 'child_process';
import util from 'util';
import path from 'path';

// Convert exec to Promise-based
const execPromise = util.promisify(exec);

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * API endpoint for location-based clean energy recommendations
 * 
 * Provides specialized recommendations based on user location,
 * with special handling for Gateway Cities and Environmental Justice communities
 */
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { location, latitude, longitude, sector = null } = req.body;

    if (!location && (!latitude || !longitude)) {
      return res.status(400).json({ message: 'Location or coordinates required' });
    }

    // Analyze the location
    const locationData = await analyzeLocation(location, latitude, longitude, sector);
    
    // Get training and job recommendations
    const recommendations = await getRecommendationsForLocation(locationData, sector);

    return res.status(200).json({
      location: locationData,
      recommendations
    });
  } catch (error) {
    console.error('Error processing location recommendations:', error);
    return res.status(500).json({ message: 'Error processing recommendations', error: error.message });
  }
}

/**
 * Analyze a location to determine its classification and characteristics
 * 
 * @param {string} location - Location name (city/neighborhood)
 * @param {number} latitude - Latitude (optional if location provided)
 * @param {number} longitude - Longitude (optional if location provided)
 * @param {string} sector - Optional clean energy sector
 * @returns {Promise<Object>} Location analysis data
 */
async function analyzeLocation(location, latitude, longitude, sector) {
  // If no coordinates provided, but we have location name, try to geocode
  if ((!latitude || !longitude) && location) {
    const coordinates = await geocodeLocation(location);
    if (coordinates) {
      latitude = coordinates.latitude;
      longitude = coordinates.longitude;
    }
  }

  // Check if the location is an EJ community
  const isEjCommunity = await checkIfEjCommunity(location, latitude, longitude);
  
  // Check if the location is a Gateway City
  const isGatewayCity = await checkIfGatewayCity(location, latitude, longitude);

  let locationData = {
    name: location,
    coordinates: latitude && longitude ? { latitude, longitude } : null,
    is_ej_community: isEjCommunity,
    is_gateway_city: isGatewayCity,
    nearest: {}
  };

  // If it's a Gateway City, get detailed info using the Gateway City Analyzer
  if (isGatewayCity) {
    locationData = {
      ...locationData,
      ...(await getGatewayCityDetails(location, sector))
    };
  }
  
  // If it's an EJ community, get detailed info using the EJ Support Tool
  if (isEjCommunity) {
    locationData = {
      ...locationData,
      ...(await getEjCommunityDetails(location, sector))
    };
  }
  
  // If neither, get nearby Gateway Cities and EJ communities
  if (!isGatewayCity && !isEjCommunity && latitude && longitude) {
    const nearbyGatewayCities = await findNearbyGatewayCities(latitude, longitude);
    const nearbyEjCommunities = await findNearbyEjCommunities(latitude, longitude);
    
    locationData.nearest = {
      gateway_cities: nearbyGatewayCities,
      ej_communities: nearbyEjCommunities
    };
  }

  return locationData;
}

/**
 * Get recommendations for a location
 * 
 * @param {Object} locationData - Location analysis data
 * @param {string} sector - Optional clean energy sector
 * @returns {Promise<Object>} Recommendations
 */
async function getRecommendationsForLocation(locationData, sector) {
  // Initialize recommendations object
  const recommendations = {
    training_programs: [],
    job_opportunities: [],
    support_programs: [],
    insights: []
  };
  
  const { is_ej_community, is_gateway_city, coordinates, name } = locationData;
  
  // Get training programs
  recommendations.training_programs = await getTrainingProgramsForLocation(
    name, 
    coordinates, 
    sector, 
    is_ej_community
  );
  
  // Get job opportunities
  recommendations.job_opportunities = await getJobOpportunitiesForLocation(
    name, 
    coordinates, 
    sector, 
    is_ej_community, 
    is_gateway_city
  );
  
  // If EJ community, add support programs
  if (is_ej_community) {
    recommendations.support_programs = await getSupportProgramsForEj(name, sector);
  }
  
  // Generate insights based on location characteristics
  recommendations.insights = await generateLocationInsights(locationData, sector);
  
  return recommendations;
}

/**
 * Check if a location is an Environmental Justice community
 * 
 * @param {string} location - Location name
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @returns {Promise<boolean>} True if EJ community
 */
async function checkIfEjCommunity(location, latitude, longitude) {
  try {
    // Try looking up by name first
    if (location) {
      const { data, error } = await supabase
        .from('ej_communities')
        .select('id')
        .or(`name.eq.${location},name.ilike.%${location}%`)
        .limit(1);
        
      if (!error && data && data.length > 0) {
        return true;
      }
    }
    
    // If we have coordinates, check spatial match
    if (latitude && longitude) {
      const { data, error } = await supabase
        .rpc('is_in_ej_community', { lat: latitude, lng: longitude });
        
      if (!error && data) {
        return data;
      }
    }
    
    // If neither method finds an EJ community, try the EJ support tool
    if (location) {
      const scriptPath = path.join(process.cwd(), 'climate_economy_ecosystem/tools/ej_support.py');
      const { stdout } = await execPromise(`python ${scriptPath} "${location}" --check-only`);
      const result = JSON.parse(stdout);
      return !result.error;
    }
    
    return false;
  } catch (error) {
    console.error('Error checking EJ community status:', error);
    return false;
  }
}

/**
 * Check if a location is a Gateway City
 * 
 * @param {string} location - Location name
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @returns {Promise<boolean>} True if Gateway City
 */
async function checkIfGatewayCity(location, latitude, longitude) {
  try {
    // Try looking up by name first
    if (location) {
      const { data, error } = await supabase
        .from('gateway_cities')
        .select('id')
        .or(`name.eq.${location},name.ilike.%${location}%`)
        .limit(1);
        
      if (!error && data && data.length > 0) {
        return true;
      }
    }
    
    // If we have coordinates, check nearby Gateway Cities
    if (latitude && longitude) {
      const { data, error } = await supabase
        .rpc('find_nearest_gateway_cities', { 
          lat: latitude, 
          lng: longitude,
          max_distance_km: 3, // Within city limits
          max_results: 1 
        });
        
      if (!error && data && data.length > 0) {
        return true;
      }
    }
    
    // If neither method finds a Gateway City, try the Gateway City Analyzer
    if (location) {
      const scriptPath = path.join(process.cwd(), 'climate_economy_ecosystem/tools/gateway_city_analyzer.py');
      const { stdout } = await execPromise(`python ${scriptPath} "${location}" --check-only`);
      const result = JSON.parse(stdout);
      return !result.error;
    }
    
    return false;
  } catch (error) {
    console.error('Error checking Gateway City status:', error);
    return false;
  }
}

/**
 * Find nearby Gateway Cities
 * 
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @returns {Promise<Array>} Nearby Gateway Cities
 */
async function findNearbyGatewayCities(latitude, longitude) {
  try {
    const { data, error } = await supabase
      .rpc('find_nearest_gateway_cities', { 
        lat: latitude, 
        lng: longitude,
        max_distance_km: 30, 
        max_results: 3 
      });
      
    if (!error && data) {
      return data;
    }
    
    return [];
  } catch (error) {
    console.error('Error finding nearby Gateway Cities:', error);
    return [];
  }
}

/**
 * Find nearby EJ communities
 * 
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @returns {Promise<Array>} Nearby EJ communities
 */
async function findNearbyEjCommunities(latitude, longitude) {
  try {
    const { data, error } = await supabase
      .rpc('find_nearest_ej_communities', { 
        lat: latitude, 
        lng: longitude,
        max_distance_km: 10, 
        max_results: 3 
      });
      
    if (!error && data) {
      return data;
    }
    
    return [];
  } catch (error) {
    console.error('Error finding nearby EJ communities:', error);
    return [];
  }
}

/**
 * Get detailed Gateway City analysis
 * 
 * @param {string} city - Gateway City name
 * @param {string} sector - Optional clean energy sector
 * @returns {Promise<Object>} Gateway City details
 */
async function getGatewayCityDetails(city, sector) {
  try {
    const scriptPath = path.join(process.cwd(), 'climate_economy_ecosystem/tools/gateway_city_analyzer.py');
    const sectorParam = sector ? `"${sector}"` : '';
    const { stdout } = await execPromise(`python ${scriptPath} "${city}" ${sectorParam}`);
    
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error getting Gateway City details:', error);
    return { error: 'Unable to analyze Gateway City' };
  }
}

/**
 * Get detailed EJ community analysis
 * 
 * @param {string} location - EJ community name
 * @param {string} sector - Optional clean energy sector
 * @returns {Promise<Object>} EJ community details
 */
async function getEjCommunityDetails(location, sector) {
  try {
    const scriptPath = path.join(process.cwd(), 'climate_economy_ecosystem/tools/ej_support.py');
    const sectorParam = sector ? `"${sector}"` : '';
    const { stdout } = await execPromise(`python ${scriptPath} "${location}" ${sectorParam}`);
    
    return JSON.parse(stdout);
  } catch (error) {
    console.error('Error getting EJ community details:', error);
    return { error: 'Unable to analyze EJ community' };
  }
}

/**
 * Geocode a location name to coordinates
 * 
 * @param {string} location - Location name
 * @returns {Promise<Object>} Latitude and longitude
 */
async function geocodeLocation(location) {
  // In a real implementation, this would use a geocoding service
  // For now, we'll use a hardcoded list of cities
  const locationMap = {
    'boston': { latitude: 42.3601, longitude: -71.0589 },
    'worcester': { latitude: 42.2626, longitude: -71.8023 },
    'springfield': { latitude: 42.1015, longitude: -72.5898 },
    'cambridge': { latitude: 42.3736, longitude: -71.1097 },
    'lowell': { latitude: 42.6334, longitude: -71.3162 },
    'new bedford': { latitude: 41.6362, longitude: -70.9342 },
    'lawrence': { latitude: 42.7070, longitude: -71.1631 },
    'chelsea': { latitude: 42.3917, longitude: -71.0328 },
    'dorchester': { latitude: 42.3016, longitude: -71.0676 },
    'holyoke': { latitude: 42.2042, longitude: -72.6162 }
  };
  
  const normalizedLocation = location.toLowerCase();
  
  if (locationMap[normalizedLocation]) {
    return locationMap[normalizedLocation];
  }
  
  // Check for partial matches
  for (const [key, coords] of Object.entries(locationMap)) {
    if (normalizedLocation.includes(key) || key.includes(normalizedLocation)) {
      return coords;
    }
  }
  
  return null;
}

/**
 * Get training programs for a location
 * 
 * @param {string} location - Location name
 * @param {Object} coordinates - Latitude and longitude
 * @param {string} sector - Optional clean energy sector
 * @param {boolean} isEjCommunity - If the location is an EJ community
 * @returns {Promise<Array>} Training programs
 */
async function getTrainingProgramsForLocation(location, coordinates, sector, isEjCommunity) {
  try {
    let query = supabase.from('training_programs').select('*');
    
    // Filter by location if provided
    if (location) {
      query = query.ilike('location', `%${location}%`);
    }
    
    // Filter by sector if provided
    if (sector) {
      query = query.eq('sector', sector);
    }
    
    // If EJ community, prefer EJ-focused programs
    if (isEjCommunity) {
      query = query.order('is_ej_focused', { ascending: false });
    }
    
    // Limit results
    query = query.limit(10);
    
    const { data, error } = await query;
    
    if (!error && data) {
      // If we have coordinates and few results, try finding nearby programs
      if (coordinates && (!data || data.length < 5)) {
        return await findNearbyTrainingPrograms(coordinates.latitude, coordinates.longitude, sector, isEjCommunity);
      }
      
      return data;
    }
    
    return [];
  } catch (error) {
    console.error('Error getting training programs:', error);
    return [];
  }
}

/**
 * Find nearby training programs
 * 
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @param {string} sector - Optional clean energy sector
 * @param {boolean} isEjCommunity - If the location is an EJ community
 * @returns {Promise<Array>} Nearby training programs
 */
async function findNearbyTrainingPrograms(latitude, longitude, sector, isEjCommunity) {
  try {
    // If it's an EJ community, use the EJ-focused training program finder
    if (isEjCommunity) {
      const { data, error } = await supabase
        .rpc('find_ej_training_programs', { 
          lat: latitude, 
          lng: longitude,
          max_distance_km: 20,
          sector: sector || null
        });
        
      if (!error && data) {
        return data;
      }
    }
    
    // Otherwise, use a simple distance-based query
    // (In a real implementation, this would use PostGIS spatial queries)
    const { data, error } = await supabase
      .from('training_programs')
      .select('*');
      
    if (!error && data) {
      // For now, just return all programs (spatial filtering would be done in the database)
      return data.slice(0, 10);
    }
    
    return [];
  } catch (error) {
    console.error('Error finding nearby training programs:', error);
    return [];
  }
}

/**
 * Get job opportunities for a location
 * 
 * @param {string} location - Location name
 * @param {Object} coordinates - Latitude and longitude
 * @param {string} sector - Optional clean energy sector
 * @param {boolean} isEjCommunity - If the location is an EJ community
 * @param {boolean} isGatewayCity - If the location is a Gateway City
 * @returns {Promise<Array>} Job opportunities
 */
async function getJobOpportunitiesForLocation(location, coordinates, sector, isEjCommunity, isGatewayCity) {
  try {
    let query = supabase.from('job_opportunities').select('*');
    
    // Filter by location if provided
    if (location) {
      query = query.ilike('location', `%${location}%`);
    }
    
    // Filter by sector if provided
    if (sector) {
      query = query.ilike('description', `%${sector}%`);
    }
    
    // If EJ community, prefer EJ-friendly jobs
    if (isEjCommunity) {
      query = query.order('is_ej_friendly', { ascending: false });
    }
    
    // If Gateway City, prefer Gateway City-focused jobs
    if (isGatewayCity) {
      query = query.order('is_gateway_city_focused', { ascending: false });
    }
    
    // Limit results
    query = query.limit(10);
    
    const { data, error } = await query;
    
    if (!error && data) {
      return data;
    }
    
    return [];
  } catch (error) {
    console.error('Error getting job opportunities:', error);
    return [];
  }
}

/**
 * Get support programs for an EJ community
 * 
 * @param {string} location - EJ community name
 * @param {string} sector - Optional clean energy sector
 * @returns {Promise<Array>} Support programs
 */
async function getSupportProgramsForEj(location, sector) {
  try {
    let query = supabase.from('ej_support_programs').select('*');
    
    // Filter by sector if provided
    if (sector) {
      query = query.contains('targeted_sectors', [sector]);
    }
    
    // Limit results
    query = query.limit(5);
    
    const { data, error } = await query;
    
    if (!error && data) {
      return data;
    }
    
    // If database query fails, fall back to the EJ support tool
    const scriptPath = path.join(process.cwd(), 'climate_economy_ecosystem/tools/ej_support.py');
    const sectorParam = sector ? `"${sector}"` : '';
    const { stdout } = await execPromise(`python ${scriptPath} "${location}" ${sectorParam} --support-programs-only`);
    
    const result = JSON.parse(stdout);
    return result.support_programs || [];
  } catch (error) {
    console.error('Error getting EJ support programs:', error);
    return [];
  }
}

/**
 * Generate insights based on location
 * 
 * @param {Object} locationData - Location analysis data
 * @param {string} sector - Optional clean energy sector
 * @returns {Promise<Array>} Insights
 */
async function generateLocationInsights(locationData, sector) {
  try {
    const { is_ej_community, is_gateway_city, name } = locationData;
    
    // If we already have insights from the Gateway City or EJ tools, use those
    if (locationData.workforce_insights || locationData.ej_specific_insights) {
      return locationData.workforce_insights || locationData.ej_specific_insights || [];
    }
    
    // Otherwise, generate new insights based on location characteristics
    const locationContext = [];
    
    if (is_gateway_city) {
      locationContext.push('Gateway City');
    }
    
    if (is_ej_community) {
      locationContext.push('Environmental Justice community');
    }
    
    const locationType = locationContext.join(' and ') || 'Massachusetts community';
    
    const sectorContext = sector ? `in the ${sector} sector` : 'across clean energy sectors';
    
    // For a real implementation, this would use a robust AI prompt
    // For now, return hardcoded insights based on location type
    if (is_ej_community) {
      return [
        `${name} has potential for community-based clean energy projects ${sectorContext}`,
        `Consider workforce programs with support services to address transportation and childcare barriers`,
        `Multilingual outreach is important for clean energy opportunities in this community`
      ];
    } else if (is_gateway_city) {
      return [
        `${name} has strong opportunities for clean energy careers ${sectorContext}`,
        `Local community colleges and vocational schools offer relevant training programs`,
        `Leveraging existing manufacturing infrastructure for clean energy growth shows promise`
      ];
    } else {
      return [
        `Consider clean energy opportunities in nearby Gateway Cities and EJ communities`,
        `Remote and hybrid work options can expand access to clean energy careers`,
        `Massachusetts offers incentives and programs for clean energy adoption statewide`
      ];
    }
  } catch (error) {
    console.error('Error generating location insights:', error);
    return [];
  }
} 