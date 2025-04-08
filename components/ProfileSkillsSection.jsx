import { useState } from 'react';
import Link from 'next/link';

/**
 * ProfileSkillsSection Component
 * 
 * Displays a user's enriched skills organized by category in their profile.
 * Also allows users to edit their skills or initiate profile enrichment if not yet done.
 */
const ProfileSkillsSection = ({ profileData, isOwnProfile }) => {
  const [activeTab, setActiveTab] = useState('technical');
  
  // Check if profile has enrichment data with skills
  const hasEnrichment = profileData?.enrichment && 
                       profileData.enrichment.status === 'completed' && 
                       profileData.enrichment.skills;
                       
  // Get skills by category
  const skills = hasEnrichment ? profileData.enrichment.skills : { technical: [], transferable: [], soft: [] };
  
  const totalSkills = (skills.technical?.length || 0) + 
                     (skills.transferable?.length || 0) + 
                     (skills.soft?.length || 0);
  
  // When profile is not enriched
  if (!hasEnrichment && isOwnProfile) {
    return (
      <div className="bg-base-200 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Skills</h2>
        
        <div className="text-center py-8">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="w-16 h-16 mx-auto mb-4 stroke-current opacity-30">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          
          <h3 className="text-lg font-semibold mb-2">Enhance Your Profile</h3>
          <p className="text-base-content/70 mb-4 max-w-md mx-auto">
            Discover your skills based on your education, work experience, and professional background.
            This helps us provide better job matches and recommendations.
          </p>
          
          <Link href="/profile/enrich" className="btn btn-primary">
            Enhance My Profile
          </Link>
        </div>
      </div>
    );
  }
  
  // When someone else's profile is not enriched
  if (!hasEnrichment && !isOwnProfile) {
    return null; // Don't show this section for non-enriched profiles of other users
  }
  
  // Empty state when profile is enriched but has no skills
  if (hasEnrichment && totalSkills === 0) {
    return (
      <div className="bg-base-200 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Skills</h2>
        
        <div className="text-center py-6">
          <p className="text-base-content/70">No skills have been added yet.</p>
          
          {isOwnProfile && (
            <Link href="/profile/enrich" className="btn btn-outline btn-sm mt-4">
              Add Skills
            </Link>
          )}
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-base-200 rounded-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Skills</h2>
        
        {isOwnProfile && (
          <Link href="/profile/enrich" className="btn btn-outline btn-sm">
            Edit Skills
          </Link>
        )}
      </div>
      
      {/* Tabs */}
      <div className="tabs tabs-boxed mb-4">
        <button 
          className={`tab ${activeTab === 'technical' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('technical')}
        >
          Technical ({skills.technical?.length || 0})
        </button>
        <button 
          className={`tab ${activeTab === 'transferable' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('transferable')}
        >
          Transferable ({skills.transferable?.length || 0})
        </button>
        <button 
          className={`tab ${activeTab === 'soft' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('soft')}
        >
          Soft ({skills.soft?.length || 0})
        </button>
      </div>
      
      {/* Skills List */}
      <div className="min-h-[100px]">
        {activeTab === 'technical' && (
          <div className="flex flex-wrap gap-2">
            {skills.technical?.map((skill, index) => (
              <div key={index} className="badge badge-primary badge-lg">
                {skill}
              </div>
            ))}
            {(skills.technical?.length || 0) === 0 && (
              <p className="text-base-content/70 text-sm py-4">No technical skills added yet.</p>
            )}
          </div>
        )}
        
        {activeTab === 'transferable' && (
          <div className="flex flex-wrap gap-2">
            {skills.transferable?.map((skill, index) => (
              <div key={index} className="badge badge-secondary badge-lg">
                {skill}
              </div>
            ))}
            {(skills.transferable?.length || 0) === 0 && (
              <p className="text-base-content/70 text-sm py-4">No transferable skills added yet.</p>
            )}
          </div>
        )}
        
        {activeTab === 'soft' && (
          <div className="flex flex-wrap gap-2">
            {skills.soft?.map((skill, index) => (
              <div key={index} className="badge badge-accent badge-lg">
                {skill}
              </div>
            ))}
            {(skills.soft?.length || 0) === 0 && (
              <p className="text-base-content/70 text-sm py-4">No soft skills added yet.</p>
            )}
          </div>
        )}
      </div>
      
      {isOwnProfile && (
        <div className="mt-6 text-xs text-base-content/60">
          <p>
            Skills were identified based on your profile information. You can edit them anytime.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProfileSkillsSection; 