'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { FileText, Edit, Upload } from 'lucide-react';
import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';

/**
 * User Profile Page
 * 
 * Displays user profile information and provides links to profile-related actions
 */
export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = createClientComponentClient();
  
  // Fetch user profile data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError) throw sessionError;
        
        if (!session) {
          router.push('/auth/signin');
          return;
        }
        
        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single();
        
        if (error) throw error;
        
        setProfile(data);
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProfile();
  }, [router, supabase]);
  
  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      </MainLayout>
    );
  }
  
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Your Profile</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Profile Summary */}
          <div className="md:col-span-2">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Profile Summary</h2>
              
              {profile ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Name</h3>
                    <p className="text-lg">{profile.full_name || 'Not provided'}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Email</h3>
                    <p className="text-lg">{profile.email || 'Not provided'}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Location</h3>
                    <p className="text-lg">{profile.location || 'Not provided'}</p>
                  </div>
                  
                  {profile.is_veteran && (
                    <div>
                      <Badge variant="secondary">Military Veteran</Badge>
                    </div>
                  )}
                  
                  {profile.is_ej_community && (
                    <div>
                      <Badge variant="secondary">Environmental Justice Community</Badge>
                    </div>
                  )}
                  
                  {profile.is_international && (
                    <div>
                      <Badge variant="secondary">International Professional</Badge>
                    </div>
                  )}
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Profile Completeness</h3>
                    <div className="mt-2">
                      <Progress value={calculateProfileCompleteness(profile)} className="h-2" />
                      <p className="text-sm text-gray-500 mt-1">
                        {calculateProfileCompleteness(profile)}% complete
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-gray-500">
                  No profile information available. Please complete your profile.
                </div>
              )}
              
              <div className="mt-6">
                <Button asChild>
                  <Link href="/onboarding">
                    <Edit className="h-4 w-4 mr-2" />
                    {profile ? 'Update Profile' : 'Complete Profile'}
                  </Link>
                </Button>
              </div>
            </Card>
          </div>
          
          {/* Actions */}
          <div className="md:col-span-1">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Actions</h2>
              
              <div className="space-y-4">
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/profile/resume">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Resume
                  </Link>
                </Button>
                
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/profile/enrich">
                    <FileText className="h-4 w-4 mr-2" />
                    Enrich Profile
                  </Link>
                </Button>
                
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link href="/assistant/chat">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Chat with Assistant
                  </Link>
                </Button>
              </div>
            </Card>
          </div>
          
          {/* Skills Section */}
          {profile && profile.skills && profile.skills.length > 0 && (
            <div className="md:col-span-3">
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Your Skills</h2>
                
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map((skill, index) => (
                    <Badge key={index} variant="outline">
                      {skill}
                    </Badge>
                  ))}
                </div>
                
                <div className="mt-4">
                  <Button variant="outline" size="sm" asChild>
                    <Link href="/profile/enrich">
                      Enhance Skills
                    </Link>
                  </Button>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}

// Helper function to calculate profile completeness
function calculateProfileCompleteness(profile) {
  if (!profile) return 0;
  
  const fields = [
    'full_name',
    'email',
    'location',
    'skills',
    'interests',
    'background'
  ];
  
  let completedFields = 0;
  
  fields.forEach(field => {
    if (profile[field]) {
      if (Array.isArray(profile[field])) {
        if (profile[field].length > 0) completedFields++;
      } else {
        if (profile[field].trim() !== '') completedFields++;
      }
    }
  });
  
  return Math.round((completedFields / fields.length) * 100);
}
