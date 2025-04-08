"use client";

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Briefcase, GraduationCap, BookOpen, Star, Calendar, MapPin, Building2, ArrowRight, Users, ThumbsUp } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

/**
 * Personalized Dashboard
 * Combines jobs, training, and resources based on user profile
 * Location: /app/dashboard/page.jsx
 */
export default function Dashboard() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('recommended');
  const [isLoading, setIsLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard/data');
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-spring-green border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-midnight-forest mb-2">
            Welcome back, {user?.user_metadata?.full_name || 'Clean Tech Professional'}
          </h1>
          <p className="text-moss-green">
            Your personalized clean energy ecosystem dashboard
          </p>
        </div>

        {/* Connection Eligibility Card */}
        <Card className="mb-8 overflow-hidden">
          <div className="bg-spring-green/10 p-6 border-b border-spring-green/20">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-midnight-forest">
                Direct Connection Eligibility Status
              </h2>
              <Badge 
                className={dashboardData?.connectionEligibility?.isEligible ? 
                  "bg-spring-green text-midnight-forest" : 
                  "bg-moss-green/30 text-moss-green"
                }
              >
                {dashboardData?.connectionEligibility?.isEligible ? 
                  "Eligible" : "Not Yet Eligible"
                }
              </Badge>
            </div>
            <p className="text-moss-green mt-2">
              {dashboardData?.connectionEligibility?.isEligible ? 
                "You're eligible to connect directly with hiring managers and HR at our partner companies." : 
                "Complete the requirements below to qualify for direct connections with partner companies."
              }
            </p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Profile Strength Requirement */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-midnight-forest">Profile Strength</h3>
                  <Badge 
                    className={dashboardData?.connectionEligibility?.profileStrength.achieved ? 
                      "bg-spring-green/10 text-spring-green" : 
                      "bg-sand-gray text-moss-green"
                    }
                  >
                    {dashboardData?.connectionEligibility?.profileStrength.current}
                    /{dashboardData?.connectionEligibility?.profileStrength.required}
                  </Badge>
                </div>
                <Progress 
                  value={dashboardData?.connectionEligibility?.profileStrength.current} 
                  className={dashboardData?.connectionEligibility?.profileStrength.achieved ? 
                    "bg-spring-green" : ""
                  }
                />
                <p className="text-xs text-moss-green">
                  {dashboardData?.connectionEligibility?.profileStrength.achieved ? 
                    "Requirement met! Your profile is complete." : 
                    `Complete your profile to reach the ${dashboardData?.connectionEligibility?.profileStrength.required}% threshold.`
                  }
                </p>
                {!dashboardData?.connectionEligibility?.profileStrength.achieved && (
                  <Button size="sm" variant="outline" className="w-full mt-2">
                    Enhance Profile
                  </Button>
                )}
              </div>
              
              {/* Engagement Score Requirement */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-midnight-forest">Engagement Score</h3>
                  <Badge 
                    className={dashboardData?.connectionEligibility?.engagementScore.achieved ? 
                      "bg-spring-green/10 text-spring-green" : 
                      "bg-sand-gray text-moss-green"
                    }
                  >
                    {dashboardData?.connectionEligibility?.engagementScore.current}
                    /{dashboardData?.connectionEligibility?.engagementScore.required}
                  </Badge>
                </div>
                <Progress 
                  value={dashboardData?.connectionEligibility?.engagementScore.current} 
                  className={dashboardData?.connectionEligibility?.engagementScore.achieved ? 
                    "bg-spring-green" : ""
                  }
                />
                <p className="text-xs text-moss-green">
                  {dashboardData?.connectionEligibility?.engagementScore.achieved ? 
                    "Requirement met! Your engagement is strong." : 
                    `Increase engagement by exploring resources and recommendations.`
                  }
                </p>
                {!dashboardData?.connectionEligibility?.engagementScore.achieved && (
                  <Button size="sm" variant="outline" className="w-full mt-2">
                    Boost Engagement
                  </Button>
                )}
              </div>
              
              {/* Match Score Requirement */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-midnight-forest">Match Quality</h3>
                  <Badge 
                    className={dashboardData?.connectionEligibility?.averageMatchScore.achieved ? 
                      "bg-spring-green/10 text-spring-green" : 
                      "bg-sand-gray text-moss-green"
                    }
                  >
                    {dashboardData?.connectionEligibility?.averageMatchScore.current}
                    /{dashboardData?.connectionEligibility?.averageMatchScore.required}
                  </Badge>
                </div>
                <Progress 
                  value={dashboardData?.connectionEligibility?.averageMatchScore.current} 
                  className={dashboardData?.connectionEligibility?.averageMatchScore.achieved ? 
                    "bg-spring-green" : ""
                  }
                />
                <p className="text-xs text-moss-green">
                  {dashboardData?.connectionEligibility?.averageMatchScore.achieved ? 
                    "Requirement met! Your skills match our partner needs." : 
                    `Add more skills and experience to increase your match score.`
                  }
                </p>
                {!dashboardData?.connectionEligibility?.averageMatchScore.achieved && (
                  <Button size="sm" variant="outline" className="w-full mt-2">
                    Improve Match
                  </Button>
                )}
              </div>
            </div>
            
            {/* Persona-specific message */}
            <div className="mt-6 p-4 bg-sand-gray/30 rounded-lg">
              <p className="text-sm text-moss-green">
                <span className="font-semibold">Note:</span> {' '}
                {dashboardData?.persona === 'veteran' && 'Military veterans benefit from lower engagement thresholds due to valuable transferable skills.'}
                {dashboardData?.persona === 'international' && 'International professionals require verified credentials before direct connections.'}
                {dashboardData?.persona === 'student' && 'Students need to demonstrate consistent engagement with the platform.'}
                {dashboardData?.persona === 'ej' && 'Environmental Justice community members have specialized training programs available.'}
                {dashboardData?.persona === 'reentry' && 'Re-entry candidates benefit from detailed profile information to improve matching.'}
                {(dashboardData?.persona === 'default' || !dashboardData?.persona) && 'Complete your profile and engage regularly to qualify for direct connections.'}
              </p>
            </div>
          </div>
        </Card>

        {/* Engagement Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <Star className="w-6 h-6 text-spring-green" />
              </div>
              <div>
                <h3 className="font-semibold text-midnight-forest">Profile Strength</h3>
                <Progress value={dashboardData?.profileStrength || 0} className="mt-2" />
              </div>
            </div>
            <Button variant="link" className="text-spring-green">
              Complete your profile
            </Button>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <Users className="w-6 h-6 text-spring-green" />
              </div>
              <div>
                <h3 className="font-semibold text-midnight-forest">Direct Connections</h3>
                <p className="text-2xl font-bold text-spring-green">
                  {dashboardData?.engagement?.direct_connections || 0}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <Star className="w-6 h-6 text-spring-green" />
              </div>
              <div>
                <h3 className="font-semibold text-midnight-forest">Recommendations</h3>
                <p className="text-2xl font-bold text-spring-green">
                  {dashboardData?.engagement?.recommendations_received || 0}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <ThumbsUp className="w-6 h-6 text-spring-green" />
              </div>
              <div>
                <h3 className="font-semibold text-midnight-forest">Satisfaction Score</h3>
                <p className="text-2xl font-bold text-spring-green">
                  {dashboardData?.engagement?.satisfaction_score || 0}%
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Card className="mb-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="p-6">
            <TabsList className="grid grid-cols-3 gap-4 mb-6">
              <TabsTrigger value="recommended" className="flex items-center gap-2">
                <Star className="w-4 h-4" />
                Recommended
              </TabsTrigger>
              <TabsTrigger value="connections" className="flex items-center gap-2">
                <Users className="w-4 h-4" />
                Connections
              </TabsTrigger>
              <TabsTrigger value="events" className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Events
              </TabsTrigger>
            </TabsList>

            <TabsContent value="recommended">
              <div className="space-y-4">
                {dashboardData?.recommendations?.map((rec) => (
                  <Card key={rec.id} className="p-6">
                    <div className="flex justify-between items-start">
                      <div>
                        <Badge className="mb-2 bg-spring-green/10 text-spring-green">
                          {rec.type}
                        </Badge>
                        <h3 className="text-lg font-semibold text-midnight-forest mb-2">{rec.title}</h3>
                        <div className="flex items-center gap-2 text-moss-green mb-2">
                          <Building2 className="w-4 h-4" />
                          <span>{rec.company_name}</span>
                          <span>•</span>
                          <MapPin className="w-4 h-4" />
                          <span>{rec.location}</span>
                        </div>
                        <p className="text-moss-green mb-4">{rec.description}</p>
                        <div className="flex items-center gap-4">
                          <Button asChild>
                            <a href={rec.url} target="_blank" rel="noopener noreferrer">
                              View Details
                            </a>
                          </Button>
                          <div className="text-sm text-moss-green">
                            Contact: {rec.contact_name}, {rec.contact_title}
                          </div>
                        </div>
                      </div>
                      <Badge className="bg-spring-green/10 text-spring-green">
                        {rec.match_score}% Match
                      </Badge>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="connections">
              <div className="space-y-4">
                {dashboardData?.recent_connections?.map((connection) => (
                  <Card key={connection.id} className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-lg bg-spring-green/10">
                        <Users className="w-6 h-6 text-spring-green" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-midnight-forest mb-2">
                          {connection.partner.contact_name}
                        </h3>
                        <p className="text-moss-green">
                          {connection.partner.contact_title} at {connection.partner.company_name}
                        </p>
                        <p className="text-sm text-moss-green mt-2">
                          Connected on {new Date(connection.connected_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="events">
              <div className="space-y-4">
                {dashboardData?.upcoming_events?.map((event) => (
                  <Card key={event.id} className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-lg bg-spring-green/10">
                        <Calendar className="w-6 h-6 text-spring-green" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-midnight-forest mb-2">
                          {event.title}
                        </h3>
                        <div className="flex items-center gap-2 text-moss-green mb-2">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(event.date).toLocaleDateString()}</span>
                          <span>•</span>
                          <MapPin className="w-4 h-4" />
                          <span>{event.location}</span>
                        </div>
                        <p className="text-moss-green mb-4">{event.description}</p>
                        <Button asChild>
                          <a href={event.registration_url} target="_blank" rel="noopener noreferrer">
                            Register Now
                          </a>
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </Card>

        {/* Resources Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <BookOpen className="w-6 h-6 text-spring-green" />
              </div>
              <h3 className="font-semibold text-midnight-forest">Learning Resources</h3>
            </div>
            <ul className="space-y-3 mb-4">
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Clean Energy Fundamentals
              </li>
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Industry Best Practices
              </li>
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Career Development
              </li>
            </ul>
            <Button variant="outline" className="w-full">Explore Resources</Button>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <GraduationCap className="w-6 h-6 text-spring-green" />
              </div>
              <h3 className="font-semibold text-midnight-forest">Skill Development</h3>
            </div>
            <ul className="space-y-3 mb-4">
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Technical Skills
              </li>
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Project Management
              </li>
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Leadership Training
              </li>
            </ul>
            <Button variant="outline" className="w-full">Start Learning</Button>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-lg bg-spring-green/10">
                <Building2 className="w-6 h-6 text-spring-green" />
              </div>
              <h3 className="font-semibold text-midnight-forest">Industry Insights</h3>
            </div>
            <ul className="space-y-3 mb-4">
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Market Trends
              </li>
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Company Profiles
              </li>
              <li className="flex items-center gap-2 text-moss-green">
                <ArrowRight className="w-4 h-4" />
                Success Stories
              </li>
            </ul>
            <Button variant="outline" className="w-full">Read More</Button>
          </Card>
        </div>
      </div>
    </div>
  );
}

