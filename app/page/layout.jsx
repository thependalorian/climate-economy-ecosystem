import { Inter } from 'next/font/google';
import { SessionProvider } from 'next-auth/react';
import { ToastProvider } from '../../components/ui/use-toast';
import { NotificationProvider } from '../../components/Notifications/NotificationProvider';
import { AuthProvider } from '../../hooks/useAuth';
import { Footer } from '../client-layout';

// Font configuration
const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap'
});

/**
 * Landing Page Layout
 * Special layout for the landing page that excludes the header
 * Location: /app/page/layout.jsx
 */
export default function LandingLayout({ children, session }) {
  return (
    <div className={`${inter.className}`} data-theme="light">
      <AuthProvider>
        <ToastProvider>
          <SessionProvider session={session}>
            <NotificationProvider>
              <div className="min-h-screen flex flex-col bg-seafoam-blue">
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