'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Frame } from '../../components/ui/Frame';
import { Heading, Text } from '../../components/ui/Typography';
import { Button } from '../../components/ui/Button';

/**
 * Login Page
 * Redirect to the proper auth/signin page and communicate changes to users
 * Location: /app/login/page.jsx
 */

export default function LegacyLoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the new auth/signin page after a brief delay
    const redirectTimeout = setTimeout(() => {
      router.push('/auth/signin');
    }, 3000);
    
    return () => clearTimeout(redirectTimeout);
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-seafoam-blue p-4">
      <Frame 
        variant="highlight" 
        showBrackets={true}
        className="w-full max-w-md"
        padding="large"
      >
        <Heading level={2} className="text-center mb-4">
          Redirecting to Sign In
        </Heading>
        
        <Text className="text-center mb-6">
          We've updated our authentication system. You'll be redirected to the new sign-in page in a few seconds.
        </Text>
        
        <div className="flex justify-center">
          <Button
            variant="primary"
            onClick={() => router.push('/auth/signin')}
          >
            Go to Sign In Now
          </Button>
        </div>
        
        <div className="flex justify-center mt-8">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-spring-green"></div>
        </div>
      </Frame>
    </div>
  );
} 