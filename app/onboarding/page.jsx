"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { ChevronLeft, ChevronRight, Users, GraduationCap, Globe, MapPin, Briefcase, ArrowRight, Check } from 'lucide-react';

// Importing onboarding components
import StepProgress from '@/components/Onboarding/StepProgress';
import Question from '@/components/Onboarding/Question';
import SelectableCard from '@/components/Onboarding/SelectableCard';
import OnboardingLayout from '@/components/Onboarding/OnboardingLayout';

/**
 * Onboarding Page Component
 * Implements a strategic 5-step onboarding process to collect information about users
 * to personalize their experience with the Climate Economy Assistant
 * 
 * Location: /app/onboarding/page.jsx
 */
export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    background: '',
    skills: [],
    interests: [],
    location: '',
    otherInfo: '',
    persona: ''
  });

  const totalSteps = 5;

  // Step content definitions
  const steps = [
    {
      id: 1,
      title: "Tell us about your background",
      description: "This helps us identify opportunities that match your experience",
      component: (
        <div className="space-y-6">
          <p className="text-gray-600 mb-4">Which option best describes your current situation?</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SelectableCard
              selected={formData.persona === 'veteran'}
              onClick={() => handlePersonaSelect('veteran')}
              icon={<Users size={24} className="text-spring-green" />}
              title="Military Veteran"
              description="Transitioning from military service to civilian clean energy career"
            />
            
            <SelectableCard
              selected={formData.persona === 'international'}
              onClick={() => handlePersonaSelect('international')}
              icon={<Globe size={24} className="text-spring-green" />}
              title="International Professional"
              description="Professional with international background or training"
            />
            
            <SelectableCard
              selected={formData.persona === 'student'}
              onClick={() => handlePersonaSelect('student')}
              icon={<GraduationCap size={24} className="text-spring-green" />}
              title="Student"
              description="Current student at vocational, community college, or university"
            />
            
            <SelectableCard
              selected={formData.persona === 'ej'}
              onClick={() => handlePersonaSelect('ej')}
              icon={<MapPin size={24} className="text-spring-green" />}
              title="Environmental Justice Community"
              description="Resident of an Environmental Justice community"
            />
            
            <SelectableCard
              selected={formData.persona === 'reentry'}
              onClick={() => handlePersonaSelect('reentry')}
              icon={<Briefcase size={24} className="text-spring-green" />}
              title="Workforce Reentry"
              description="Returning to the workforce after a career gap"
            />
            
            <SelectableCard
              selected={formData.persona === 'other'}
              onClick={() => handlePersonaSelect('other')}
              icon={<Check size={24} className="text-spring-green" />}
              title="Other"
              description="My situation is different from the options above"
            />
          </div>
          
          {formData.persona && (
            <div className="mt-6">
              <Question
                type="textarea"
                label="Tell us more about your background (optional)"
                placeholder="Share any relevant details about your work history, education, or experience..."
                value={formData.background}
                onChange={(value) => setFormData({...formData, background: value})}
              />
            </div>
          )}
        </div>
      )
    },
    {
      id: 2,
      title: "What skills do you bring?",
      description: "Select all that apply to your experience",
      component: (
        <div className="space-y-6">
          <p className="text-gray-600 mb-4">Select skills you have experience with (select all that apply)</p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {[
              'Project Management',
              'Technical Writing',
              'Electrical Work',
              'Customer Service',
              'Computer Programming',
              'Data Analysis',
              'Teaching/Training',
              'Construction',
              'Engineering',
              'Mechanical Skills',
              'Sales',
              'Research',
              'Community Organizing',
              'Administrative',
              'Manufacturing',
              'Leadership',
              'CDL License',
              'Logistics'
            ].map((skill) => (
              <button
                key={skill}
                className={`px-4 py-3 border rounded-lg text-left transition-colors ${
                  formData.skills.includes(skill)
                    ? 'bg-spring-green text-midnight-forest border-spring-green'
                    : 'bg-white border-gray-300 hover:border-spring-green'
                }`}
                onClick={() => handleSkillToggle(skill)}
              >
                {skill}
              </button>
            ))}
          </div>
          
          <Question
            type="text"
            label="Other skills (optional)"
            placeholder="Enter any other skills you have..."
            value={formData.otherSkills || ''}
            onChange={(value) => setFormData({...formData, otherSkills: value})}
          />
        </div>
      )
    },
    {
      id: 3,
      title: "What are you interested in?",
      description: "Select areas of the clean energy economy that interest you",
      component: (
        <div className="space-y-6">
          <p className="text-gray-600 mb-4">Select clean energy sectors you're interested in (select all that apply)</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'Solar Energy', image: '/images/interests/solar.jpg' },
              { name: 'Wind Energy', image: '/images/interests/wind.jpg' },
              { name: 'Energy Efficiency', image: '/images/interests/efficiency.jpg' },
              { name: 'Electric Vehicles', image: '/images/interests/ev.jpg' },
              { name: 'Battery Storage', image: '/images/interests/battery.jpg' },
              { name: 'Green Buildings', image: '/images/interests/buildings.jpg' },
              { name: 'Climate Policy', image: '/images/interests/policy.jpg' },
              { name: 'Environmental Justice', image: '/images/interests/justice.jpg' }
            ].map((interest) => (
              <div 
                key={interest.name} 
                className={`relative rounded-lg overflow-hidden cursor-pointer border-2 transition-all ${
                  formData.interests.includes(interest.name)
                    ? 'border-spring-green shadow-md'
                    : 'border-transparent hover:border-gray-300'
                }`}
                onClick={() => handleInterestToggle(interest.name)}
              >
                <div className="h-40 relative">
                  <Image
                    src={interest.image}
                    alt={interest.name}
                    layout="fill"
                    objectFit="cover"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                    <h3 className="text-white text-xl font-bold">{interest.name}</h3>
                  </div>
                  
                  {formData.interests.includes(interest.name) && (
                    <div className="absolute top-2 right-2 bg-spring-green rounded-full p-1">
                      <Check size={16} className="text-midnight-forest" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: 4,
      title: "Location preferences",
      description: "Tell us where you'd like to work in Massachusetts",
      component: (
        <div className="space-y-6">
          <p className="text-gray-600 mb-4">Please select your preferred location(s)</p>
          
          <div className="relative h-96 rounded-lg overflow-hidden mb-6">
            <Image
              src="/images/ma-map.jpg"
              alt="Massachusetts Map"
              layout="fill"
              objectFit="cover"
            />
            <div className="absolute inset-0 bg-midnight-forest bg-opacity-30 pointer-events-none"></div>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {[
              'Greater Boston',
              'Northeast MA',
              'Southeast MA',
              'Central MA',
              'Western MA',
              'Cape & Islands',
              'Remote Only',
              'Any Location'
            ].map((location) => (
              <button
                key={location}
                className={`px-4 py-2 border rounded-lg text-center transition-colors ${
                  formData.location === location
                    ? 'bg-spring-green text-midnight-forest border-spring-green'
                    : 'bg-white border-gray-300 hover:border-spring-green'
                }`}
                onClick={() => setFormData({...formData, location})}
              >
                {location}
              </button>
            ))}
          </div>
          
          <Question
            type="checkbox"
            label="I'm willing to relocate within Massachusetts for the right opportunity"
            checked={formData.willRelocate || false}
            onChange={(checked) => setFormData({...formData, willRelocate: checked})}
          />
          
          <Question
            type="checkbox"
            label="I'm located in an Environmental Justice community"
            checked={formData.inEJCommunity || false}
            onChange={(checked) => setFormData({...formData, inEJCommunity: checked})}
          />
        </div>
      )
    },
    {
      id: 5,
      title: "Almost done!",
      description: "Review your information and confirm your preferences",
      component: (
        <div className="space-y-6">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-lg font-medium mb-4">Your Onboarding Summary</h3>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Background</p>
                  <p className="font-medium">{getPersonaLabel(formData.persona)}</p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500">Location Preference</p>
                  <p className="font-medium">{formData.location || "Not specified"}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-500">Selected Skills</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {formData.skills.length > 0 ? formData.skills.map((skill) => (
                    <span key={skill} className="bg-gray-100 px-2 py-1 rounded text-sm">
                      {skill}
                    </span>
                  )) : <span className="text-gray-400">No skills selected</span>}
                </div>
              </div>
              
              <div>
                <p className="text-sm text-gray-500">Interests</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {formData.interests.length > 0 ? formData.interests.map((interest) => (
                    <span key={interest} className="bg-gray-100 px-2 py-1 rounded text-sm">
                      {interest}
                    </span>
                  )) : <span className="text-gray-400">No interests selected</span>}
                </div>
              </div>
            </div>
          </div>
          
          <div className="border-t pt-6">
            <Question
              type="checkbox"
              label="I agree to share my information to receive personalized job and training recommendations"
              checked={formData.consentToShare || false}
              onChange={(checked) => setFormData({...formData, consentToShare: checked})}
            />
            
            <Question
              type="checkbox"
              label="I'd like to receive email updates about new opportunities (optional)"
              checked={formData.consentToEmail || false}
              onChange={(checked) => setFormData({...formData, consentToEmail: checked})}
            />
          </div>
        </div>
      )
    }
  ];

  // Helper to get the persona label
  function getPersonaLabel(persona) {
    switch(persona) {
      case 'veteran': return 'Military Veteran';
      case 'international': return 'International Professional';
      case 'student': return 'Student';
      case 'ej': return 'Environmental Justice Community';
      case 'reentry': return 'Workforce Reentry';
      case 'other': return 'Other';
      default: return 'Not specified';
    }
  }

  // Handler for persona selection
  const handlePersonaSelect = (persona) => {
    setFormData({...formData, persona});
  };

  // Handler for skill selection
  const handleSkillToggle = (skill) => {
    if (formData.skills.includes(skill)) {
      setFormData({
        ...formData,
        skills: formData.skills.filter(s => s !== skill)
      });
    } else {
      setFormData({
        ...formData,
        skills: [...formData.skills, skill]
      });
    }
  };

  // Handler for interest selection
  const handleInterestToggle = (interest) => {
    if (formData.interests.includes(interest)) {
      setFormData({
        ...formData,
        interests: formData.interests.filter(i => i !== interest)
      });
    } else {
      setFormData({
        ...formData,
        interests: [...formData.interests, interest]
      });
    }
  };

  // Navigate to the next step
  const handleNext = async () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
      window.scrollTo(0, 0);
    } else {
      try {
        // Submit onboarding data to Supabase
        const response = await fetch('/api/onboarding', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          throw new Error('Failed to submit onboarding data');
        }

        // Redirect to dashboard on success
        router.push('/dashboard');
      } catch (error) {
        console.error('Error submitting onboarding data:', error);
        // You might want to show an error message to the user here
      }
    }
  };

  // Navigate to the previous step
  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo(0, 0);
    } else {
      router.push('/');
    }
  };

  // Get current step data
  const currentStepData = steps.find(step => step.id === currentStep);
  
  // Determine if the current step is complete
  const isCurrentStepComplete = () => {
    switch(currentStep) {
      case 1:
        return !!formData.persona;
      case 2:
        return formData.skills.length > 0;
      case 3:
        return formData.interests.length > 0;
      case 4:
        return !!formData.location;
      case 5:
        return formData.consentToShare;
      default:
        return false;
    }
  };

  return (
    <OnboardingLayout>
      <div className="max-w-4xl mx-auto mt-8 mb-16 p-6 bg-white rounded-lg shadow-lg">
        <div className="mb-10">
          <StepProgress currentStep={currentStep} totalSteps={totalSteps} />
        </div>
        
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-midnight-forest mb-2">
            {currentStepData.title}
          </h2>
          <p className="text-gray-600">
            {currentStepData.description}
          </p>
        </div>
        
        <div className="mb-10">
          {currentStepData.component}
        </div>
        
        <div className="flex justify-between">
          <button
            onClick={handlePrevious}
            className="btn btn-outline border-gray-300 hover:bg-gray-100 hover:border-gray-400"
          >
            <ChevronLeft size={16} className="mr-2" />
            {currentStep === 1 ? 'Back to Home' : 'Previous'}
          </button>
          
          <button
            onClick={handleNext}
            disabled={!isCurrentStepComplete()}
            className={`btn btn-primary group ${!isCurrentStepComplete() ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            {currentStep === totalSteps ? (
              <>Finish & Go to Dashboard</>
            ) : (
              <>Next <ChevronRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" /></>
            )}
          </button>
        </div>
      </div>
    </OnboardingLayout>
  );
} 