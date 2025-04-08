'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, TrendingUp, Briefcase, GraduationCap, Wind, Zap, Droplets, Sun } from 'lucide-react';
import Link from 'next/link';

// Sector data
const sectors = [
  {
    id: 'renewable-energy',
    name: 'Renewable Energy',
    description: 'Clean energy generation including solar, wind, and hydroelectric power.',
    icon: <Sun className="h-6 w-6" />,
    growthRate: 24.5,
    jobCount: 12500,
    avgSalary: '$78,500',
    topSkills: ['Solar PV Installation', 'Wind Turbine Maintenance', 'Energy Storage Systems'],
    topEmployers: ['Eversource', 'National Grid', 'Vineyard Wind'],
    color: 'bg-yellow-500'
  },
  {
    id: 'energy-efficiency',
    name: 'Energy Efficiency',
    description: 'Reducing energy consumption in buildings, transportation, and industry.',
    icon: <Zap className="h-6 w-6" />,
    growthRate: 18.2,
    jobCount: 9800,
    avgSalary: '$72,300',
    topSkills: ['HVAC Systems', 'Building Automation', 'Energy Auditing'],
    topEmployers: ['Ameresco', 'Schneider Electric', 'Johnson Controls'],
    color: 'bg-blue-500'
  },
  {
    id: 'clean-transportation',
    name: 'Clean Transportation',
    description: 'Electric vehicles, public transit, and sustainable transportation infrastructure.',
    icon: <Wind className="h-6 w-6" />,
    growthRate: 32.1,
    jobCount: 7600,
    avgSalary: '$81,200',
    topSkills: ['EV Charging Infrastructure', 'Battery Technology', 'Sustainable Logistics'],
    topEmployers: ['Tesla', 'Proterra', 'ChargePoint'],
    color: 'bg-green-500'
  },
  {
    id: 'water-management',
    name: 'Water Management',
    description: 'Water conservation, treatment, and sustainable water infrastructure.',
    icon: <Droplets className="h-6 w-6" />,
    growthRate: 15.8,
    jobCount: 5400,
    avgSalary: '$68,900',
    topSkills: ['Water Treatment', 'Stormwater Management', 'Water Conservation'],
    topEmployers: ['Xylem', 'AECOM', 'Veolia North America'],
    color: 'bg-cyan-500'
  }
];

