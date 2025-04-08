'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import ProfileEnrichment from '../../../components/ProfileEnrichment';
import MainLayout from '@/components/layout/MainLayout';

/**
 * Profile Enrichment Page
 *
 * Allows users to enhance their profile with skills extracted from their
 * education, experience, and social profiles
 */
export default function EnrichProfilePage() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = createClientComponentClient();

  // Get the current user's ID
  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);

        const { data: { session }, error } = await supabase.auth.getSession();

        if (error) throw error;

        if (!session) {
          // Redirect to login if no session
          router.push('/login');
          return;
        }

        setUserId(session.user.id);
      } catch (error) {
        console.error('Error fetching user session:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router, supabase]);

  // Handle completion of profile enrichment
  const handleComplete = () => {
    router.push('/profile');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Enhance Your Profile</h1>
          <p className="text-base-content/70">
            Unlock better job matches by enriching your profile with relevant skills.
          </p>
        </div>

        {userId && <ProfileEnrichment userId={userId} onComplete={handleComplete} />}
      </div>
    </MainLayout>
  );
}