"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, Eye, EyeOff } from 'lucide-react';
import SignupForm from '@/components/SignupForm';
import Image from 'next/image';

/**
 * Signup Page Component
 * Collects basic registration information before redirecting to onboarding
 * 
 * Location: /app/auth/signup/page.jsx
 */
export default function Signup() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <div className="container mx-auto px-4 py-8 flex-1 flex flex-col items-center justify-center">
        <Link href="/" className="mb-8 flex items-center">
          <Image 
            src="/images/act-logo.png"
            alt="ACT Logo"
            width={48}
            height={48}
          />
          <span className="ml-2 text-xl font-bold text-midnight-forest">Climate Economy Ecosystem</span>
        </Link>
        
        <div className="w-full max-w-md">
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-8">
              <div className="text-center mb-8">
                <h1 className="text-2xl font-bold text-midnight-forest mb-2">Create Your Account</h1>
                <p className="text-gray-600">Join the Massachusetts clean energy community</p>
              </div>
              
              <SignupForm redirectUrl="/onboarding" />
              
              <div className="mt-6 text-center text-sm text-gray-600">
                <p>Already have an account? <Link href="/auth/signin" className="text-spring-green hover:underline">Sign In</Link></p>
              </div>
            </div>
          </div>
          
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600">
              By signing up, you agree to our{' '}
              <Link href="/terms" className="text-spring-green hover:underline">Terms of Service</Link>{' '}
              and{' '}
              <Link href="/privacy" className="text-spring-green hover:underline">Privacy Policy</Link>.
            </p>
          </div>
        </div>
      </div>
      
      <footer className="mt-auto bg-white border-t border-gray-200 py-6">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-sm text-gray-500 mb-4 md:mb-0">
              © {new Date().getFullYear()} Alliance for Climate Transition. All rights reserved.
            </div>
            
            <div className="flex space-x-6">
              <Link href="/privacy" className="text-sm text-gray-500 hover:text-midnight-forest">
                Privacy Policy
              </Link>
              <Link href="/terms" className="text-sm text-gray-500 hover:text-midnight-forest">
                Terms of Service
              </Link>
              <Link href="/contact" className="text-sm text-gray-500 hover:text-midnight-forest">
                Contact Us
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
