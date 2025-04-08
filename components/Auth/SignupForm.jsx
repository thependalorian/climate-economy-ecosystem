"use client";

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function SignupForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [location, setLocation] = useState('');
  const [isEJCommunity, setIsEJCommunity] = useState(false);
  const [isVeteran, setIsVeteran] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Validate password strength
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    try {
      // Create a user in Supabase Auth
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          email,
          password,
          location,
          is_ej_community: isEJCommunity,
          is_veteran: isVeteran,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Error creating account');
      }

      // Sign in the user
      const result = await signIn('credentials', {
        redirect: false,
        email,
        password,
      });

      if (result.error) {
        throw new Error('Failed to sign in after account creation');
      }

      // Redirect to onboarding or dashboard
      router.push('/onboarding');
    } catch (error) {
      console.error('Signup error:', error);
      setError(error.message || 'An unexpected error occurred');
      setLoading(false);
    }
  };

  const handleGoogleSignUp = () => {
    signIn('google', { callbackUrl: '/onboarding' });
  };

  return (
    <div className="w-full max-w-md bg-white shadow-xl rounded-lg p-6">
      <h2 className="text-2xl font-bold text-center mb-6">Create Your Account</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <span>{error}</span>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="form-control">
          <label className="label">
            <span className="label-text">Full Name</span>
          </label>
          <input
            type="text"
            placeholder="John Doe"
            className="input input-bordered w-full"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        
        <div className="form-control">
          <label className="label">
            <span className="label-text">Email</span>
          </label>
          <input
            type="email"
            placeholder="your@email.com"
            className="input input-bordered w-full"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div className="form-control">
          <label className="label">
            <span className="label-text">Password</span>
          </label>
          <input
            type="password"
            placeholder="********"
            className="input input-bordered w-full"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
          <label className="label">
            <span className="label-text-alt">Must be at least 8 characters</span>
          </label>
        </div>
        
        <div className="form-control">
          <label className="label">
            <span className="label-text">Location (City, State)</span>
          </label>
          <input
            type="text"
            placeholder="Boston, MA"
            className="input input-bordered w-full"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>
        
        <div className="form-control">
          <label className="label cursor-pointer justify-start gap-2">
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={isEJCommunity}
              onChange={(e) => setIsEJCommunity(e.target.checked)}
            />
            <span className="label-text">I live in an Environmental Justice community</span>
          </label>
        </div>
        
        <div className="form-control">
          <label className="label cursor-pointer justify-start gap-2">
            <input
              type="checkbox"
              className="checkbox checkbox-primary"
              checked={isVeteran}
              onChange={(e) => setIsVeteran(e.target.checked)}
            />
            <span className="label-text">I am a veteran or active military</span>
          </label>
        </div>
        
        <div className="form-control mt-6">
          <Button
            type="submit"
            variant="primary"
            className="w-full"
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </Button>
        </div>
      </form>
      
      <div className="relative flex py-5 items-center mt-4">
        <div className="flex-grow border-t border-gray-300"></div>
        <span className="flex-shrink mx-4 text-gray-600">OR</span>
        <div className="flex-grow border-t border-gray-300"></div>
      </div>
      
      <Button
        onClick={handleGoogleSignUp}
        variant="outline"
        className="w-full"
        disabled={loading}
      >
        <span className="mr-2">Sign up with Google</span>
      </Button>
      
      <div className="text-center mt-6">
        <p className="text-gray-600">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-blue-600 hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
} 