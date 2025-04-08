'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  MapPin, 
  Calendar, 
  Users, 
  Building, 
  GraduationCap, 
  Briefcase,
  ArrowRight,
  ExternalLink,
  CheckCircle,
  Info
} from 'lucide-react';
import Link from 'next/link';

// Sample EJ communities data
const ejCommunities = [
  {
    id: 'lawrence',
    name: 'Lawrence',
    population: 89143,
    medianIncome: 44613,
    unemploymentRate: 7.8,
    cleanEnergyJobs: 450,
    programs: [
      {
        id: 'lawrence-green-jobs',
        name: 'Lawrence Green Jobs Academy',
        type: 'Training',
        organization: 'Groundwork Lawrence',
        description: 'A 12-week training program focused on preparing residents for careers in solar installation, energy efficiency, and green building.',
        eligibility: 'Lawrence residents, priority for low-income individuals',
        nextSession: 'September 15, 2023',
        contact: 'greenjobs@groundworklawrence.org'
      },
      {
        id: 'lawrence-weatherization',
        name: 'Lawrence Home Weatherization Assistance',
        type: 'Financial Assistance',
        organization: 'Community Action, Inc.',
        description: 'Provides free weatherization services to income-eligible households, while creating jobs for local residents in energy efficiency.',
        eligibility: 'Income below 60% of state median income',
        nextSession: 'Ongoing',
        contact: 'weatherization@communityactioninc.org'
      }
    ],
    employers: [
      {
        name: 'Solectria Renewables',
        industry: 'Solar Manufacturing',
        jobCount: 120,
        hiringNow: true
      },
      {
        name: 'Groundwork Lawrence',
        industry: 'Environmental Services',
        jobCount: 45,
        hiringNow: true
      }
    ]
  },
  {
    id: 'holyoke',
    name: 'Holyoke',
    population: 40117,
    medianIncome: 42707,
    unemploymentRate: 8.2,
    cleanEnergyJobs: 380,
    programs: [
      {
        id: 'holyoke-clean-energy',
        name: 'Holyoke Clean Energy Corps',
        type: 'Training & Employment',
        organization: 'Holyoke Community College',
        description: 'A workforce development program that trains residents for clean energy jobs while completing energy efficiency projects in the community.',
        eligibility: 'Holyoke residents, priority for those from low-income neighborhoods',
        nextSession: 'October 1, 2023',
        contact: 'cleanenergy@hcc.edu'
      }
    ],
    employers: [
      {
        name: 'Holyoke Gas & Electric',
        industry: 'Utility',
        jobCount: 85,
        hiringNow: true
      }
    ]
  },
  {
    id: 'chelsea',
    name: 'Chelsea',
    population: 40160,
    medianIncome: 56802,
    unemploymentRate: 6.9,
    cleanEnergyJobs: 210,
    programs: [
      {
        id: 'chelsea-resilience',
        name: 'Chelsea Climate Resilience Corps',
        type: 'Training & Employment',
        organization: 'GreenRoots Chelsea',
        description: 'Trains residents in climate resilience strategies, green infrastructure, and clean energy technologies while implementing community projects.',
        eligibility: 'Chelsea residents, priority for environmental justice neighborhoods',
        nextSession: 'January 15, 2024',
        contact: 'resilience@greenrootschelsea.org'
      }
    ],
    employers: [
      {
        name: 'Eastern Salt Company',
        industry: 'Sustainable Infrastructure',
        jobCount: 65,
        hiringNow: false
      }
    ]
  }
];

// Sample resources data
const resources = [
  {
    id: 'masscec-equity',
    name: 'MassCEC Equity Workforce Program',
    type: 'Funding & Training',
    organization: 'Massachusetts Clean Energy Center',
    description: 'Provides funding and support for clean energy job training programs that serve environmental justice communities and underrepresented groups.',
    eligibility: 'Organizations serving EJ communities',
    website: 'https://www.masscec.com/equity',
    contact: 'equity@masscec.com'
  },
  {
    id: 'ej-workforce',
    name: 'Environmental Justice Workforce Development Grant',
    type: 'Grant',
    organization: 'Massachusetts Executive Office of Energy and Environmental Affairs',
    description: 'Grants to support workforce development programs in clean energy, climate adaptation, and environmental fields for residents of EJ communities.',
    eligibility: 'Non-profits, educational institutions, and municipalities',
    website: 'https://www.mass.gov/environmental-justice',
    contact: 'ej.grants@mass.gov'
  },
  {
    id: 'clean-energy-internship',
    name: 'Clean Energy Internship Program',
    type: 'Internship',
    organization: 'Massachusetts Clean Energy Center',
    description: 'Paid internships with Massachusetts clean energy companies, with dedicated spots for students from environmental justice communities.',
    eligibility: 'Students and recent graduates from Massachusetts',
    website: 'https://www.masscec.com/internship',
    contact: 'internship@masscec.com'
  }
];

