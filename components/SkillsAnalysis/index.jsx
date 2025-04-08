'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  TrendingUp, 
  Briefcase, 
  GraduationCap, 
  BarChart, 
  ArrowRight,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import Link from 'next/link';

// Sample skills data
const skillsData = [
  {
    id: 'solar-installation',
    name: 'Solar Panel Installation',
    category: 'Technical',
    demandScore: 92,
    growthRate: 28.5,
    avgSalary: '$72,000',
    jobCount: 3250,
    matchScore: 85,
    requiredFor: ['Solar Installer', 'PV System Designer', 'Renewable Energy Technician'],
    relatedSkills: ['Electrical Systems', 'Roofing', 'Safety Protocols'],
    trainingPrograms: [
      { name: 'Solar Installation Certificate', provider: 'MassCEC', duration: '8 weeks', cost: 'Free for MA residents' },
      { name: 'PV Associate Certification', provider: 'NABCEP', duration: 'Self-paced', cost: '$500' }
    ]
  },
  {
    id: 'energy-auditing',
    name: 'Energy Auditing',
    category: 'Technical',
    demandScore: 88,
    growthRate: 22.3,
    avgSalary: '$68,500',
    jobCount: 2800,
    matchScore: 72,
    requiredFor: ['Energy Auditor', 'Building Performance Specialist', 'Sustainability Consultant'],
    relatedSkills: ['Building Science', 'HVAC Systems', 'Energy Modeling'],
    trainingPrograms: [
      { name: 'BPI Building Analyst Certification', provider: 'MassGreen', duration: '4 weeks', cost: '$1,200 (scholarships available)' },
      { name: 'Energy Auditor Training', provider: 'UMass Clean Energy Extension', duration: '12 weeks', cost: '$2,000' }
    ]
  },
  {
    id: 'ev-charging',
    name: 'EV Charging Infrastructure',
    category: 'Technical',
    demandScore: 95,
    growthRate: 34.7,
    avgSalary: '$78,200',
    jobCount: 1950,
    matchScore: 68,
    requiredFor: ['EV Infrastructure Specialist', 'Charging Station Technician', 'Electrical Engineer'],
    relatedSkills: ['Electrical Systems', 'Network Configuration', 'Site Assessment'],
    trainingPrograms: [
      { name: 'EV Infrastructure Certification', provider: 'Electric Vehicle Infrastructure Training Program', duration: '6 weeks', cost: '$1,500' },
      { name: 'Advanced EV Charging Systems', provider: 'Roxbury Community College', duration: '10 weeks', cost: '$1,800' }
    ]
  },
  {
    id: 'project-management',
    name: 'Clean Energy Project Management',
    category: 'Business',
    demandScore: 90,
    growthRate: 18.9,
    avgSalary: '$85,000',
    jobCount: 2100,
    matchScore: 91,
    requiredFor: ['Renewable Energy Project Manager', 'Sustainability Program Manager', 'Clean Energy Development Manager'],
    relatedSkills: ['Budgeting', 'Stakeholder Management', 'Permitting'],
    trainingPrograms: [
      { name: 'Clean Energy Project Management Certificate', provider: 'Boston University', duration: '16 weeks', cost: '$3,200' },
      { name: 'Sustainable Project Management', provider: 'UMass Amherst', duration: '8 weeks', cost: '$1,800' }
    ]
  },
  {
    id: 'energy-storage',
    name: 'Energy Storage Systems',
    category: 'Technical',
    demandScore: 94,
    growthRate: 31.2,
    avgSalary: '$76,800',
    jobCount: 1650,
    matchScore: 65,
    requiredFor: ['Energy Storage Specialist', 'Battery Systems Engineer', 'Microgrid Designer'],
    relatedSkills: ['Battery Technology', 'Power Electronics', 'System Integration'],
    trainingPrograms: [
      { name: 'Energy Storage Certificate', provider: 'MassCEC', duration: '10 weeks', cost: '$1,200' },
      { name: 'Battery Systems Engineering', provider: 'Worcester Polytechnic Institute', duration: '14 weeks', cost: '$2,500' }
    ]
  }
];

