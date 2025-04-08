'use client';

import { AuthProvider } from '../hooks/useAuth';
import { ToastProvider } from '../components/ui/toast';
import { SessionProvider } from 'next-auth/react';

/**
 * Client Providers
 * Wraps all client-side providers in a single component
 * Location: /app/providers.jsx
 */
export default function Providers({ children }) {
  return (
    <SessionProvider>
      <AuthProvider>
        <ToastProvider>
          {children}
        </ToastProvider>
      </AuthProvider>
    </SessionProvider>
  );
}