export default function EJCommunitySupport() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCommunity, setSelectedCommunity] = useState(ejCommunities[0]);
  
  // Filter communities based on search query
  const filteredCommunities = searchQuery 
    ? ejCommunities.filter(community => 
        community.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : ejCommunities;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Environmental Justice Community Support</h1>
        <p className="text-muted-foreground mt-2">
          Resources, programs, and opportunities for clean energy careers in Massachusetts Environmental Justice communities.
        </p>
      </div>
      
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
        <Input 
          placeholder="Search for your community..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>
      
      <div className="flex flex-col md:flex-row gap-6">
        {/* Communities list */}
        <div className="md:w-1/3 space-y-4">
          <h2 className="text-2xl font-bold">EJ Communities</h2>
          
          {filteredCommunities.map(community => (
            <Card 
              key={community.id}
              className={`cursor-pointer transition-all ${selectedCommunity.id === community.id ? 'border-primary ring-1 ring-primary' : 'hover:border-primary/50'}`}
              onClick={() => setSelectedCommunity(community)}
            >
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <CardTitle>{community.name}</CardTitle>
                  <Badge variant="outline" className="flex items-center">
                    <Briefcase className="h-3 w-3 mr-1" />
                    {community.cleanEnergyJobs} jobs
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Population:</span>
                  <span>{community.population.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Median Income:</span>
                  <span>${community.medianIncome.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Unemployment:</span>
                  <span>{community.unemploymentRate}%</span>
                </div>
              </CardContent>
            </Card>
          ))}
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What is an EJ Community?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Environmental Justice (EJ) communities in Massachusetts are neighborhoods that meet specific criteria related to income, 
                minority population, and English language proficiency.
              </p>
              <p className="text-sm text-muted-foreground">
                These communities often face disproportionate environmental burdens and have historically had less access to economic opportunities 
                in growing sectors like clean energy.
              </p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" size="sm" asChild>
                <Link href="https://www.mass.gov/environmental-justice" target="_blank" rel="noopener noreferrer">
                  Learn More <ExternalLink className="h-3 w-3 ml-1" />
                </Link>
              </Button>
            </CardFooter>
          </Card>
        </div>
        
        {/* Community details */}
        <div className="md:w-2/3">
          <Card className="h-full">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-2xl">{selectedCommunity.name}</CardTitle>
                  <CardDescription className="mt-2">
                    Environmental Justice community with {selectedCommunity.cleanEnergyJobs} clean energy jobs
                  </CardDescription>
                </div>
                <Button asChild>
                  <Link href={`/communities/${selectedCommunity.id}`}>
                    Community Profile <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            
            <CardContent>
              <Tabs defaultValue="programs">
                <TabsList className="mb-4">
                  <TabsTrigger value="programs">Programs</TabsTrigger>
                  <TabsTrigger value="employers">Employers</TabsTrigger>
                  <TabsTrigger value="resources">Resources</TabsTrigger>
                </TabsList>
                
                <TabsContent value="programs" className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Local Programs</h3>
                    <Button variant="outline" size="sm" asChild>
                      <Link href="/programs">
                        View All Programs
                      </Link>
                    </Button>
                  </div>
                  
                  {selectedCommunity.programs.map(program => (
                    <Card key={program.id}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle>{program.name}</CardTitle>
                            <CardDescription>{program.organization}</CardDescription>
                          </div>
                          <Badge>{program.type}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="pb-2">
                        <p className="text-sm text-muted-foreground mb-4">{program.description}</p>
                        
                        <div className="space-y-2">
                          <div className="flex items-start">
                            <Users className="h-4 w-4 mr-2 mt-0.5 text-muted-foreground" />
                            <div>
                              <span className="text-sm font-medium">Eligibility:</span>
                              <span className="text-sm text-muted-foreground ml-2">{program.eligibility}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <Calendar className="h-4 w-4 mr-2 mt-0.5 text-muted-foreground" />
                            <div>
                              <span className="text-sm font-medium">Next Session:</span>
                              <span className="text-sm text-muted-foreground ml-2">{program.nextSession}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-start">
                            <Mail className="h-4 w-4 mr-2 mt-0.5 text-muted-foreground" />
                            <div>
                              <span className="text-sm font-medium">Contact:</span>
                              <span className="text-sm text-muted-foreground ml-2">{program.contact}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button size="sm">Apply Now</Button>
                      </CardFooter>
                    </Card>
                  ))}
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Statewide Programs</CardTitle>
                      <CardDescription>
                        These programs are available to residents of all Environmental Justice communities in Massachusetts
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {resources.map(resource => (
                        <div key={resource.id} className="flex justify-between items-center border-b pb-4 last:border-0 last:pb-0">
                          <div>
                            <div className="font-medium">{resource.name}</div>
                            <div className="text-sm text-muted-foreground">{resource.organization}</div>
                          </div>
                          <Button size="sm" variant="outline" asChild>
                            <Link href={`/resources/${resource.id}`}>
                              View Details
                            </Link>
                          </Button>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="employers" className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Local Employers</h3>
                    <Button variant="outline" size="sm" asChild>
                      <Link href="/employers">
                        View All Employers
                      </Link>
                    </Button>
                  </div>
                  
                  {selectedCommunity.employers.map((employer, index) => (
                    <Card key={index}>
                      <CardHeader className="pb-2">
                        <div className="flex justify-between">
                          <div>
                            <CardTitle>{employer.name}</CardTitle>
                            <CardDescription>{employer.industry}</CardDescription>
                          </div>
                          {employer.hiringNow && (
                            <Badge className="bg-green-600">Hiring Now</Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="pb-2">
                        <div className="flex justify-between text-sm">
                          <span>
                            <span className="text-muted-foreground">Clean Energy Jobs: </span>
                            <span className="font-medium">{employer.jobCount}</span>
                          </span>
                          <span className="text-muted-foreground">Located in {selectedCommunity.name}</span>
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button size="sm">View Jobs</Button>
                      </CardFooter>
                    </Card>
                  ))}
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Regional Employers</CardTitle>
                      <CardDescription>
                        These employers hire from multiple communities in the region
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex justify-between items-center border-b pb-4">
                        <div>
                          <div className="font-medium">Eversource</div>
                          <div className="text-sm text-muted-foreground">Utility</div>
                        </div>
                        <Badge variant="outline">25 miles away</Badge>
                      </div>
                      <div className="flex justify-between items-center border-b pb-4">
                        <div>
                          <div className="font-medium">MassCEC</div>
                          <div className="text-sm text-muted-foreground">Government Agency</div>
                        </div>
                        <Badge variant="outline">30 miles away</Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium">Boston Solar</div>
                          <div className="text-sm text-muted-foreground">Solar Installation</div>
                        </div>
                        <Badge variant="outline">15 miles away</Badge>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button variant="outline" size="sm" asChild>
                        <Link href="/employers">
                          View All Regional Employers
                        </Link>
                      </Button>
                    </CardFooter>
                  </Card>
                </TabsContent>
                
                <TabsContent value="resources" className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Support Resources</h3>
                    <Button variant="outline" size="sm" asChild>
                      <Link href="/resources">
                        View All Resources
                      </Link>
                    </Button>
                  </div>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Transportation Assistance</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-4">
                        Transportation support for residents of {selectedCommunity.name} attending clean energy training programs or job interviews.
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Public transit passes</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Ride-sharing credits</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Carpooling coordination</span>
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button size="sm">Apply for Assistance</Button>
                    </CardFooter>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Childcare Support</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-4">
                        Childcare assistance for parents attending clean energy training programs or starting new jobs in the sector.
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Childcare vouchers</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">On-site childcare at select training locations</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Extended hours childcare for evening classes</span>
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button size="sm">Apply for Assistance</Button>
                    </CardFooter>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Financial Support</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-4">
                        Financial assistance programs to help residents of {selectedCommunity.name} pursue clean energy careers.
                      </p>
                      <div className="space-y-2">
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Training stipends</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Tool and equipment grants</span>
                        </div>
                        <div className="flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                          <span className="text-sm">Certification exam fee waivers</span>
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button size="sm">Apply for Assistance</Button>
                    </CardFooter>
                  </Card>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Success Stories</CardTitle>
          <CardDescription>
            Residents from Environmental Justice communities who have built successful careers in clean energy
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Maria Rodriguez</CardTitle>
              <CardDescription>Lawrence, MA</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                "After completing the Lawrence Green Jobs Academy program, I was hired as a solar installer. 
                Three years later, I'm now a team lead managing installation projects across the region."
              </p>
              <div className="text-sm">
                <div className="font-medium">Current Role:</div>
                <div className="text-muted-foreground">Solar Installation Team Lead at Boston Solar</div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">James Washington</CardTitle>
              <CardDescription>Chelsea, MA</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                "The Chelsea Climate Resilience Corps gave me the skills and connections to start my career in energy efficiency. 
                The support services helped me balance training with family responsibilities."
              </p>
              <div className="text-sm">
                <div className="font-medium">Current Role:</div>
                <div className="text-muted-foreground">Energy Auditor at Mass Save</div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">David Nguyen</CardTitle>
              <CardDescription>Holyoke, MA</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                "Starting with an internship through the MassCEC program, I gained experience in wind energy operations. 
                Now I'm pursuing an engineering degree while working full-time in the industry."
              </p>
              <div className="text-sm">
                <div className="font-medium">Current Role:</div>
                <div className="text-muted-foreground">Wind Turbine Technician at Berkshire Wind Power</div>
              </div>
            </CardContent>
          </Card>
        </CardContent>
        <CardFooter>
          <Button variant="outline" asChild>
            <Link href="/success-stories">
              Read More Success Stories
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
