/**
 * OnboardingLayout Component
 * 
 * A layout wrapper for onboarding pages that provides consistent styling
 * and navigation options across the entire onboarding flow.
 */
'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowLeft } from 'lucide-react';

const OnboardingLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with logo only */}
      <header className="bg-white border-b border-gray-200 py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-2">
            <Image
              src="/images/act-logo.png"
              alt="ACT Logo"
              width={40}
              height={40}
            />
            <span className="text-xl font-bold text-midnight-forest">Climate Economy Ecosystem</span>
          </Link>
          
          <Link 
            href="/" 
            className="text-gray-600 hover:text-midnight-forest flex items-center text-sm"
          >
            <ArrowLeft size={16} className="mr-1" />
            Back to Home
          </Link>
        </div>
      </header>
      
      {/* Main content area */}
      <main className="container mx-auto py-8 px-4">
        {children}
      </main>
      
      {/* Simple footer */}
      <footer className="bg-white border-t border-gray-200 py-6 mt-auto">
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
};

export default OnboardingLayout; 