export default function SectorExplorer() {
  const [selectedSector, setSelectedSector] = useState(sectors[0]);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Clean Energy Sector Explorer</h1>
      <p className="text-muted-foreground">
        Explore growing sectors in the Massachusetts clean energy economy, discover in-demand skills, 
        and find career opportunities.
      </p>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Sector selection cards */}
        <div className="md:w-1/3 space-y-4">
          <h2 className="text-2xl font-bold">Sectors</h2>
          
          {sectors.map(sector => (
            <Card 
              key={sector.id}
              className={`cursor-pointer transition-all ${selectedSector.id === sector.id ? 'border-primary ring-1 ring-primary' : 'hover:border-primary/50'}`}
              onClick={() => setSelectedSector(sector)}
            >
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <div className={`p-2 rounded-md ${sector.color} text-white`}>
                    {sector.icon}
                  </div>
                  <Badge variant="outline" className="flex items-center">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    {sector.growthRate}% growth
                  </Badge>
                </div>
                <CardTitle className="text-lg mt-2">{sector.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{sector.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {/* Sector details */}
        <div className="md:w-2/3">
          <Card className="h-full">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-2xl flex items-center">
                    <div className={`p-2 rounded-md ${selectedSector.color} text-white mr-3`}>
                      {selectedSector.icon}
                    </div>
                    {selectedSector.name}
                  </CardTitle>
                  <CardDescription className="mt-2">{selectedSector.description}</CardDescription>
                </div>
                <Button asChild>
                  <Link href={`/sectors/${selectedSector.id}`}>
                    Explore Sector <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            
            <CardContent>
              <Tabs defaultValue="overview">
                <TabsList className="mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="jobs">Jobs</TabsTrigger>
                  <TabsTrigger value="skills">Skills</TabsTrigger>
                  <TabsTrigger value="training">Training</TabsTrigger>
                </TabsList>
                
                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Job Openings
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="flex items-center">
                        <Briefcase className="h-5 w-5 mr-2 text-primary" />
                        <span className="text-2xl font-bold">{selectedSector.jobCount.toLocaleString()}</span>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Average Salary
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="flex items-center">
                        <TrendingUp className="h-5 w-5 mr-2 text-primary" />
                        <span className="text-2xl font-bold">{selectedSector.avgSalary}</span>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Growth Rate
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center mb-2">
                          <TrendingUp className="h-5 w-5 mr-2 text-primary" />
                          <span className="text-2xl font-bold">{selectedSector.growthRate}%</span>
                        </div>
                        <Progress value={selectedSector.growthRate} className="h-2" />
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Top Skills</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {selectedSector.topSkills.map((skill, index) => (
                            <li key={index} className="flex items-center">
                              <GraduationCap className="h-4 w-4 mr-2 text-primary" />
                              {skill}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                      <CardFooter>
                        <Button variant="outline" size="sm" asChild>
                          <Link href="/skills">
                            View All Skills
                          </Link>
                        </Button>
                      </CardFooter>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Top Employers</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {selectedSector.topEmployers.map((employer, index) => (
                            <li key={index} className="flex items-center">
                              <Briefcase className="h-4 w-4 mr-2 text-primary" />
                              {employer}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                      <CardFooter>
                        <Button variant="outline" size="sm" asChild>
                          <Link href="/employers">
                            View All Employers
                          </Link>
                        </Button>
                      </CardFooter>
                    </Card>
                  </div>
                </TabsContent>
                
                <TabsContent value="jobs">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-medium">Recent Job Openings</h3>
                      <Button variant="outline" size="sm" asChild>
                        <Link href="/jobs">
                          View All Jobs
                        </Link>
                      </Button>
                    </div>
                    
                    <div className="space-y-4">
                      {[1, 2, 3].map(job => (
                        <Card key={job}>
                          <CardHeader className="pb-2">
                            <div className="flex justify-between">
                              <CardTitle>{selectedSector.name} {job === 1 ? 'Specialist' : job === 2 ? 'Technician' : 'Engineer'}</CardTitle>
                              <Badge>{job === 1 ? '2 days ago' : job === 2 ? '1 week ago' : '3 days ago'}</Badge>
                            </div>
                            <CardDescription>{selectedSector.topEmployers[job-1]} • {job === 1 ? 'Boston' : job === 2 ? 'Cambridge' : 'Worcester'}, MA</CardDescription>
                          </CardHeader>
                          <CardContent className="pb-2">
                            <div className="flex flex-wrap gap-2 mb-2">
                              {selectedSector.topSkills.slice(job-1, job+1).map((skill, index) => (
                                <Badge key={index} variant="secondary">{skill}</Badge>
                              ))}
                            </div>
                            <div className="text-sm font-medium">
                              Salary: {selectedSector.avgSalary}
                            </div>
                          </CardContent>
                          <CardFooter>
                            <Button size="sm">Apply Now</Button>
                          </CardFooter>
                        </Card>
                      ))}
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="skills">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Key Skills in {selectedSector.name}</h3>
                    <p className="text-muted-foreground">
                      These are the most in-demand skills for jobs in the {selectedSector.name.toLowerCase()} sector in Massachusetts.
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selectedSector.topSkills.map((skill, index) => (
                        <Card key={index}>
                          <CardHeader className="pb-2">
                            <CardTitle className="text-base">{skill}</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm text-muted-foreground">Demand Level</span>
                              <Badge>High</Badge>
                            </div>
                            <Progress value={85} className="h-2" />
                          </CardContent>
                          <CardFooter>
                            <Button variant="outline" size="sm">Find Training</Button>
                          </CardFooter>
                        </Card>
                      ))}
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="training">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Training Programs</h3>
                    <p className="text-muted-foreground">
                      Find training programs in Massachusetts to build skills for the {selectedSector.name.toLowerCase()} sector.
                    </p>
                    
                    <div className="space-y-4">
                      <Card>
                        <CardHeader>
                          <CardTitle>{selectedSector.name} Certification</CardTitle>
                          <CardDescription>Massachusetts Clean Energy Center</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <p className="mb-2">
                            A comprehensive 12-week program covering core skills needed for careers in {selectedSector.name.toLowerCase()}.
                          </p>
                          <div className="flex flex-wrap gap-2 mb-2">
                            <Badge variant="outline">Free for MA Residents</Badge>
                            <Badge variant="outline">12 Weeks</Badge>
                            <Badge variant="outline">In-Person</Badge>
                          </div>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                          <div className="text-sm text-muted-foreground">Next cohort starts June 15</div>
                          <Button size="sm">Learn More</Button>
                        </CardFooter>
                      </Card>
                      
                      <Card>
                        <CardHeader>
                          <CardTitle>Advanced {selectedSector.topSkills[0]}</CardTitle>
                          <CardDescription>Bunker Hill Community College</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <p className="mb-2">
                            Specialized training in {selectedSector.topSkills[0]} with hands-on projects and industry mentorship.
                          </p>
                          <div className="flex flex-wrap gap-2 mb-2">
                            <Badge variant="outline">$1,200 (Scholarships Available)</Badge>
                            <Badge variant="outline">8 Weeks</Badge>
                            <Badge variant="outline">Hybrid</Badge>
                          </div>
                        </CardContent>
                        <CardFooter className="flex justify-between">
                          <div className="text-sm text-muted-foreground">Rolling admissions</div>
                          <Button size="sm">Learn More</Button>
                        </CardFooter>
                      </Card>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
