"use client";

import { useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import LoginForm from '../../../components/Auth/LoginForm';
import { Frame } from '../../../components/ui/Frame';
import { Heading, Text } from '../../../components/ui/Typography';

export default function SignIn() {
  const { data: session, status } = useSession();
  const router = useRouter();
  
  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (status === 'authenticated') {
      router.push('/dashboard');
    }
  }, [status, router]);
  
  if (status === 'loading') {
    return (
      <div className="flex justify-center items-center min-h-screen bg-sand-gray">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-spring-green"></div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-4 bg-sand-gray">
      <Frame 
        variant="default" 
        className="max-w-md w-full" 
        padding="large"
        showBrackets={true}
      >
        <Heading level={2} className="text-center mb-6">Sign In</Heading>
        <Text variant="large" className="text-center mb-8 max-w-md">
          Access your Massachusetts Clean Tech Ecosystem account to explore personalized clean energy opportunities.
        </Text>
        
        <LoginForm />
      </Frame>
    </div>
  );
}
