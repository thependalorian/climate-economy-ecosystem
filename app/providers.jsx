'use client';

import { AuthProvider } from '../hooks/useAuth';
import { ToastProvider } from '../components/ui/toast';

/**
 * Client Providers
 * Wraps all client-side providers in a single component
 * Location: /app/providers.jsx
 */
export default function Providers({ children }) {
  return (
    <AuthProvider>
      <ToastProvider>
        {children}
      </ToastProvider>
    </AuthProvider>
  );
} 