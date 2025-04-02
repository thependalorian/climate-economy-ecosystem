"use client";

import { useSession, signOut } from 'next-auth/react';
import Link from 'next/link';
import { useState } from 'react';
import { FaUser, FaSignOutAlt, FaCog, FaClipboardList } from 'react-icons/fa';

export default function UserMenu() {
  const { data: session, status } = useSession();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleSignOut = () => {
    signOut({ callbackUrl: '/' });
  };

  if (status === 'loading') {
    return (
      <div className="animate-pulse">
        <div className="w-32 h-10 bg-base-300 rounded"></div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex space-x-2">
        <Link href="/auth/signin" className="btn btn-sm btn-outline">
          Sign In
        </Link>
        <Link href="/auth/signup" className="btn btn-sm btn-primary">
          Sign Up
        </Link>
      </div>
    );
  }

  return (
    <div className="dropdown dropdown-end">
      <div 
        tabIndex={0} 
        role="button" 
        className="btn btn-ghost flex items-center gap-2"
        onClick={toggleMenu}
      >
        {session.user.image ? (
          <img 
            src={session.user.image} 
            alt={session.user.name || 'User'} 
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="avatar placeholder">
            <div className="bg-primary text-neutral-content rounded-full w-8">
              <span>{session.user.name?.charAt(0) || session.user.email?.charAt(0) || 'U'}</span>
            </div>
          </div>
        )}
        <span className="hidden md:inline">{session.user.name || session.user.email}</span>
      </div>
      
      <ul 
        tabIndex={0} 
        className={`menu dropdown-content z-[1] p-2 shadow bg-base-100 rounded-box w-52 mt-4 ${isMenuOpen ? '' : 'hidden'}`}
      >
        <li>
          <Link href="/dashboard" className="flex items-center gap-2">
            <FaClipboardList /> Dashboard
          </Link>
        </li>
        <li>
          <Link href="/profile" className="flex items-center gap-2">
            <FaUser /> Profile
          </Link>
        </li>
        <li>
          <Link href="/settings" className="flex items-center gap-2">
            <FaCog /> Settings
          </Link>
        </li>
        <li>
          <button onClick={handleSignOut} className="flex items-center gap-2 text-error">
            <FaSignOutAlt /> Sign Out
          </button>
        </li>
      </ul>
    </div>
  );
} 