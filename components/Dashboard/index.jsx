'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  BarChart, 
  TrendingUp, 
  Users, 
  Briefcase, 
  GraduationCap, 
  Calendar,
  ArrowRight,
  Bell,
  CheckCircle,
  ExternalLink,
  FileText
} from 'lucide-react';
import Link from 'next/link';

// Sample dashboard data
const dashboardData = {
  user: {
    name: 'Alex Johnson',
    email: 'alex.johnson@example.com',
    avatar: '/placeholder-avatar.jpg',
    profileCompletion: 85,
    jobMatchScore: 78
  },
  notifications: [
    {
      id: 1,
      type: 'job',
      title: 'New job match: Solar Installation Team Lead',
      description: '92% match with your profile',
      date: '2 hours ago',
      read: false
    },
    {
      id: 2,
      type: 'event',
      title: 'Upcoming Event: Clean Energy Career Fair',
      description: 'May 15, 2023 at Boston Convention Center',
      date: '1 day ago',
      read: true
    },
    {
      id: 3,
      type: 'program',
      title: 'Application Deadline: MassCEC Internship',
      description: 'Applications due in 3 days',
      date: '2 days ago',
      read: false
    }
  ],
  jobMatches: [
    {
      id: 'job1',
      title: 'Solar Installation Team Lead',
      company: 'Boston Solar',
      location: 'Boston, MA',
      matchScore: 92,
      salary: '$75,000 - $85,000',
      posted: '3 days ago'
    },
    {
      id: 'job2',
      title: 'Energy Efficiency Specialist',
      company: 'Mass Save',
      location: 'Cambridge, MA',
      matchScore: 87,
      salary: '$65,000 - $75,000',
      posted: '1 week ago'
    },
    {
      id: 'job3',
      title: 'Renewable Energy Project Coordinator',
      company: 'MassCEC',
      location: 'Boston, MA',
      matchScore: 84,
      salary: '$60,000 - $70,000',
      posted: '2 days ago'
    }
  ],
  upcomingEvents: [
    {
      id: 'event1',
      title: 'Clean Energy Career Fair',
      organizer: 'MassCEC',
      location: 'Boston Convention Center',
      date: 'May 15, 2023',
      time: '10:00 AM - 4:00 PM',
      type: 'In-Person'
    },
    {
      id: 'event2',
      title: 'Solar Installation Workshop',
      organizer: 'NABCEP',
      location: 'Virtual',
      date: 'May 22, 2023',
      time: '1:00 PM - 3:00 PM',
      type: 'Virtual'
    }
  ],
  trainingPrograms: [
    {
      id: 'program1',
      title: 'Advanced Solar PV Installation',
      provider: 'North American Board of Certified Energy Practitioners',
      duration: '8 weeks',
      format: 'Hybrid',
      matchScore: 95,
      startDate: 'June 5, 2023'
    },
    {
      id: 'program2',
      title: 'Energy Auditing Certification',
      provider: 'Building Performance Institute',
      duration: '6 weeks',
      format: 'Online',
      matchScore: 88,
      startDate: 'July 10, 2023'
    }
  ],
  industryMetrics: {
    jobGrowth: 24.5,
    averageSalary: 78500,
    openPositions: 3250,
    topSectors: [
      { name: 'Solar Energy', growth: 32.1, jobs: 1250 },
      { name: 'Energy Efficiency', growth: 18.7, jobs: 950 },
      { name: 'Clean Transportation', growth: 27.3, jobs: 650 }
    ]
  }
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back, {dashboardData.user.name}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" asChild>
            <Link href="/profile">
              View Profile
            </Link>
          </Button>
          <Button size="sm" asChild>
            <Link href="/jobs">
              Find Jobs
            </Link>
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile summary card */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex justify-between">
              <Avatar className="h-12 w-12">
                <AvatarImage src={dashboardData.user.avatar} alt={dashboardData.user.name} />
                <AvatarFallback>{dashboardData.user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
              </Avatar>
              <Badge variant="outline">Profile</Badge>
            </div>
            <CardTitle className="mt-4">{dashboardData.user.name}</CardTitle>
            <CardDescription>{dashboardData.user.email}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Profile Completion</span>
                <span className="text-sm font-medium">{dashboardData.user.profileCompletion}%</span>
              </div>
              <Progress value={dashboardData.user.profileCompletion} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Job Match Score</span>
                <span className="text-sm font-medium">{dashboardData.user.jobMatchScore}/100</span>
              </div>
              <Progress value={dashboardData.user.jobMatchScore} className="h-2" />
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full" asChild>
              <Link href="/profile/enhance">
                Enhance Your Profile
              </Link>
            </Button>
          </CardFooter>
        </Card>
        
        {/* Notifications card */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Notifications</CardTitle>
              <Badge>{dashboardData.notifications.filter(n => !n.read).length}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {dashboardData.notifications.map(notification => (
              <div 
                key={notification.id} 
                className={`p-3 rounded-lg border ${notification.read ? 'bg-background' : 'bg-muted border-primary'}`}
              >
                <div className="flex items-start">
                  <div className={`p-2 rounded-full ${
                    notification.type === 'job' 
                      ? 'bg-blue-100 text-blue-600' 
                      : notification.type === 'event' 
                        ? 'bg-green-100 text-green-600' 
                        : 'bg-amber-100 text-amber-600'
                  } mr-3`}>
                    {notification.type === 'job' 
                      ? <Briefcase className="h-4 w-4" /> 
                      : notification.type === 'event' 
                        ? <Calendar className="h-4 w-4" /> 
                        : <GraduationCap className="h-4 w-4" />
                    }
                  </div>
                  <div>
                    <div className="font-medium text-sm">{notification.title}</div>
                    <div className="text-xs text-muted-foreground">{notification.description}</div>
                    <div className="text-xs text-muted-foreground mt-1">{notification.date}</div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
          <CardFooter>
            <Button variant="ghost" size="sm" className="w-full">
              View All Notifications
            </Button>
          </CardFooter>
        </Card>
        
        {/* Industry metrics card */}
        <Card>
          <CardHeader>
            <CardTitle>Industry Metrics</CardTitle>
            <CardDescription>Massachusetts Clean Energy Economy</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Job Growth</div>
                <div className="flex items-center">
                  <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                  <span className="font-bold text-green-600">+{dashboardData.industryMetrics.jobGrowth}%</span>
                </div>
              </div>
              
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Average Salary</div>
                <div className="font-bold">${dashboardData.industryMetrics.averageSalary.toLocaleString()}</div>
              </div>
              
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Open Positions</div>
                <div className="font-bold">{dashboardData.industryMetrics.openPositions.toLocaleString()}</div>
              </div>
              
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Top Sector</div>
                <div className="font-bold">{dashboardData.industryMetrics.topSectors[0].name}</div>
              </div>
            </div>
            
            <div className="pt-2">
              <div className="text-sm font-medium mb-2">Sector Growth</div>
              {dashboardData.industryMetrics.topSectors.map((sector, index) => (
                <div key={index} className="mb-2 last:mb-0">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm">{sector.name}</span>
                    <span className="text-xs text-green-600">+{sector.growth}%</span>
                  </div>
                  <Progress value={sector.growth} max={40} className="h-1" />
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="outline" size="sm" className="w-full" asChild>
              <Link href="/sectors">
                <BarChart className="h-4 w-4 mr-2" />
                Explore Sectors
              </Link>
            </Button>
          </CardFooter>
        </Card>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full justify-start">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="jobs">Job Matches</TabsTrigger>
          <TabsTrigger value="training">Training</TabsTrigger>
          <TabsTrigger value="events">Events</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top job match */}
            <Card>
              <CardHeader>
                <CardTitle>Top Job Match</CardTitle>
                <CardDescription>Based on your profile and skills</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="text-xl font-bold">{dashboardData.jobMatches[0].title}</div>
                    <div className="text-muted-foreground">{dashboardData.jobMatches[0].company}</div>
                    <div className="flex items-center mt-1 text-sm">
                      <Briefcase className="h-4 w-4 mr-1 text-muted-foreground" />
                      <span>{dashboardData.jobMatches[0].location}</span>
                    </div>
                  </div>
                  <Badge className="bg-green-600">{dashboardData.jobMatches[0].matchScore}% Match</Badge>
                </div>
                
                <div className="text-sm mb-4">
                  <div className="font-medium">Salary Range</div>
                  <div>{dashboardData.jobMatches[0].salary}</div>
                </div>
                
                <div className="text-sm">
                  <div className="font-medium">Posted</div>
                  <div>{dashboardData.jobMatches[0].posted}</div>
                </div>
              </CardContent>
              <CardFooter>
                <Button asChild>
                  <Link href={`/jobs/${dashboardData.jobMatches[0].id}`}>
                    View Job Details
                  </Link>
                </Button>
              </CardFooter>
            </Card>
            
            {/* Next event */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Event</CardTitle>
                <CardDescription>Mark your calendar</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="text-xl font-bold">{dashboardData.upcomingEvents[0].title}</div>
                    <div className="text-muted-foreground">{dashboardData.upcomingEvents[0].organizer}</div>
                    <div className="flex items-center mt-1 text-sm">
                      <Calendar className="h-4 w-4 mr-1 text-muted-foreground" />
                      <span>{dashboardData.upcomingEvents[0].date}</span>
                    </div>
                  </div>
                  <Badge variant="outline">{dashboardData.upcomingEvents[0].type}</Badge>
                </div>
                
                <div className="text-sm mb-4">
                  <div className="font-medium">Time</div>
                  <div>{dashboardData.upcomingEvents[0].time}</div>
                </div>
                
                <div className="text-sm">
                  <div className="font-medium">Location</div>
                  <div>{dashboardData.upcomingEvents[0].location}</div>
                </div>
              </CardContent>
              <CardFooter>
                <Button asChild>
                  <Link href={`/events/${dashboardData.upcomingEvents[0].id}`}>
                    Event Details
                  </Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Recommended Next Steps</CardTitle>
              <CardDescription>Actions to improve your clean energy career prospects</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className="bg-primary/10 p-2 rounded-full mr-3">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div className="font-medium">Complete Your Profile</div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Add your certifications and work samples to increase your profile strength.
                  </p>
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <Link href="/profile/edit">
                      Update Profile
                    </Link>
                  </Button>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className="bg-primary/10 p-2 rounded-full mr-3">
                      <GraduationCap className="h-5 w-5 text-primary" />
                    </div>
                    <div className="font-medium">Explore Training</div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Enhance your skills with recommended training programs in your field.
                  </p>
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <Link href="/training">
                      Find Training
                    </Link>
                  </Button>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center">
                    <div className="bg-primary/10 p-2 rounded-full mr-3">
                      <Users className="h-5 w-5 text-primary" />
                    </div>
                    <div className="font-medium">Network</div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Connect with professionals and attend industry events to build your network.
                  </p>
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <Link href="/events">
                      Find Events
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="jobs" className="space-y-6 mt-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Your Job Matches</h2>
            <Button asChild>
              <Link href="/jobs">
                View All Jobs
              </Link>
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dashboardData.jobMatches.map(job => (
              <Card key={job.id}>
                <CardHeader>
                  <div className="flex justify-between">
                    <div>
                      <CardTitle>{job.title}</CardTitle>
                      <CardDescription>{job.company} • {job.location}</CardDescription>
                    </div>
                    <Badge className="bg-green-600">{job.matchScore}% Match</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Salary Range:</span>
                      <span>{job.salary}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Posted:</span>
                      <span>{job.posted}</span>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button variant="outline" size="sm">Save</Button>
                  <Button size="sm" asChild>
                    <Link href={`/jobs/${job.id}`}>
                      View Details
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Job Search Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start">
                <CheckCircle className="h-5 w-5 mr-3 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">Tailor your resume for each application</p>
                  <p className="text-sm text-muted-foreground">
                    Highlight relevant skills and experience for each specific job you apply to.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <CheckCircle className="h-5 w-5 mr-3 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">Prepare for technical interviews</p>
                  <p className="text-sm text-muted-foreground">
                    Clean energy jobs often require demonstrating technical knowledge during interviews.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <CheckCircle className="h-5 w-5 mr-3 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">Leverage industry connections</p>
                  <p className="text-sm text-muted-foreground">
                    Many clean energy jobs are filled through networking and referrals.
                  </p>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="outline" asChild>
                <Link href="/resources/job-search">
                  View Job Search Resources
                </Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="training" className="space-y-6 mt-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Recommended Training</h2>
            <Button asChild>
              <Link href="/training">
                View All Programs
              </Link>
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dashboardData.trainingPrograms.map(program => (
              <Card key={program.id}>
                <CardHeader>
                  <div className="flex justify-between">
                    <div>
                      <CardTitle>{program.title}</CardTitle>
                      <CardDescription>{program.provider}</CardDescription>
                    </div>
                    <Badge className="bg-green-600">{program.matchScore}% Match</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Duration:</span>
                      <span>{program.duration}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Format:</span>
                      <span>{program.format}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Start Date:</span>
                      <span>{program.startDate}</span>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button variant="outline" size="sm">Save</Button>
                  <Button size="sm" asChild>
                    <Link href={`/training/${program.id}`}>
                      View Details
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Financial Assistance</CardTitle>
              <CardDescription>Resources to help fund your training</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-b pb-4">
                <div className="font-medium mb-1">MassCEC Workforce Development Grants</div>
                <p className="text-sm text-muted-foreground mb-2">
                  Funding for Massachusetts residents pursuing clean energy training and certifications.
                </p>
                <Button size="sm" variant="outline" asChild>
                  <Link href="https://www.masscec.com/workforce" target="_blank" rel="noopener noreferrer">
                    Learn More <ExternalLink className="h-3 w-3 ml-1" />
                  </Link>
                </Button>
              </div>
              
              <div className="border-b pb-4">
                <div className="font-medium mb-1">Clean Energy Scholarship Program</div>
                <p className="text-sm text-muted-foreground mb-2">
                  Scholarships for students pursuing degrees or certifications in clean energy fields.
                </p>
                <Button size="sm" variant="outline">
                  Check Eligibility
                </Button>
              </div>
              
              <div>
                <div className="font-medium mb-1">Employer Tuition Assistance</div>
                <p className="text-sm text-muted-foreground mb-2">
                  Many clean energy employers offer tuition reimbursement for relevant training.
                </p>
                <Button size="sm" variant="outline">
                  View Participating Employers
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="events" className="space-y-6 mt-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Upcoming Events</h2>
            <Button asChild>
              <Link href="/events">
                View All Events
              </Link>
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dashboardData.upcomingEvents.map(event => (
              <Card key={event.id}>
                <CardHeader>
                  <div className="flex justify-between">
                    <div>
                      <CardTitle>{event.title}</CardTitle>
                      <CardDescription>{event.organizer}</CardDescription>
                    </div>
                    <Badge variant="outline">{event.type}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center text-sm">
                      <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                      <span>{event.date} • {event.time}</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 mr-2 text-muted-foreground" />
                      <span>{event.location}</span>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button variant="outline" size="sm">Add to Calendar</Button>
                  <Button size="sm" asChild>
                    <Link href={`/events/${event.id}`}>
                      Event Details
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Networking Opportunities</CardTitle>
              <CardDescription>Connect with clean energy professionals</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-b pb-4">
                <div className="font-medium mb-1">Massachusetts Clean Energy Meetup Group</div>
                <p className="text-sm text-muted-foreground mb-2">
                  Regular networking events for clean energy professionals across Massachusetts.
                </p>
                <Button size="sm" variant="outline">
                  Join Group
                </Button>
              </div>
              
              <div className="border-b pb-4">
                <div className="font-medium mb-1">Women in Clean Energy Mentorship Program</div>
                <p className="text-sm text-muted-foreground mb-2">
                  Mentorship and networking program for women pursuing careers in clean energy.
                </p>
                <Button size="sm" variant="outline">
                  Apply Now
                </Button>
              </div>
              
              <div>
                <div className="font-medium mb-1">Clean Energy Industry Associations</div>
                <p className="text-sm text-muted-foreground mb-2">
                  Join industry associations for networking, professional development, and job opportunities.
                </p>
                <Button size="sm" variant="outline">
                  View Associations
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
