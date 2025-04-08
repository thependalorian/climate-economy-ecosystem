'use client';

import { Suspense } from 'react';
import ClimateAssistant from '@/components/Climate/ClimateAssistant';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export const metadata = {
  title: 'Massachusetts Climate Assistant | Climate Economy Ecosystem',
  description: 'Get specialized information about the Massachusetts clean energy economy, careers, and resources.',
};

// Loading component
function ClimateAssistantLoading() {
  return (
    <Card className="flex items-center justify-center h-[calc(100vh-6rem)] max-w-4xl mx-auto">
      <div className="flex flex-col items-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading Massachusetts Climate Assistant...</p>
      </div>
    </Card>
  );
}

export default function ClimatePage() {
  return (
    <div className="container py-6">
      <h1 className="text-3xl font-bold mb-6">Massachusetts Climate Economy Assistant</h1>
      <p className="text-muted-foreground mb-6">
        Get specialized information about clean energy careers, training programs, and resources in Massachusetts.
        This assistant is trained on Massachusetts-specific climate economy reports and data.
      </p>
      
      <Suspense fallback={<ClimateAssistantLoading />}>
        <ClimateAssistant />
      </Suspense>
    </div>
  );
}
