'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { 
  MessageSquare, 
  User, 
  FileText, 
  BarChart, 
  LogOut,
  LogIn
} from 'lucide-react';

/**
 * Main Layout Component
 * 
 * Provides consistent layout with navigation for all pages
 */
const MainLayout = ({ children }) => {
  const { user, signOut } = useAuth();
  
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <Link href="/" className="flex items-center space-x-2">
            <Image
              src="/images/act-logo.png"
              alt="Climate Economy Ecosystem"
              width={40}
              height={40}
            />
            <span className="text-xl font-bold text-midnight-forest">Climate Economy Ecosystem</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-600 hidden md:inline">
                  {user.email}
                </span>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={signOut}
                  className="text-gray-600"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  <span className="hidden md:inline">Sign Out</span>
                </Button>
              </>
            ) : (
              <Button variant="outline" size="sm" asChild>
                <Link href="/auth/signin">
                  <LogIn className="h-4 w-4 mr-2" />
                  Sign In
                </Link>
              </Button>
            )}
          </div>
        </div>
      </header>
      
      {/* Main content with sidebar */}
      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-16 md:w-64 bg-white border-r border-gray-200 shrink-0">
          <nav className="p-4 space-y-2">
            <Button variant="ghost" className="w-full justify-start" asChild>
              <Link href="/assistant/chat">
                <MessageSquare className="h-5 w-5 mr-2" />
                <span className="hidden md:inline">Chat</span>
              </Link>
            </Button>
            
            <Button variant="ghost" className="w-full justify-start" asChild>
              <Link href="/profile">
                <User className="h-5 w-5 mr-2" />
                <span className="hidden md:inline">Profile</span>
              </Link>
            </Button>
            
            <Button variant="ghost" className="w-full justify-start" asChild>
              <Link href="/profile/resume">
                <FileText className="h-5 w-5 mr-2" />
                <span className="hidden md:inline">Resume Upload</span>
              </Link>
            </Button>
            
            {user && user.role === 'admin' && (
              <Button variant="ghost" className="w-full justify-start" asChild>
                <Link href="/admin/metrics">
                  <BarChart className="h-5 w-5 mr-2" />
                  <span className="hidden md:inline">Metrics Dashboard</span>
                </Link>
              </Button>
            )}
          </nav>
        </aside>
        
        {/* Main content */}
        <main className="flex-1 p-4 md:p-8">
          {children}
        </main>
      </div>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} Alliance for Climate Transition. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
