'use client';

import { useState, useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useRouter } from 'next/navigation';
import EnhancedJobSearch from '../../../components/EnhancedJobSearch';

/**
 * Enhanced Job Search Page
 * 
 * Provides an advanced job search experience that leverages user profile enrichment
 * data to deliver more relevant job matches and recommendations
 */
export default function EnhancedJobSearchPage() {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasEnrichment, setHasEnrichment] = useState(false);
  const router = useRouter();
  const supabase = createClientComponentClient();
  
  // Check authentication and get user profile
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setLoading(true);
        
        // Check if user is logged in
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) throw error;
        
        if (!session) {
          // Redirect to login if no session
          router.push('/login?redirect=/jobs/enhanced-search');
          return;
        }
        
        setUserId(session.user.id);
        
        // Check if user has an enriched profile
        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('enrichment')
          .eq('id', session.user.id)
          .single();
          
        if (profileError) {
          console.error('Error fetching profile:', profileError);
        } else if (profile && profile.enrichment && profile.enrichment.status === 'completed') {
          setHasEnrichment(true);
        }
      } catch (error) {
        console.error('Error checking auth:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, [router, supabase]);
  
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Job Search</h1>
        <p className="text-base-content/70">
          Find the perfect climate career opportunity that matches your skills and interests.
        </p>
      </div>
      
      {!hasEnrichment && (
        <div className="alert alert-info mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <span className="font-bold">Want better job matches?</span> Take a moment to enrich your profile
            for more personalized job recommendations.
            <button 
              className="btn btn-primary btn-sm ml-4"
              onClick={() => router.push('/profile/enrich')}
            >
              Enrich Profile
            </button>
          </div>
        </div>
      )}
      
      {userId && <EnhancedJobSearch userId={userId} />}
    </div>
  );
} 