'use client';

import AdminMetricsDashboard from '../../../components/AdminMetricsDashboard';
import MainLayout from '@/components/layout/MainLayout';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

/**
 * Admin Metrics Page
 *
 * Displays metrics dashboard for profile enrichment and job search analytics
 */
export default function AdminMetricsPage() {
  const { user } = useAuth();
  const router = useRouter();

  // Check if user is admin
  useEffect(() => {
    if (user && user.role !== 'admin') {
      router.push('/assistant/chat');
    } else if (!user) {
      router.push('/auth/signin');
    }
  }, [user, router]);

  if (!user || user.role !== 'admin') {
    return null;
  }

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Admin Metrics Dashboard</h1>
        <p className="mb-6">
          Track user engagement and performance metrics for profile enrichment and job search features.
        </p>

        <AdminMetricsDashboard />
      </div>
    </MainLayout>
  );
}