'use client';

import { useSession, signIn, signOut } from 'next-auth/react';
import { useCallback } from 'react';
import { tracingService } from '@/lib/tracing/langsmith-client';

/**
 * useAuth Hook
 * 
 * A custom React hook that provides authentication functionality
 * using NextAuth.js. Includes tracing for monitoring and debugging.
 * 
 * @returns {Object} Object containing auth state and methods
 */
export function useAuth() {
  const { data: session, status } = useSession();
  
  /**
   * Login function
   * 
   * @param {string} provider - The authentication provider to use
   * @returns {Promise} Promise that resolves when login is complete
   */
  const login = useCallback(async (provider = 'google') => {
    try {
      // Track login attempt
      const runId = tracingService.createRunId();
      tracingService.logLlmCall(
        'auth',
        'login_attempt',
        provider,
        runId,
        { auth_action: 'login_attempt' }
      );
      
      // Perform login
      await signIn(provider);
      
      // Track successful login
      tracingService.logLlmCall(
        'auth',
        'login_success',
        provider,
        runId,
        { auth_action: 'login_success' }
      );
    } catch (error) {
      console.error('Login error:', error);
      
      // Track login error
      tracingService.logLlmCall(
        'auth',
        'login_error',
        error.message,
        null,
        { auth_action: 'login_error' }
      );
      
      throw error;
    }
  }, []);
  
  /**
   * Logout function
   * 
   * @returns {Promise} Promise that resolves when logout is complete
   */
  const logout = useCallback(async () => {
    try {
      // Track logout
      tracingService.logLlmCall(
        'auth',
        'logout',
        '',
        null,
        { auth_action: 'logout' }
      );
      
      // Perform logout
      await signOut();
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }, []);
  
  return {
    session,
    status,
    isAuthenticated: status === 'authenticated',
    isLoading: status === 'loading',
    user: session?.user,
    login,
    logout
  };
}

/**
 * AuthProvider component
 * 
 * This is a placeholder component for backward compatibility.
 * In a NextAuth.js app, you should use SessionProvider from next-auth/react.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {React.ReactNode} The wrapped children
 */
export function AuthProvider({ children }) {
  return children;
}
