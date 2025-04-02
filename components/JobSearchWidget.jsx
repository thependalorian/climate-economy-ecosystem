import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { Alert, Button, Card, Checkbox, Input, Select, Spinner } from 'daisyui';

const SECTORS = [
  "High-Performance Buildings",
  "Renewable Energy",
  "Clean Transportation",
  "Energy Storage",
  "Grid Modernization",
  "Offshore Wind",
  "Workforce Development",
  "Education & Training",
  "Innovation & Entrepreneurship",
  "Business Development",
  "Economic Development",
  "Ecosystem Development",
  "Energy Efficiency"
];

const LOCATIONS = [
  "Boston, MA",
  "Cambridge, MA",
  "Somerville, MA",
  "Worcester, MA",
  "Springfield, MA",
  "Lowell, MA",
  "Amherst, MA",
  "Remote"
];

const EXPERIENCE_LEVELS = [
  "Entry Level",
  "Mid Level",
  "Senior Level",
  "Internship",
  "Apprenticeship"
];

const REMOTE_OPTIONS = [
  "On-site",
  "Remote",
  "Hybrid"
];

/**
 * Job Search Widget Component
 * 
 * This component allows users to search for jobs from our defined companies
 * based on their profile and search criteria.
 */
const JobSearchWidget = ({ userProfile, onJobSelected }) => {
  const { data: session } = useSession();
  const [searchText, setSearchText] = useState('');
  const [selectedSectors, setSelectedSectors] = useState([]);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [experienceLevel, setExperienceLevel] = useState('');
  const [remoteStatus, setRemoteStatus] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  // Load user profile data for initial search criteria
  useEffect(() => {
    if (userProfile) {
      if (userProfile.interested_sectors) {
        setSelectedSectors(userProfile.interested_sectors);
      }
    }
  }, [userProfile]);

  const handleSearch = async () => {
    if (!session) {
      setError('You must be signed in to search for jobs');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/jobs/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          search_text: searchText,
          sectors: selectedSectors.length > 0 ? selectedSectors : undefined,
          locations: selectedLocations.length > 0 ? selectedLocations : undefined,
          experience_level: experienceLevel || undefined,
          remote_status: remoteStatus || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to search for jobs');
      }

      const data = await response.json();
      
      if (data.success) {
        setSearchResults(data.results);
      } else {
        setError(data.error || 'An error occurred while searching for jobs');
        setSearchResults([]);
      }
    } catch (err) {
      setError(err.message || 'An error occurred while searching for jobs');
      setSearchResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSectorChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setSelectedSectors([...selectedSectors, value]);
    } else {
      setSelectedSectors(selectedSectors.filter(sector => sector !== value));
    }
  };

  const handleLocationChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setSelectedLocations([...selectedLocations, value]);
    } else {
      setSelectedLocations(selectedLocations.filter(location => location !== value));
    }
  };

  const toggleExpanded = () => {
    setExpanded(!expanded);
  };

  const handleJobClick = (job) => {
    if (onJobSelected) {
      onJobSelected(job);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card className="bg-base-100 shadow-xl mb-6">
        <Card.Body>
          <h2 className="card-title">Job Search</h2>
          <p className="mb-4">Search for jobs from our Massachusetts clean energy companies</p>
          
          <div className="space-y-4">
            <div className="flex flex-col md:flex-row gap-2">
              <Input
                type="text"
                placeholder="Search for jobs (e.g., energy analyst, solar installer)"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="flex-1"
              />
              <Button 
                color="primary" 
                onClick={handleSearch}
                disabled={isLoading}
                className="min-w-32"
              >
                {isLoading ? <Spinner size="sm" /> : 'Search Jobs'}
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                size="sm" 
                variant="outline" 
                onClick={toggleExpanded}
                className="ml-auto"
              >
                {expanded ? 'Hide Filters' : 'Show Filters'}
              </Button>
            </div>
            
            {expanded && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-base-300">
                <div>
                  <label className="font-medium">Sectors</label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                    {SECTORS.map(sector => (
                      <div key={sector} className="flex items-center gap-2">
                        <Checkbox
                          id={`sector-${sector}`}
                          value={sector}
                          checked={selectedSectors.includes(sector)}
                          onChange={handleSectorChange}
                        />
                        <label htmlFor={`sector-${sector}`} className="cursor-pointer text-sm">
                          {sector}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <div className="mb-4">
                    <label className="font-medium">Locations</label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                      {LOCATIONS.map(location => (
                        <div key={location} className="flex items-center gap-2">
                          <Checkbox
                            id={`location-${location}`}
                            value={location}
                            checked={selectedLocations.includes(location)}
                            onChange={handleLocationChange}
                          />
                          <label htmlFor={`location-${location}`} className="cursor-pointer text-sm">
                            {location}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="font-medium">Experience Level</label>
                      <Select
                        value={experienceLevel}
                        onChange={(e) => setExperienceLevel(e.target.value)}
                        className="w-full mt-2"
                      >
                        <option value="">Any Experience Level</option>
                        {EXPERIENCE_LEVELS.map(level => (
                          <option key={level} value={level}>{level}</option>
                        ))}
                      </Select>
                    </div>
                    
                    <div>
                      <label className="font-medium">Remote Status</label>
                      <Select
                        value={remoteStatus}
                        onChange={(e) => setRemoteStatus(e.target.value)}
                        className="w-full mt-2"
                      >
                        <option value="">Any Remote Status</option>
                        {REMOTE_OPTIONS.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </Select>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card.Body>
      </Card>
      
      {error && (
        <Alert className="alert-error mb-6">
          <span>{error}</span>
        </Alert>
      )}
      
      {searchResults.length > 0 ? (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Found {searchResults.length} job listings</h3>
          
          {searchResults.map(job => (
            <Card 
              key={job.id} 
              className="bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => handleJobClick(job)}
            >
              <Card.Body>
                <div className="flex justify-between">
                  <Card.Title>{job.title}</Card.Title>
                  <span className="badge badge-primary">{job.company}</span>
                </div>
                <div className="flex gap-2 flex-wrap mt-2">
                  {job.location && (
                    <span className="badge badge-outline badge-sm">{job.location}</span>
                  )}
                  {job.sector && (
                    <span className="badge badge-outline badge-sm">{job.sector}</span>
                  )}
                  {job.experience_level && (
                    <span className="badge badge-outline badge-sm">{job.experience_level}</span>
                  )}
                  {job.remote_status && (
                    <span className="badge badge-outline badge-sm">{job.remote_status}</span>
                  )}
                </div>
                <p className="mt-2 text-sm line-clamp-2">{job.description}</p>
                <div className="card-actions justify-end mt-4">
                  <Button color="primary" size="sm">View Details</Button>
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      ) : (
        searchText && !isLoading && !error && (
          <div className="text-center py-6">
            <h3 className="text-lg font-semibold">No job listings found</h3>
            <p className="text-sm text-gray-500 mt-2">Try adjusting your search criteria</p>
          </div>
        )
      )}
    </div>
  );
};

export default JobSearchWidget; 