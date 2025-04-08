'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  User, 
  Mail, 
  MapPin, 
  Phone, 
  Briefcase, 
  GraduationCap, 
  Award, 
  FileText,
  Edit,
  Download,
  Share2,
  TrendingUp,
  BarChart4,
  CheckCircle,
  Github
} from 'lucide-react';
import Link from 'next/link';

// Sample user data
const userData = {
  id: 'user123',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  location: 'Boston, MA',
  phone: '(617) 555-1234',
  avatar: '/placeholder-avatar.jpg',
  title: 'Renewable Energy Specialist',
  about: 'Experienced renewable energy professional with a focus on solar PV systems and energy efficiency. Passionate about advancing clean energy solutions in Massachusetts.',
  climateEconomyScore: 78,
  skills: [
    { name: 'Solar PV Installation', level: 'Advanced', verified: true },
    { name: 'Energy Auditing', level: 'Intermediate', verified: true },
    { name: 'Project Management', level: 'Advanced', verified: true },
    { name: 'Electrical Systems', level: 'Intermediate', verified: false },
    { name: 'Building Science', level: 'Beginner', verified: false },
    { name: 'Customer Relations', level: 'Advanced', verified: true }
  ],
  experience: [
    {
      title: 'Solar Installation Team Lead',
      company: 'Boston Solar Solutions',
      location: 'Boston, MA',
      startDate: 'Jan 2020',
      endDate: 'Present',
      description: 'Lead a team of solar installers on residential and commercial projects throughout Massachusetts. Manage project timelines, client communications, and quality control.'
    },
    {
      title: 'Energy Auditor',
      company: 'Mass Energy Efficiency',
      location: 'Cambridge, MA',
      startDate: 'Mar 2018',
      endDate: 'Dec 2019',
      description: 'Conducted comprehensive energy audits for residential and small commercial properties. Provided recommendations for energy efficiency improvements and renewable energy solutions.'
    }
  ],
  education: [
    {
      degree: 'Bachelor of Science in Environmental Engineering',
      institution: 'University of Massachusetts Amherst',
      location: 'Amherst, MA',
      year: '2018'
    },
    {
      degree: 'Solar PV Installer Certification',
      institution: 'North American Board of Certified Energy Practitioners (NABCEP)',
      location: 'Online',
      year: '2019'
    }
  ],
  certifications: [
    {
      name: 'NABCEP PV Installation Professional',
      issuer: 'North American Board of Certified Energy Practitioners',
      date: 'May 2019',
      expires: 'May 2022'
    },
    {
      name: 'BPI Building Analyst',
      issuer: 'Building Performance Institute',
      date: 'August 2018',
      expires: 'August 2021'
    }
  ],
  jobMatches: [
    {
      title: 'Senior Solar Installer',
      company: 'SunPower Massachusetts',
      location: 'Worcester, MA',
      matchScore: 92,
      salary: '$75,000 - $85,000',
      posted: '3 days ago'
    },
    {
      title: 'Renewable Energy Project Manager',
      company: 'Clean Energy Collective',
      location: 'Boston, MA',
      matchScore: 87,
      salary: '$80,000 - $95,000',
      posted: '1 week ago'
    },
    {
      title: 'Energy Efficiency Consultant',
      company: 'Mass Save',
      location: 'Springfield, MA',
      matchScore: 84,
      salary: '$70,000 - $80,000',
      posted: '2 days ago'
    }
  ],
  skillGaps: [
    {
      skill: 'Battery Storage Systems',
      demandLevel: 'High',
      trainingOptions: [
        { name: 'Energy Storage Certificate', provider: 'MassCEC', duration: '8 weeks' },
        { name: 'Battery Systems Fundamentals', provider: 'UMass Clean Energy Extension', duration: '4 weeks' }
      ]
    },
    {
      skill: 'Energy Modeling Software',
      demandLevel: 'Medium',
      trainingOptions: [
        { name: 'Energy Modeling with EnergyPlus', provider: 'Boston Architectural College', duration: '6 weeks' },
        { name: 'Building Energy Simulation', provider: 'Northeastern University', duration: '10 weeks' }
      ]
    }
  ],
  careerPathways: [
    {
      title: 'Solar Operations Manager',
      timeframe: '1-2 years',
      requiredSkills: ['Team Management', 'Operations Planning', 'Quality Control'],
      salaryRange: '$85,000 - $100,000'
    },
    {
      title: 'Renewable Energy Director',
      timeframe: '3-5 years',
      requiredSkills: ['Strategic Planning', 'Budget Management', 'Business Development'],
      salaryRange: '$100,000 - $130,000'
    }
  ],
  github: 'github.com/alexjohnson',
  linkedin: 'linkedin.com/in/alexjohnson'
};

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <h1 className="text-3xl font-bold">My Profile</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Profile
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button size="sm" onClick={() => setIsEditing(!isEditing)}>
            <Edit className="h-4 w-4 mr-2" />
            {isEditing ? 'Save Changes' : 'Edit Profile'}
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left column - Profile summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex justify-between">
                <Avatar className="h-20 w-20">
                  <AvatarImage src={userData.avatar} alt={userData.name} />
                  <AvatarFallback>{userData.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <Badge className="h-fit">Verified Profile</Badge>
              </div>
              <CardTitle className="text-2xl mt-4">{userData.name}</CardTitle>
              <CardDescription className="text-lg">{userData.title}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center">
                <Mail className="h-4 w-4 mr-2 text-muted-foreground" />
                <span>{userData.email}</span>
              </div>
              <div className="flex items-center">
                <MapPin className="h-4 w-4 mr-2 text-muted-foreground" />
                <span>{userData.location}</span>
              </div>
              <div className="flex items-center">
                <Phone className="h-4 w-4 mr-2 text-muted-foreground" />
                <span>{userData.phone}</span>
              </div>
              <div className="flex items-center">
                <Github className="h-4 w-4 mr-2 text-muted-foreground" />
                <a href={`https://${userData.github}`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  {userData.github}
                </a>
              </div>
              
              <div className="pt-4 border-t">
                <h3 className="font-semibold mb-2">About Me</h3>
                <p className="text-sm text-muted-foreground">{userData.about}</p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Climate Economy Fit</CardTitle>
              <CardDescription>Your match to the Massachusetts clean energy economy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Overall Score</span>
                  <span className="text-sm font-medium">{userData.climateEconomyScore}/100</span>
                </div>
                <Progress value={userData.climateEconomyScore} className="h-3" />
              </div>
              
              <div className="pt-4 space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Skills Match</span>
                    <span className="text-sm font-medium">82%</span>
                  </div>
                  <Progress value={82} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Experience Match</span>
                    <span className="text-sm font-medium">75%</span>
                  </div>
                  <Progress value={75} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Location Match</span>
                    <span className="text-sm font-medium">95%</span>
                  </div>
                  <Progress value={95} className="h-2" />
                </div>
              </div>
              
              <Button variant="outline" className="w-full" asChild>
                <Link href="/profile/enhance">
                  Enhance Your Profile
                </Link>
              </Button>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Top Skills</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {userData.skills.slice(0, 5).map((skill, index) => (
                <div key={index}>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center">
                      <span className="text-sm font-medium">{skill.name}</span>
                      {skill.verified && (
                        <CheckCircle className="h-3 w-3 ml-2 text-green-600" />
                      )}
                    </div>
                    <Badge variant="outline">{skill.level}</Badge>
                  </div>
                  <Progress 
                    value={skill.level === 'Advanced' ? 90 : skill.level === 'Intermediate' ? 65 : 40} 
                    className="h-2" 
                  />
                </div>
              ))}
              
              <Button variant="outline" className="w-full" asChild>
                <Link href="/profile/skills">
                  View All Skills
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
        
        {/* Right column - Detailed information */}
        <div className="md:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <Tabs defaultValue="experience" className="w-full">
                <TabsList className="w-full justify-start">
                  <TabsTrigger value="experience">Experience</TabsTrigger>
                  <TabsTrigger value="education">Education</TabsTrigger>
                  <TabsTrigger value="certifications">Certifications</TabsTrigger>
                  <TabsTrigger value="job-matches">Job Matches</TabsTrigger>
                  <TabsTrigger value="career-path">Career Path</TabsTrigger>
                </TabsList>
              </Tabs>
            </CardHeader>
            
            <CardContent>
              <Tabs defaultValue="experience">
                <TabsContent value="experience" className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Work Experience</h3>
                    {isEditing && (
                      <Button size="sm" variant="outline">
                        Add Experience
                      </Button>
                    )}
                  </div>
                  
                  {userData.experience.map((exp, index) => (
                    <Card key={index}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle>{exp.title}</CardTitle>
                            <CardDescription>{exp.company} • {exp.location}</CardDescription>
                          </div>
                          <Badge variant="outline">{exp.startDate} - {exp.endDate}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground">{exp.description}</p>
                      </CardContent>
                      {isEditing && (
                        <CardFooter>
                          <Button size="sm" variant="outline">Edit</Button>
                        </CardFooter>
                      )}
                    </Card>
                  ))}
                </TabsContent>
                
                <TabsContent value="education" className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Education</h3>
                    {isEditing && (
                      <Button size="sm" variant="outline">
                        Add Education
                      </Button>
                    )}
                  </div>
                  
                  {userData.education.map((edu, index) => (
                    <Card key={index}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle>{edu.degree}</CardTitle>
                            <CardDescription>{edu.institution} • {edu.location}</CardDescription>
                          </div>
                          <Badge variant="outline">{edu.year}</Badge>
                        </div>
                      </CardHeader>
                      {isEditing && (
                        <CardFooter>
                          <Button size="sm" variant="outline">Edit</Button>
                        </CardFooter>
                      )}
                    </Card>
                  ))}
                </TabsContent>
                
                <TabsContent value="certifications" className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Certifications</h3>
                    {isEditing && (
                      <Button size="sm" variant="outline">
                        Add Certification
                      </Button>
                    )}
                  </div>
                  
                  {userData.certifications.map((cert, index) => (
                    <Card key={index}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle>{cert.name}</CardTitle>
                            <CardDescription>{cert.issuer}</CardDescription>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline">Issued: {cert.date}</Badge>
                            <div className="text-xs text-muted-foreground mt-1">Expires: {cert.expires}</div>
                          </div>
                        </div>
                      </CardHeader>
                      {isEditing && (
                        <CardFooter>
                          <Button size="sm" variant="outline">Edit</Button>
                        </CardFooter>
                      )}
                    </Card>
                  ))}
                </TabsContent>
                
                <TabsContent value="job-matches" className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Top Job Matches</h3>
                    <Button variant="outline" size="sm" asChild>
                      <Link href="/jobs">
                        View All Jobs
                      </Link>
                    </Button>
                  </div>
                  
                  {userData.jobMatches.map((job, index) => (
                    <Card key={index}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle>{job.title}</CardTitle>
                            <CardDescription>{job.company} • {job.location}</CardDescription>
                          </div>
                          <Badge className="bg-green-600">{job.matchScore}% Match</Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="pb-2">
                        <div className="flex justify-between text-sm">
                          <span>{job.salary}</span>
                          <span className="text-muted-foreground">Posted {job.posted}</span>
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button size="sm">View Job</Button>
                      </CardFooter>
                    </Card>
                  ))}
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Skill Gaps</CardTitle>
                      <CardDescription>
                        Addressing these skill gaps could increase your job match scores
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {userData.skillGaps.map((gap, index) => (
                        <div key={index} className="border-b pb-4 last:border-0 last:pb-0">
                          <div className="flex justify-between mb-2">
                            <span className="font-medium">{gap.skill}</span>
                            <Badge variant="outline">{gap.demandLevel} Demand</Badge>
                          </div>
                          <div className="space-y-2">
                            {gap.trainingOptions.map((option, i) => (
                              <div key={i} className="flex justify-between items-center text-sm">
                                <div>
                                  <span className="font-medium">{option.name}</span>
                                  <div className="text-muted-foreground">{option.provider} • {option.duration}</div>
                                </div>
                                <Button size="sm" variant="outline">Learn More</Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="career-path" className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Career Pathways</h3>
                    <Button variant="outline" size="sm" asChild>
                      <Link href="/career-paths">
                        Explore More Paths
                      </Link>
                    </Button>
                  </div>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Your Career Trajectory</CardTitle>
                      <CardDescription>
                        Based on your skills and experience, here are potential career paths in the clean energy sector
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {userData.careerPathways.map((path, index) => (
                        <div key={index} className="border-b pb-6 last:border-0 last:pb-0">
                          <div className="flex justify-between mb-2">
                            <CardTitle className="text-lg">{path.title}</CardTitle>
                            <Badge variant="outline">{path.timeframe}</Badge>
                          </div>
                          <div className="space-y-4">
                            <div>
                              <h4 className="text-sm font-medium mb-2">Required Skills</h4>
                              <div className="flex flex-wrap gap-2">
                                {path.requiredSkills.map((skill, i) => (
                                  <Badge key={i} variant="secondary">{skill}</Badge>
                                ))}
                              </div>
                            </div>
                            <div className="flex justify-between items-center">
                              <div>
                                <h4 className="text-sm font-medium">Salary Range</h4>
                                <div className="text-lg font-bold">{path.salaryRange}</div>
                              </div>
                              <Button>View Path Details</Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Industry Growth Trends</CardTitle>
                      <CardDescription>
                        Clean energy sector growth in Massachusetts
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm text-muted-foreground">Solar Industry</div>
                          <div className="flex items-center">
                            <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                            <span className="font-bold text-green-600">+24.5% growth</span>
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-muted-foreground">Energy Efficiency</div>
                          <div className="flex items-center">
                            <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                            <span className="font-bold text-green-600">+18.2% growth</span>
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-muted-foreground">Clean Transportation</div>
                          <div className="flex items-center">
                            <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                            <span className="font-bold text-green-600">+32.1% growth</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="pt-4">
                        <Button variant="outline" className="w-full" asChild>
                          <Link href="/sectors">
                            <BarChart4 className="h-4 w-4 mr-2" />
                            View Detailed Industry Analysis
                          </Link>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
