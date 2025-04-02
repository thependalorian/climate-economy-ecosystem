'use client';

import { Inter } from 'next/font/google';
import { SessionProvider } from 'next-auth/react';
import UserMenu from '../components/Auth/UserMenu';
import Link from 'next/link';
import { ToastProvider } from '../components/ui/use-toast';
import { NotificationProvider } from '../components/Notifications/NotificationProvider';
import Notifications from '../components/Notifications';
import { AuthProvider } from '../hooks/useAuth';

// Font configuration
const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap'
});

/**
 * Client Layout
 * Handles all client-side providers and layout using ACT brand guidelines
 * Location: /app/client-layout.jsx
 */
export default function ClientLayout({ children, session }) {
  return (
    <div className={`${inter.className}`} data-theme="light">
      <AuthProvider>
        <ToastProvider>
          <SessionProvider session={session}>
            <NotificationProvider>
              <div className="min-h-screen flex flex-col bg-seafoam-blue">
                <Header />
                <main className="flex-grow">
                  {children}
                </main>
                <Footer />
              </div>
            </NotificationProvider>
          </SessionProvider>
        </ToastProvider>
      </AuthProvider>
    </div>
  );
}

function Header() {
  return (
    <header className="bg-midnight-forest text-white shadow-md border-b-4 border-spring-green">
      <div className="container mx-auto px-6 flex items-center justify-between h-16">
        <div className="border-2 border-spring-green px-4 py-2 rounded-md bg-midnight-forest">
          <Link href="/" className="font-helvetica text-xl font-bold text-spring-green hover:text-accent transition-colors">
            Massachusetts Clean Tech
          </Link>
        </div>
        
        <nav className="hidden md:flex space-x-6">
          <Link href="/dashboard" className="text-white font-medium hover:text-spring-green transition-colors">
            Dashboard
          </Link>
          <Link href="/resume-upload" className="text-white font-medium hover:text-spring-green transition-colors">
            Resume Analysis
          </Link>
          <div className="relative group">
            <span className="text-white font-medium hover:text-spring-green transition-colors cursor-pointer">
              Opportunities
            </span>
            <div className="absolute z-10 left-0 mt-2 w-48 bg-midnight-forest rounded-md shadow-md hidden group-hover:block border border-spring-green">
              <Link href="/jobs" className="block px-4 py-2 text-white hover:bg-moss-green">
                Jobs
              </Link>
              <Link href="/training" className="block px-4 py-2 text-white hover:bg-moss-green">
                Training
              </Link>
            </div>
          </div>
          <Link href="/resources" className="text-white font-medium hover:text-spring-green transition-colors">
            Resources
          </Link>
          <Link href="/counselor" className="text-white font-medium hover:text-spring-green transition-colors">
            Career Counseling
          </Link>
        </nav>
        
        <div className="flex items-center space-x-4">
          <Notifications />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="bg-midnight-forest text-white py-10 border-t-4 border-spring-green">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h4 className="text-xl font-bold text-spring-green mb-4">Massachusetts Clean Tech</h4>
            <p className="text-seafoam-blue mb-4">
              Connecting job seekers with clean energy opportunities in Massachusetts.
            </p>
          </div>
          
          <div>
            <h5 className="text-lg font-bold text-spring-green mb-4">Quick Links</h5>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/jobs" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Find Jobs
                </Link>
              </li>
              <li>
                <Link href="/training" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Training Programs
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h5 className="text-lg font-bold text-spring-green mb-4">Resources</h5>
            <ul className="space-y-2">
              <li>
                <Link href="/resources/veterans" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Veterans
                </Link>
              </li>
              <li>
                <Link href="/resources/ej-communities" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  EJ Communities
                </Link>
              </li>
              <li>
                <Link href="/resources/international" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  International Professionals
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h5 className="text-lg font-bold text-spring-green mb-4">Legal</h5>
            <ul className="space-y-2">
              <li>
                <Link href="/privacy" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-seafoam-blue hover:text-spring-green transition-colors">
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-moss-green mt-8 pt-8 text-center">
          <p className="text-seafoam-blue">
            © {new Date().getFullYear()} Massachusetts Clean Tech Ecosystem | Powered by 
            <span className="font-semibold text-spring-green ml-1">
              Alliance for Climate Transition
            </span>
          </p>
        </div>
      </div>
    </footer>
  );
} 