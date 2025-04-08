'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ArrowRight, MessageSquare, Users, Activity, Search, Briefcase } from '../lib/icons-shim';
import Link from 'next/link';
import Image from 'next/image';

/**
 * Landing Page
 * First page users see, highlighting key features
 * Location: /app/page.jsx
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="bg-midnight-forest py-20 px-4 flex-grow">
        <div className="container mx-auto max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-spring-green mb-6">
                Your Guide to the Climate Economy Ecosystem
              </h1>
              <p className="text-sand-gray text-lg mb-8">
                Connect with climate tech employers, discover personalized opportunities, and navigate your career in the green economy.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" asChild className="w-full sm:w-auto">
                  <Link href="/assistant/chat">
                    <MessageSquare className="mr-2 h-5 w-5" />
                    Chat with Assistant
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="w-full sm:w-auto">
                  <Link href="/dashboard">
                    <Activity className="mr-2 h-5 w-5" />
                    View Dashboard
                  </Link>
                </Button>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="relative h-96 w-full">
                <div className="absolute inset-0 bg-spring-green/10 rounded-lg flex items-center justify-center">
                  <div className="bg-midnight-forest/90 p-6 rounded-lg max-w-sm">
                    <div className="flex items-start gap-4 mb-4">
                      <div className="w-8 h-8 bg-spring-green/20 rounded-full flex items-center justify-center">
                        <MessageSquare className="h-4 w-4 text-spring-green" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sand-gray text-sm">
                          "I'm looking for job opportunities in solar installation in Massachusetts."
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-4">
                      <div className="w-8 h-8 bg-spring-green rounded-full flex items-center justify-center">
                        <MessageSquare className="h-4 w-4 text-midnight-forest" />
                      </div>
                      <div className="flex-1">
                        <p className="text-spring-green text-sm">
                          "I found 12 solar installer positions in your area. The top match is at SunPower in Cambridge, with an 85% match to your skills..."
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-sand-gray py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-3xl font-bold text-midnight-forest text-center mb-12">
            Navigate Your Climate Career Journey
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 bg-spring-green/20 rounded-lg flex items-center justify-center mb-4">
                <MessageSquare className="h-6 w-6 text-spring-green" />
              </div>
              <h3 className="text-xl font-semibold text-midnight-forest mb-2">
                AI Assistant
              </h3>
              <p className="text-moss-green mb-4">
                Get personalized guidance, answers, and connections to resources for your climate career.
              </p>
              <Button variant="link" className="pl-0" asChild>
                <Link href="/assistant/chat" className="flex items-center text-spring-green">
                  Start chatting
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </Card>
            
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 bg-spring-green/20 rounded-lg flex items-center justify-center mb-4">
                <Briefcase className="h-6 w-6 text-spring-green" />
              </div>
              <h3 className="text-xl font-semibold text-midnight-forest mb-2">
                Job Matches
              </h3>
              <p className="text-moss-green mb-4">
                Discover opportunities matched to your skills, interests, and career goals in clean energy.
              </p>
              <Button variant="link" className="pl-0" asChild>
                <Link href="/dashboard" className="flex items-center text-spring-green">
                  View matches
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </Card>
            
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 bg-spring-green/20 rounded-lg flex items-center justify-center mb-4">
                <Search className="h-6 w-6 text-spring-green" />
              </div>
              <h3 className="text-xl font-semibold text-midnight-forest mb-2">
                Knowledge Base
              </h3>
              <p className="text-moss-green mb-4">
                Access resources, training programs, and industry insights on the Massachusetts clean energy sector.
              </p>
              <Button variant="link" className="pl-0" asChild>
                <Link href="/assistant/search" className="flex items-center text-spring-green">
                  Explore resources
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </Card>
            
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 bg-spring-green/20 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-spring-green" />
              </div>
              <h3 className="text-xl font-semibold text-midnight-forest mb-2">
                Direct Connections
              </h3>
              <p className="text-moss-green mb-4">
                Connect directly with hiring managers at partner companies once you meet qualification thresholds.
              </p>
              <Button variant="link" className="pl-0" asChild>
                <Link href="/dashboard" className="flex items-center text-spring-green">
                  Check eligibility
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </Card>
          </div>
        </div>
      </div>
      
      {/* Call to Action */}
      <div className="bg-seafoam-blue/20 py-16 px-4">
        <div className="container mx-auto max-w-6xl text-center">
          <h2 className="text-3xl font-bold text-midnight-forest mb-6">
            Ready to Start Your Climate Career Journey?
          </h2>
          <p className="text-moss-green max-w-2xl mx-auto mb-8">
            Join thousands of professionals who have found their place in the clean energy economy through our platform.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/auth/signup">
                Create Account
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/auth/login">
                Sign In
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 