"use client";

import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ClimateChat from '../../components/ClimateChat';
import { Calendar, Users, FileText, ChevronRight } from 'lucide-react';

/**
 * Counselor Page
 * Provides career counseling resources and scheduling following ACT brand guidelines
 * Location: /app/counselor/page.jsx
 */
export default function CounselorPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState(null);
  
  // Redirect if not authenticated
  if (!isLoading && !user) {
    router.push('/login?redirect=/counselor');
    return null;
  }
  
  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-spring-green border-t-transparent"></div>
        <p className="ml-3 text-moss-green font-medium">Loading...</p>
      </div>
    );
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">
        Career Counseling Services
      </h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {/* Career Counseling Information */}
          <div className="card bg-base-100 border-2 border-spring-green mb-8">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">Schedule a Career Consultation</h2>
              <p className="mb-6">
                Our career counselors specialize in helping job seekers navigate the clean energy economy. 
                Whether you're transitioning from another field, looking to translate military experience, 
                or starting your career, our counselors can provide personalized guidance.
              </p>
              
              {/* Calendly Integration */}
              <div className="bg-accent p-6 rounded-lg mb-6">
                <h3 className="text-xl font-bold mb-2">Available Appointment Times</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-4">
                  {["Mon, Apr 5 - 10:00 AM", "Mon, Apr 5 - 2:00 PM", "Tue, Apr 6 - 11:00 AM", 
                    "Wed, Apr 7 - 1:00 PM", "Thu, Apr 8 - 3:00 PM", "Fri, Apr 9 - 9:00 AM"].map((slot, index) => (
                    <button
                      key={index}
                      className={`p-2 rounded text-sm text-center transition-colors ${
                        selectedDate === slot
                          ? 'bg-spring-green text-midnight-forest font-medium'
                          : 'bg-base-100 hover:bg-spring-green/20 text-midnight-forest border border-moss-green/20'
                      }`}
                      onClick={() => setSelectedDate(slot)}
                    >
                      {slot}
                    </button>
                  ))}
                </div>
                
                <div className="mt-6 flex justify-end">
                  <button
                    className="btn btn-primary"
                    disabled={!selectedDate}
                    onClick={() => alert(`Appointment scheduled for ${selectedDate}`)}
                  >
                    Schedule Appointment
                  </button>
                </div>
              </div>
              
              {/* Counselor Team */}
              <div>
                <h3 className="text-xl font-bold mb-4">Our Career Counselors</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-base-300 p-4 rounded-lg flex items-center">
                    <div className="w-16 h-16 bg-moss-green/20 rounded-full flex items-center justify-center mr-4">
                      <Users size={28} className="text-moss-green" />
                    </div>
                    <div>
                      <h4 className="font-bold">Sarah Johnson</h4>
                      <p className="text-sm text-moss-green">Clean Energy Transition Specialist</p>
                    </div>
                  </div>
                  
                  <div className="bg-base-300 p-4 rounded-lg flex items-center">
                    <div className="w-16 h-16 bg-moss-green/20 rounded-full flex items-center justify-center mr-4">
                      <Users size={28} className="text-moss-green" />
                    </div>
                    <div>
                      <h4 className="font-bold">Michael Chen</h4>
                      <p className="text-sm text-moss-green">Technical Skills Counselor</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Resources Section */}
          <div className="card bg-base-100 border-2 border-spring-green mb-8">
            <div className="card-body">
              <h2 className="card-title text-2xl mb-4">Counseling Resources</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ResourceCard 
                  title="Resume Review Guidelines" 
                  description="Tips for optimizing your resume for clean energy employers."
                  icon={<FileText size={24} className="text-moss-green" />}
                  link="/resources/resume-guide"
                />
                
                <ResourceCard 
                  title="Interview Preparation" 
                  description="Common questions and preparation tips for the industry."
                  icon={<Calendar size={24} className="text-moss-green" />}
                  link="/resources/interview-prep"
                />
                
                <ResourceCard 
                  title="Skills Assessment" 
                  description="Identify your transferable skills for clean energy careers."
                  icon={<Users size={24} className="text-moss-green" />}
                  link="/skills-assessment"
                />
                
                <ResourceCard 
                  title="Industry Trends" 
                  description="Latest developments in the Massachusetts clean energy sector."
                  icon={<FileText size={24} className="text-moss-green" />}
                  link="/resources/industry-trends"
                />
              </div>
            </div>
          </div>
        </div>
        
        {/* AI Assistant */}
        <div className="lg:col-span-1">
          <ClimateChat />
        </div>
      </div>
    </div>
  );
}

function ResourceCard({ title, description, icon, link }) {
  const router = useRouter();
  
  return (
    <div 
      className="border border-spring-green/20 bg-base-100 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => router.push(link)}
    >
      <div className="flex items-start">
        <div className="p-2 bg-spring-green/10 rounded-full mr-3">
          {icon}
        </div>
        <div className="flex-1">
          <h4 className="font-bold mb-1">{title}</h4>
          <p className="text-sm">{description}</p>
        </div>
        <ChevronRight size={18} className="text-moss-green self-center" />
      </div>
    </div>
  );
}
