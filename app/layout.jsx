import './globals.css';

// Metadata export for Next.js (must be at the server component level)
export const metadata = {
  title: 'Massachusetts Clean Energy Ecosystem',
  description: 'Connecting job seekers with clean energy opportunities in Massachusetts',
};

// Import the client components
import ClientLayout from './client-layout';
import Providers from './providers';

/**
 * Root Layout - Server Component
 * Provides the HTML structure and metadata
 */
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <ClientLayout>{children}</ClientLayout>
        </Providers>
      </body>
    </html>
  );
} 