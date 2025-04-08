'use client';

import { Suspense } from 'react';
import EnhancedChatInterface from '@/components/Chat/EnhancedChatInterface';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export const metadata = {
  title: 'Chat | Climate Economy Ecosystem',
  description: 'Chat with our AI assistant about clean energy careers, training, and resources in Massachusetts.',
};

// Loading component
function ChatLoading() {
  return (
    <Card className="flex items-center justify-center h-[calc(100vh-6rem)] max-w-4xl mx-auto">
      <div className="flex flex-col items-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading chat interface...</p>
      </div>
    </Card>
  );
}

export default function ChatPage() {
  return (
    <div className="container py-6">
      <h1 className="text-3xl font-bold mb-6">Climate Economy Assistant</h1>
      <p className="text-muted-foreground mb-6">
        Chat with our AI assistant about clean energy careers, training programs, and resources in Massachusetts.
        You can also upload your resume for personalized recommendations.
      </p>
      
      <Suspense fallback={<ChatLoading />}>
        <EnhancedChatInterface />
      </Suspense>
    </div>
  );
}
