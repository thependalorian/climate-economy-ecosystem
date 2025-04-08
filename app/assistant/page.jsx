'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, MessageSquare, Upload, Briefcase } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import ResumeUpload from '@/components/Assistant/ResumeUpload';
import ChatInterface from '@/components/Assistant/ChatInterface';

/**
 * Climate Assistant Page
 * Combines AI assistant, resume analysis, and career tools
 * Location: /app/assistant/page.jsx
 */
export default function ClimateAssistant() {
  const [activeTab, setActiveTab] = useState('chat');
  const { toast } = useToast();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-midnight-forest mb-6">
          Climate Economy Assistant
        </h1>
        
        <Card className="p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid grid-cols-2 gap-4 mb-6">
              <TabsTrigger value="chat" className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Chat Assistant
              </TabsTrigger>
              <TabsTrigger value="resume" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Resume Analysis
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="chat">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-midnight-forest mb-2">
                  Chat with your Climate Economy Assistant
                </h2>
                <p className="text-moss-green mb-4">
                  Get personalized guidance on clean energy careers, training programs, and opportunities.
                </p>
                <ChatInterface />
              </div>
            </TabsContent>
            
            <TabsContent value="resume">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-midnight-forest mb-2">
                  Resume Analysis
                </h2>
                <p className="text-moss-green mb-4">
                  Upload your resume to get personalized recommendations for clean energy roles and skills alignment.
                </p>
                <ResumeUpload />
              </div>
            </TabsContent>
          </Tabs>
        </Card>
        
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
          <Card className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <Briefcase className="w-6 h-6 text-spring-green" />
              </div>
              <div>
                <h3 className="font-semibold text-midnight-forest mb-2">
                  Job Match Analysis
                </h3>
                <p className="text-moss-green text-sm mb-4">
                  Get matched with clean energy jobs based on your skills and experience.
                </p>
                <Button variant="outline" className="w-full">
                  Start Matching
                </Button>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <Upload className="w-6 h-6 text-spring-green" />
              </div>
              <div>
                <h3 className="font-semibold text-midnight-forest mb-2">
                  Skills Assessment
                </h3>
                <p className="text-moss-green text-sm mb-4">
                  Evaluate your skills against clean energy job requirements.
                </p>
                <Button variant="outline" className="w-full">
                  Start Assessment
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
} 