export default function SkillsAnalysis() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkill, setSelectedSkill] = useState(skillsData[0]);
  const [userSkills, setUserSkills] = useState(['Project Management', 'Electrical Systems', 'Customer Service']);
  
  // Filter skills based on search query
  const filteredSkills = searchQuery 
    ? skillsData.filter(skill => 
        skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        skill.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : skillsData;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Clean Energy Skills Analysis</h1>
      <p className="text-muted-foreground">
        Explore in-demand skills in the Massachusetts clean energy economy, assess your skill gaps, 
        and find training opportunities.
      </p>
      
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
        <Input 
          placeholder="Search for skills..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Skills list */}
        <div className="md:w-1/3 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Top Skills</h2>
            <Badge variant="outline" className="flex items-center">
              <TrendingUp className="h-3 w-3 mr-1" />
              High Demand
            </Badge>
          </div>
          
          {filteredSkills.map(skill => (
            <Card 
              key={skill.id}
              className={`cursor-pointer transition-all ${selectedSkill.id === skill.id ? 'border-primary ring-1 ring-primary' : 'hover:border-primary/50'}`}
              onClick={() => setSelectedSkill(skill)}
            >
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg">{skill.name}</CardTitle>
                  <Badge>{skill.category}</Badge>
                </div>
              </CardHeader>
              <CardContent className="pb-2">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-muted-foreground">Demand Level</span>
                  <span className="text-sm font-medium">{skill.demandScore}/100</span>
                </div>
                <Progress value={skill.demandScore} className="h-2" />
                
                <div className="flex justify-between mt-4">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Growth: </span>
                    <span className="font-medium text-green-600">+{skill.growthRate}%</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-muted-foreground">Jobs: </span>
                    <span className="font-medium">{skill.jobCount.toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <div className="w-full flex items-center">
                  <span className="text-sm text-muted-foreground mr-2">Your Match:</span>
                  <Progress value={skill.matchScore} className="h-2 flex-grow" />
                  <span className="text-sm font-medium ml-2">{skill.matchScore}%</span>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
        
        {/* Skill details */}
        <div className="md:w-2/3">
          <Card className="h-full">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-2xl">{selectedSkill.name}</CardTitle>
                  <CardDescription className="mt-2">
                    A highly sought-after skill in the Massachusetts clean energy sector with {selectedSkill.jobCount.toLocaleString()} open positions.
                  </CardDescription>
                </div>
                <Button asChild>
                  <Link href={`/skills/${selectedSkill.id}`}>
                    Explore Skill <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            
            <CardContent>
              <Tabs defaultValue="overview">
                <TabsList className="mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="jobs">Related Jobs</TabsTrigger>
                  <TabsTrigger value="gap-analysis">Gap Analysis</TabsTrigger>
                  <TabsTrigger value="training">Training</TabsTrigger>
                </TabsList>
                
                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Demand Score
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center mb-2">
                          <BarChart className="h-5 w-5 mr-2 text-primary" />
                          <span className="text-2xl font-bold">{selectedSkill.demandScore}/100</span>
                        </div>
                        <Progress value={selectedSkill.demandScore} className="h-2" />
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
                        <span className="text-2xl font-bold">{selectedSkill.avgSalary}</span>
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
                          <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                          <span className="text-2xl font-bold text-green-600">+{selectedSkill.growthRate}%</span>
                        </div>
                        <Progress value={selectedSkill.growthRate} className="h-2 bg-green-100" indicatorClassName="bg-green-600" />
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Required For</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {selectedSkill.requiredFor.map((job, index) => (
                            <li key={index} className="flex items-center">
                              <Briefcase className="h-4 w-4 mr-2 text-primary" />
                              {job}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                      <CardFooter>
                        <Button variant="outline" size="sm" asChild>
                          <Link href="/jobs">
                            View Related Jobs
                          </Link>
                        </Button>
                      </CardFooter>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Related Skills</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {selectedSkill.relatedSkills.map((skill, index) => (
                            <li key={index} className="flex items-center">
                              <GraduationCap className="h-4 w-4 mr-2 text-primary" />
                              {skill}
                              {userSkills.includes(skill) && (
                                <Badge variant="outline" className="ml-2 text-green-600 border-green-600">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  You have this
                                </Badge>
                              )}
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
                  </div>
                </TabsContent>
                
                <TabsContent value="jobs">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <h3 className="text-lg font-medium">Jobs Requiring {selectedSkill.name}</h3>
                      <Button variant="outline" size="sm" asChild>
                        <Link href="/jobs">
                          View All Jobs
                        </Link>
                      </Button>
                    </div>
                    
                    <div className="space-y-4">
                      {selectedSkill.requiredFor.map((job, index) => (
                        <Card key={index}>
                          <CardHeader className="pb-2">
                            <div className="flex justify-between">
                              <CardTitle>{job}</CardTitle>
                              <Badge>{index === 0 ? '12 openings' : index === 1 ? '8 openings' : '5 openings'}</Badge>
                            </div>
                            <CardDescription>
                              {index === 0 ? 'Multiple Companies' : index === 1 ? 'MassCEC, Eversource' : 'National Grid, Ameresco'}
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="pb-2">
                            <div className="flex flex-wrap gap-2 mb-2">
                              <Badge variant="secondary">{selectedSkill.name}</Badge>
                              {selectedSkill.relatedSkills.slice(0, 2).map((skill, i) => (
                                <Badge key={i} variant="secondary">{skill}</Badge>
                              ))}
                            </div>
                            <div className="text-sm font-medium">
                              Salary Range: {selectedSkill.avgSalary} - ${parseInt(selectedSkill.avgSalary.replace('$', '').replace(',', '')) + 15000}
                            </div>
                          </CardContent>
                          <CardFooter>
                            <Button size="sm">View Job Details</Button>
                          </CardFooter>
                        </Card>
                      ))}
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="gap-analysis">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Your Skill Gap Analysis</h3>
                    <p className="text-muted-foreground">
                      Based on your profile, here's how your skills match with the requirements for {selectedSkill.name}.
                    </p>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Overall Match</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">Your match score</span>
                          <span className="text-sm font-medium">{selectedSkill.matchScore}%</span>
                        </div>
                        <Progress value={selectedSkill.matchScore} className="h-3" />
                        
                        <div className="mt-4 space-y-4">
                          <div>
                            <div className="flex items-center mb-2">
                              <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                              <span className="font-medium">Skills You Have</span>
                            </div>
                            <div className="ml-6 space-y-2">
                              {userSkills.map((skill, index) => (
                                <div key={index} className="flex items-center">
                                  <Badge variant="outline" className="text-green-600 border-green-600">
                                    {skill}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <div className="flex items-center mb-2">
                              <XCircle className="h-4 w-4 mr-2 text-red-500" />
                              <span className="font-medium">Skills You Need</span>
                            </div>
                            <div className="ml-6 space-y-2">
                              {selectedSkill.relatedSkills
                                .filter(skill => !userSkills.includes(skill))
                                .map((skill, index) => (
                                  <div key={index} className="flex items-center justify-between">
                                    <Badge variant="outline" className="text-red-500 border-red-500">
                                      {skill}
                                    </Badge>
                                    <Button size="sm" variant="outline">Find Training</Button>
                                  </div>
                                ))
                              }
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Recommended Next Steps</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-4">
                          <li className="flex items-start">
                            <AlertCircle className="h-5 w-5 mr-2 text-primary mt-0.5" />
                            <div>
                              <p className="font-medium">Complete training in {selectedSkill.relatedSkills[0]}</p>
                              <p className="text-sm text-muted-foreground">This skill is required for 85% of jobs in this field.</p>
                            </div>
                          </li>
                          <li className="flex items-start">
                            <AlertCircle className="h-5 w-5 mr-2 text-primary mt-0.5" />
                            <div>
                              <p className="font-medium">Gain practical experience through internships</p>
                              <p className="text-sm text-muted-foreground">The MassCEC internship program is currently accepting applications.</p>
                            </div>
                          </li>
                          <li className="flex items-start">
                            <AlertCircle className="h-5 w-5 mr-2 text-primary mt-0.5" />
                            <div>
                              <p className="font-medium">Obtain industry certification</p>
                              <p className="text-sm text-muted-foreground">See the training tab for recommended certification programs.</p>
                            </div>
                          </li>
                        </ul>
                      </CardContent>
                      <CardFooter>
                        <Button>Create Development Plan</Button>
                      </CardFooter>
                    </Card>
                  </div>
                </TabsContent>
                
                <TabsContent value="training">
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium">Training Programs</h3>
                    <p className="text-muted-foreground">
                      Find training programs in Massachusetts to develop your {selectedSkill.name} skills.
                    </p>
                    
                    <div className="space-y-4">
                      {selectedSkill.trainingPrograms.map((program, index) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle>{program.name}</CardTitle>
                            <CardDescription>{program.provider}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="flex flex-wrap gap-2 mb-4">
                              <Badge variant="outline">{program.duration}</Badge>
                              <Badge variant="outline">{program.cost}</Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              This program provides comprehensive training in {selectedSkill.name} and related skills, 
                              with hands-on projects and industry-recognized certification.
                            </p>
                          </CardContent>
                          <CardFooter className="flex justify-between">
                            <div className="text-sm text-muted-foreground">Next session starts soon</div>
                            <Button size="sm">Learn More</Button>
                          </CardFooter>
                        </Card>
                      ))}
                      
                      <Card>
                        <CardHeader>
                          <CardTitle>MassCEC Workforce Development Programs</CardTitle>
                          <CardDescription>Massachusetts Clean Energy Center</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <p className="mb-4">
                            MassCEC offers a variety of training programs and funding opportunities to help Massachusetts 
                            residents develop skills for the clean energy economy.
                          </p>
                          <div className="flex flex-wrap gap-2">
                            <Badge variant="outline">Multiple Programs</Badge>
                            <Badge variant="outline">Financial Assistance Available</Badge>
                            <Badge variant="outline">Job Placement Support</Badge>
                          </div>
                        </CardContent>
                        <CardFooter>
                          <Button asChild>
                            <Link href="https://www.masscec.com/workforce" target="_blank" rel="noopener noreferrer">
                              Visit MassCEC Website
                            </Link>
                          </Button>
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
