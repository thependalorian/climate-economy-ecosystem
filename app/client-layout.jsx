'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import MainLayout from '@/components/layout/MainLayout';

/**
 * Client Layout
 * Contains navigation and global UI elements requiring client-side interactivity
 * Location: /app/client-layout.jsx
 */
export default function ClientLayout({ children }) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [isInitialized, setIsInitialized] = useState(false);

  // Determine if this is the landing page (pathname === '/')
  const isLandingPage = pathname === '/';

  useEffect(() => {
    setIsInitialized(true);
  }, []);

  if (!isInitialized) {
    // Initial render - prevent hydration mismatch by not showing anything
    return <div style={{ visibility: 'hidden' }}>{children}</div>;
  }

  // For landing page, use the original layout
  if (isLandingPage) {
    return (
      <div className="min-h-screen flex flex-col">
        <main className="flex-grow">
          {children}
        </main>
      </div>
    );
  }

  // For all other pages, use the MainLayout
  return <MainLayout>{children}</MainLayout>;
}