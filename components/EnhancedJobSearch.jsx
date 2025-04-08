import { useState, useEffect, useRef } from 'react';
import toast from '../lib/toast-shim';
import Link from 'next/link';

// Import metrics service
import { metricsService } from '../lib/monitoring/metrics_service';

/**
 * EnhancedJobSearch Component
 * 
 * Provides an enhanced job search interface that leverages user profile enrichment data
 * to improve search results and provide job recommendations.
 */
const EnhancedJobSearch = ({ userId }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [searchParams, setSearchParams] = useState({
    query: '',
    sectors: [],
    focus_areas: [],
    locations: [],
    skills: [],
    experience_level: '',
    remote_status: 'any'
  });
  const [availableSectors, setAvailableSectors] = useState([]);
  const [availableFocusAreas, setAvailableFocusAreas] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [isProfileEnriched, setIsProfileEnriched] = useState(false);
  const searchInputRef = useRef(null);

  // Fetch user profile, sectors, focus areas, and job recommendations on component mount
  useEffect(() => {
    const fetchInitialData = async () => {
      if (!userId) return;
      
      setIsLoading(true);
      try {
        // Fetch user profile
        const profileResponse = await fetch(`/api/profile/${userId}`);
        if (!profileResponse.ok) throw new Error('Failed to fetch profile');
        
        const profileData = await profileResponse.json();
        setUserProfile(profileData);
        
        // Check if profile is enriched
        if (profileData.enrichment && 
            profileData.enrichment.status === 'completed' && 
            profileData.enrichment.skills) {
          setIsProfileEnriched(true);
        }
        
        // Fetch sectors
        const sectorsResponse = await fetch('/api/sectors');
        if (sectorsResponse.ok) {
          const sectorsData = await sectorsResponse.json();
          setAvailableSectors(sectorsData);
        }
        
        // Fetch focus areas
        const focusAreasResponse = await fetch('/api/focus-areas');
        if (focusAreasResponse.ok) {
          const focusAreasData = await focusAreasResponse.json();
          setAvailableFocusAreas(focusAreasData);
        }
        
        // Fetch job recommendations
        const recommendationsResponse = await fetch(`/api/jobs/enhanced-search?userId=${userId}&limit=5`);
        if (recommendationsResponse.ok) {
          const recommendationsData = await recommendationsResponse.json();
          setRecommendations(recommendationsData.jobs || []);
          
          // Track recommendations metrics if we got some
          if (recommendationsData.jobs && recommendationsData.jobs.length > 0) {
            try {
              metricsService.trackEnhancedJobSearch({
                query: "recommendations",
                results: recommendationsData.jobs,
                usedProfileData: true,
                isRecommendation: true
              });
            } catch (metricError) {
              console.error('Error tracking recommendation metrics:', metricError);
            }
          }
        }
      } catch (error) {
        console.error('Error fetching initial data:', error);
        toast.error('Failed to load initial data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchInitialData();
  }, [userId]);

  // Handle search form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle multi-select inputs (sectors, focus areas, locations, skills)
  const handleMultiSelectChange = (name, value) => {
    setSearchParams(prev => {
      // If value is already in array, remove it, otherwise add it
      const currentValues = prev[name];
      if (currentValues.includes(value)) {
        return {
          ...prev,
          [name]: currentValues.filter(item => item !== value)
        };
      } else {
        return {
          ...prev,
          [name]: [...currentValues, value]
        };
      }
    });
  };

  // Handle search submission
  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    
    setIsLoading(true);
    setShowRecommendations(false);
    
    try {
      const response = await fetch('/api/jobs/enhanced-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          userId,
          searchParams
        })
      });
      
      if (!response.ok) throw new Error('Search failed');
      
      const data = await response.json();
      setSearchResults(data.jobs || []);
      
      // Track search metrics
      try {
        metricsService.trackEnhancedJobSearch({
          query: searchParams.query,
          results: data.jobs || [],
          usedProfileData: data.search_stats?.enhanced || false,
          sectors: searchParams.sectors,
          skills: searchParams.skills,
          isRecommendation: false
        });
      } catch (metricError) {
        console.error('Error tracking search metrics:', metricError);
      }
      
      if (data.jobs.length === 0) {
        toast.info('No matching jobs found. Try adjusting your search criteria.');
      }
    } catch (error) {
      console.error('Error performing job search:', error);
      toast.error('Search failed. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Clear search form and show recommendations
  const handleClearSearch = () => {
    setSearchParams({
      query: '',
      sectors: [],
      focus_areas: [],
      locations: [],
      skills: [],
      experience_level: '',
      remote_status: 'any'
    });
    
    setSearchResults([]);
    setShowRecommendations(true);
    
    // Focus on search input
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };
  
  // Add a skill to the search
  const addSkillToSearch = (skill) => {
    if (!searchParams.skills.includes(skill)) {
      setSearchParams(prev => ({
        ...prev,
        skills: [...prev.skills, skill]
      }));
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Render job card
  const renderJobCard = (job, index, isRecommendation = false) => {
    return (
      <div key={`job-${index}`} className="card bg-base-100 shadow-md hover:shadow-lg transition-shadow duration-300">
        <div className="card-body">
          {isRecommendation && (
            <div className="badge badge-secondary mb-2">Recommended</div>
          )}
          
          <div className="flex justify-between items-start">
            <h3 className="card-title text-lg md:text-xl">{job.title}</h3>
            {job.relevance_score && (
              <div className="badge badge-primary">{Math.round(job.relevance_score * 100)}% Match</div>
            )}
          </div>
          
          <div className="mt-2">
            <p className="text-base-content/80">
              <span className="font-medium">{job.company}</span>
              {job.location && <span> • {job.location}</span>}
              {job.remote_status && job.remote_status !== 'onsite' && (
                <span className="badge badge-outline badge-xs ml-2">
                  {job.remote_status === 'remote' ? 'Remote' : 'Hybrid'}
                </span>
              )}
            </p>
          </div>
          
          {job.description && (
            <p className="mt-2 text-sm text-base-content/70 line-clamp-3">
              {job.description}
            </p>
          )}
          
          {job.matching_skills && job.matching_skills.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-base-content/60 mb-1">Matching Skills:</p>
              <div className="flex flex-wrap gap-1">
                {job.matching_skills.slice(0, 5).map((skill, i) => (
                  <span key={i} className="badge badge-sm badge-primary">{skill}</span>
                ))}
                {job.matching_skills.length > 5 && (
                  <span className="badge badge-sm badge-outline">+{job.matching_skills.length - 5} more</span>
                )}
              </div>
            </div>
          )}
          
          <div className="card-actions justify-between items-center mt-4">
            <div className="text-xs text-base-content/60">
              {job.posted_date && `Posted ${formatDate(job.posted_date)}`}
            </div>
            
            <Link href={`/jobs/${job.id}`} className="btn btn-primary btn-sm">
              View Details
            </Link>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Search Form */}
      <div className="lg:col-span-1 bg-base-200 p-4 rounded-lg sticky top-4 self-start">
        <h2 className="text-xl font-bold mb-4">Find Your Climate Career</h2>
        
        {!isProfileEnriched && (
          <div className="alert alert-info mb-4 text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <span className="font-bold">Tip:</span> Enrich your profile to get better job matches.
              <Link href="/profile/enrich" className="block mt-1 text-primary underline">
                Enrich profile now
              </Link>
            </div>
          </div>
        )}
        
        <form onSubmit={handleSearch} className="space-y-4">
          {/* Search Query */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Search</span>
            </label>
            <input
              ref={searchInputRef}
              type="text"
              name="query"
              value={searchParams.query}
              onChange={handleInputChange}
              placeholder="Job title, keyword, or company"
              className="input input-bordered w-full"
            />
          </div>
          
          {/* Sectors */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Sectors</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {availableSectors.map((sector, index) => (
                <label key={index} className="cursor-pointer">
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={searchParams.sectors.includes(sector.name)}
                    onChange={() => handleMultiSelectChange('sectors', sector.name)}
                  />
                  <span className={`badge badge-lg ${searchParams.sectors.includes(sector.name) ? 'badge-primary' : 'badge-outline'}`}>
                    {sector.name}
                  </span>
                </label>
              ))}
            </div>
          </div>
          
          {/* Focus Areas */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Focus Areas</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {availableFocusAreas.map((area, index) => (
                <label key={index} className="cursor-pointer">
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={searchParams.focus_areas.includes(area.name)}
                    onChange={() => handleMultiSelectChange('focus_areas', area.name)}
                  />
                  <span className={`badge badge-lg ${searchParams.focus_areas.includes(area.name) ? 'badge-secondary' : 'badge-outline'}`}>
                    {area.name}
                  </span>
                </label>
              ))}
            </div>
          </div>
          
          {/* Skills */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Skills</span>
            </label>
            
            {isProfileEnriched && (
              <div className="mb-2">
                <div className="collapse collapse-arrow bg-base-100">
                  <input type="checkbox" className="peer" /> 
                  <div className="collapse-title text-sm font-medium">
                    Add skills from your profile
                  </div>
                  <div className="collapse-content">
                    <div className="tabs tabs-boxed mb-2">
                      <a className="tab tab-active">Technical</a>
                      <a className="tab">Transferable</a>
                      <a className="tab">Soft</a>
                    </div>
                    
                    <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto p-1">
                      {userProfile?.enrichment?.skills?.technical?.map((skill, i) => (
                        <button
                          key={i}
                          type="button"
                          className="badge badge-sm badge-primary cursor-pointer"
                          onClick={() => addSkillToSearch(skill)}
                        >
                          {skill}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div className="flex flex-wrap gap-2 mb-2">
              {searchParams.skills.map((skill, index) => (
                <div key={index} className="badge badge-primary badge-lg gap-2">
                  {skill}
                  <button
                    type="button"
                    onClick={() => setSearchParams(prev => ({
                      ...prev,
                      skills: prev.skills.filter((_, i) => i !== index)
                    }))}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-4 h-4 stroke-current">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
            
            <div className="flex gap-2">
              <input
                type="text"
                className="input input-bordered flex-1"
                placeholder="Add a skill"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    e.preventDefault();
                    addSkillToSearch(e.target.value.trim());
                    e.target.value = '';
                  }
                }}
              />
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={(e) => {
                  const input = e.target.previousElementSibling;
                  if (input.value.trim()) {
                    addSkillToSearch(input.value.trim());
                    input.value = '';
                  }
                }}
              >
                Add
              </button>
            </div>
          </div>
          
          {/* Location */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Location</span>
            </label>
            <input
              type="text"
              name="locations"
              value={searchParams.locations.join(', ')}
              onChange={(e) => setSearchParams(prev => ({
                ...prev,
                locations: e.target.value.split(',').map(loc => loc.trim()).filter(Boolean)
              }))}
              placeholder="City, State, or Country (comma separated)"
              className="input input-bordered w-full"
            />
          </div>
          
          {/* Experience Level */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Experience Level</span>
            </label>
            <select
              name="experience_level"
              value={searchParams.experience_level}
              onChange={handleInputChange}
              className="select select-bordered w-full"
            >
              <option value="">Any experience level</option>
              <option value="entry">Entry level</option>
              <option value="mid">Mid level</option>
              <option value="senior">Senior level</option>
              <option value="executive">Executive</option>
            </select>
          </div>
          
          {/* Remote Status */}
          <div className="form-control">
            <label className="label">
              <span className="label-text">Work Type</span>
            </label>
            <select
              name="remote_status"
              value={searchParams.remote_status}
              onChange={handleInputChange}
              className="select select-bordered w-full"
            >
              <option value="any">Any work type</option>
              <option value="remote">Remote only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
            </select>
          </div>
          
          {/* Action Buttons */}
          <div className="flex gap-2 mt-6">
            <button
              type="button"
              className="btn btn-outline flex-1"
              onClick={handleClearSearch}
            >
              Clear
            </button>
            <button
              type="submit"
              className="btn btn-primary flex-1"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="loading loading-spinner loading-sm"></span>
              ) : (
                'Search'
              )}
            </button>
          </div>
        </form>
      </div>
      
      {/* Results */}
      <div className="lg:col-span-2">
        {isLoading && !searchResults.length && !recommendations.length ? (
          <div className="flex flex-col items-center justify-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            <p className="mt-4 text-lg">Searching for jobs...</p>
          </div>
        ) : (
          <>
            {showRecommendations && recommendations.length > 0 ? (
              <div>
                <h2 className="text-2xl font-bold mb-4">Recommended for You</h2>
                <div className="space-y-4">
                  {recommendations.map((job, index) => renderJobCard(job, index, true))}
                </div>
              </div>
            ) : searchResults.length > 0 ? (
              <div>
                <h2 className="text-2xl font-bold mb-4">Search Results</h2>
                <p className="text-sm text-base-content/70 mb-4">
                  Found {searchResults.length} matching jobs
                </p>
                <div className="space-y-4">
                  {searchResults.map((job, index) => renderJobCard(job, index))}
                </div>
              </div>
            ) : !isLoading && !showRecommendations ? (
              <div className="flex flex-col items-center justify-center h-96 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current w-16 h-16 mb-4 opacity-30">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h3 className="text-xl font-semibold">No jobs found</h3>
                <p className="mt-2 text-base-content/70 max-w-md">
                  Try adjusting your search criteria or <button className="text-primary" onClick={() => setShowRecommendations(true)}>view recommendations</button> instead.
                </p>
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
};

export default EnhancedJobSearch; 