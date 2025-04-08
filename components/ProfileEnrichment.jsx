import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import toast from '../lib/toast-shim';

// Import metrics service
import { metricsService } from '../lib/monitoring/metrics_service';

/**
 * ProfileEnrichment Component
 * 
 * Displays a user interface for profile enrichment where users can review
 * and verify skills that have been extracted from their profile information
 */
const ProfileEnrichment = ({ userId, onComplete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [enrichmentStatus, setEnrichmentStatus] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [skillCategories, setSkillCategories] = useState({
    technical: [],
    transferable: [],
    soft: []
  });
  const [dataSources, setDataSources] = useState([]);
  const router = useRouter();

  // Fetch user profile and enrichment status
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (!userId) return;
      
      setIsLoading(true);
      try {
        const response = await fetch(`/api/profile/${userId}`);
        if (!response.ok) throw new Error('Failed to fetch profile');
        
        const data = await response.json();
        setUserProfile(data);
        
        // Check if profile has enrichment data
        if (data.enrichment) {
          setEnrichmentStatus(data.enrichment.status);
          
          // Set skill categories if available
          if (data.enrichment.skills) {
            setSkillCategories({
              technical: data.enrichment.skills.technical || [],
              transferable: data.enrichment.skills.transferable || [],
              soft: data.enrichment.skills.soft || []
            });
          }
          
          // Set data sources if available
          if (data.enrichment.data_sources) {
            setDataSources(data.enrichment.data_sources);
          }
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
        toast.error('Failed to load profile information');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserProfile();
  }, [userId]);

  // Start profile enrichment process
  const startEnrichment = async () => {
    setIsEnriching(true);
    try {
      const response = await fetch('/api/profile/enrichment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          userId,
          options: {
            verify_before_save: true,
            member_companies_only: true
          }
        })
      });
      
      if (!response.ok) throw new Error('Enrichment process failed');
      
      const data = await response.json();
      
      // Update local state with enrichment results
      setUserProfile(data.profile);
      setEnrichmentStatus(data.profile.enrichment.status);
      
      if (data.profile.enrichment.skills) {
        setSkillCategories({
          technical: data.profile.enrichment.skills.technical || [],
          transferable: data.profile.enrichment.skills.transferable || [],
          soft: data.profile.enrichment.skills.soft || []
        });
      }
      
      if (data.profile.enrichment.data_sources) {
        setDataSources(data.profile.enrichment.data_sources);
      }
      
      // Track profile enrichment metrics
      try {
        metricsService.trackProfileEnrichment({
          status: data.profile.enrichment.status,
          skills: data.profile.enrichment.skills,
          data_sources: data.profile.enrichment.data_sources,
          is_verified: false
        });
      } catch (metricError) {
        console.error('Error tracking metrics:', metricError);
      }
      
      toast.success('Profile enrichment completed');
    } catch (error) {
      console.error('Error during enrichment:', error);
      toast.error('Profile enrichment failed. Please try again later.');
    } finally {
      setIsEnriching(false);
    }
  };

  // Handle skill addition
  const addSkill = (category, skill) => {
    setSkillCategories(prev => ({
      ...prev,
      [category]: [...prev[category], skill]
    }));
  };

  // Handle skill removal
  const removeSkill = (category, index) => {
    setSkillCategories(prev => ({
      ...prev,
      [category]: prev[category].filter((_, i) => i !== index)
    }));
  };

  // Save verified skills
  const saveVerifiedSkills = async () => {
    setIsLoading(true);
    
    // Calculate metrics data for verification
    const originalSkills = userProfile?.enrichment?.skills || { technical: [], transferable: [], soft: [] };
    const verificationData = {
      verifiedCount: Object.values(skillCategories).reduce((total, arr) => total + arr.length, 0),
      addedCount: 0,
      removedCount: 0,
      categories: Object.keys(skillCategories)
    };
    
    // Count added/removed skills
    for (const category in skillCategories) {
      const original = originalSkills[category] || [];
      const current = skillCategories[category];
      
      // Count removed skills (in original but not in current)
      const removed = original.filter(skill => !current.includes(skill)).length;
      
      // Count added skills (in current but not in original)
      const added = current.filter(skill => !original.includes(skill)).length;
      
      verificationData.removedCount += removed;
      verificationData.addedCount += added;
    }
    
    try {
      const response = await fetch('/api/profile/enrichment', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          userId,
          verifiedData: {
            skills: skillCategories
          }
        })
      });
      
      if (!response.ok) throw new Error('Failed to save verified skills');
      
      // Track skill verification metrics
      try {
        metricsService.trackSkillVerification(verificationData);
      } catch (metricError) {
        console.error('Error tracking verification metrics:', metricError);
      }
      
      toast.success('Profile skills updated successfully');
      
      // Call completion handler if provided
      if (onComplete) onComplete();
      
    } catch (error) {
      console.error('Error saving verified skills:', error);
      toast.error('Failed to save skills. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-6 space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        <p className="text-lg">Loading profile information...</p>
      </div>
    );
  }

  // Show enrichment initiation UI if not yet enriched
  if (!enrichmentStatus || enrichmentStatus === 'pending' || enrichmentStatus === 'failed') {
    return (
      <div className="bg-base-200 rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Profile Enrichment</h2>
        <p className="mb-4">
          Enhance your profile by discovering skills from your education, work experience, and
          professional background. This helps us provide better job matches and recommendations.
        </p>
        
        <div className="alert alert-info mb-4">
          <div className="flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-6 h-6 mx-2 stroke-current">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <label>You'll have a chance to review and verify all information before it's saved to your profile.</label>
          </div>
        </div>
        
        <button 
          className="btn btn-primary w-full"
          onClick={startEnrichment}
          disabled={isEnriching}
        >
          {isEnriching ? (
            <>
              <span className="loading loading-spinner"></span>
              Analyzing Your Background...
            </>
          ) : (
            'Enhance My Profile'
          )}
        </button>
      </div>
    );
  }

  // Show verification UI if enrichment completed
  return (
    <div className="bg-base-200 rounded-lg shadow-lg p-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Verify Your Skills</h2>
      <p className="mb-6">
        We've identified these skills based on your profile information. Please review and verify them
        before saving to your profile.
      </p>
      
      {/* Technical Skills */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Technical Skills</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {skillCategories.technical.map((skill, index) => (
            <div key={`tech-${index}`} className="badge badge-primary badge-lg gap-2">
              {skill}
              <button onClick={() => removeSkill('technical', index)}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-4 h-4 stroke-current">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
        <div className="flex items-center">
          <input 
            type="text" 
            id="newTechnicalSkill" 
            className="input input-bordered w-full max-w-xs mr-2" 
            placeholder="Add a technical skill" 
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.target.value.trim()) {
                addSkill('technical', e.target.value.trim());
                e.target.value = '';
              }
            }}
          />
          <button 
            className="btn btn-sm btn-outline"
            onClick={() => {
              const input = document.getElementById('newTechnicalSkill');
              if (input.value.trim()) {
                addSkill('technical', input.value.trim());
                input.value = '';
              }
            }}
          >
            Add
          </button>
        </div>
      </div>
      
      {/* Transferable Skills */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Transferable Skills</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {skillCategories.transferable.map((skill, index) => (
            <div key={`trans-${index}`} className="badge badge-secondary badge-lg gap-2">
              {skill}
              <button onClick={() => removeSkill('transferable', index)}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-4 h-4 stroke-current">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
        <div className="flex items-center">
          <input 
            type="text" 
            id="newTransferableSkill" 
            className="input input-bordered w-full max-w-xs mr-2" 
            placeholder="Add a transferable skill" 
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.target.value.trim()) {
                addSkill('transferable', e.target.value.trim());
                e.target.value = '';
              }
            }}
          />
          <button 
            className="btn btn-sm btn-outline"
            onClick={() => {
              const input = document.getElementById('newTransferableSkill');
              if (input.value.trim()) {
                addSkill('transferable', input.value.trim());
                input.value = '';
              }
            }}
          >
            Add
          </button>
        </div>
      </div>
      
      {/* Soft Skills */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Soft Skills</h3>
        <div className="flex flex-wrap gap-2 mb-3">
          {skillCategories.soft.map((skill, index) => (
            <div key={`soft-${index}`} className="badge badge-accent badge-lg gap-2">
              {skill}
              <button onClick={() => removeSkill('soft', index)}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-4 h-4 stroke-current">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
        <div className="flex items-center">
          <input 
            type="text" 
            id="newSoftSkill" 
            className="input input-bordered w-full max-w-xs mr-2" 
            placeholder="Add a soft skill" 
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.target.value.trim()) {
                addSkill('soft', e.target.value.trim());
                e.target.value = '';
              }
            }}
          />
          <button 
            className="btn btn-sm btn-outline"
            onClick={() => {
              const input = document.getElementById('newSoftSkill');
              if (input.value.trim()) {
                addSkill('soft', input.value.trim());
                input.value = '';
              }
            }}
          >
            Add
          </button>
        </div>
      </div>
      
      {/* Information Sources */}
      <div className="mb-6">
        <div className="collapse collapse-arrow bg-base-100">
          <input type="checkbox" className="peer" /> 
          <div className="collapse-title text-lg font-semibold">
            Information Sources
          </div>
          <div className="collapse-content"> 
            <ul className="list-disc pl-5">
              {dataSources.map((source, index) => (
                <li key={index} className="mb-2">
                  <span className="font-semibold">{source.type}</span>
                  {source.query && <span className="text-sm"> - "{source.query}"</span>}
                </li>
              ))}
              {dataSources.length === 0 && (
                <li>No specific data sources available</li>
              )}
            </ul>
          </div>
        </div>
      </div>
      
      {/* Privacy Note */}
      <div className="alert alert-info mb-6">
        <div className="flex-1">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-6 h-6 mx-2 stroke-current">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <label>We only search for information from trusted sources and member companies in our ecosystem. Your privacy is important to us.</label>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        <button 
          className="btn btn-ghost"
          onClick={() => {
            if (onComplete) onComplete();
          }}
        >
          Skip
        </button>
        <button 
          className="btn btn-primary"
          onClick={saveVerifiedSkills}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="loading loading-spinner"></span>
              Saving...
            </>
          ) : (
            'Save Verified Skills'
          )}
        </button>
      </div>
    </div>
  );
};

export default ProfileEnrichment; 