'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Copy, Check } from 'lucide-react';
import MainLayout from '@/components/layout/MainLayout';
import { useToast } from '@/components/ui/use-toast';

/**
 * API Documentation Page
 * 
 * Provides comprehensive documentation for the Climate Economy Ecosystem API
 */
export default function ApiDocsPage() {
  const { toast } = useToast();
  const [copiedEndpoint, setCopiedEndpoint] = useState(null);
  
  const copyToClipboard = (text, endpointId) => {
    navigator.clipboard.writeText(text);
    setCopiedEndpoint(endpointId);
    
    toast({
      title: "Copied to clipboard",
      description: "The endpoint URL has been copied to your clipboard.",
    });
    
    setTimeout(() => {
      setCopiedEndpoint(null);
    }, 2000);
  };
  
  const endpoints = [
    {
      id: "health",
      name: "Health Check",
      method: "GET",
      url: "/api/health",
      description: "Check the health status of the application and its dependencies.",
      parameters: [],
      responses: [
        { 
          status: 200, 
          description: "All systems operational", 
          example: `{
  "status": "ok",
  "uptime": 3600,
  "timestamp": "2023-06-15T14:30:00Z",
  "services": {
    "database": {
      "status": "ok",
      "latency": "45ms"
    },
    "openai": {
      "status": "ok",
      "latency": "120ms"
    },
    "storage": {
      "status": "ok",
      "latency": "35ms"
    }
  },
  "responseTime": "210ms"
}`
        },
        { 
          status: 503, 
          description: "One or more services degraded", 
          example: `{
  "status": "degraded",
  "uptime": 3600,
  "timestamp": "2023-06-15T14:30:00Z",
  "services": {
    "database": {
      "status": "ok",
      "latency": "45ms"
    },
    "openai": {
      "status": "error",
      "message": "API key invalid",
      "latency": "120ms"
    },
    "storage": {
      "status": "ok",
      "latency": "35ms"
    }
  },
  "responseTime": "210ms"
}`
        }
      ]
    },
    {
      id: "jobs-recommendations",
      name: "Job Recommendations",
      method: "GET",
      url: "/api/jobs/recommendations",
      description: "Get personalized job recommendations from member companies based on user profile.",
      parameters: [
        { name: "userId", type: "string", required: true, description: "The user ID to get recommendations for" }
      ],
      responses: [
        { 
          status: 200, 
          description: "Successful response", 
          example: `{
  "recommendations": [
    {
      "job": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Solar Installer",
        "company": {
          "name": "Solect Energy",
          "logo_url": "/images/companies/solect.png"
        },
        "location": "Boston, MA",
        "job_type": "Full-time",
        "experience_level": "Entry",
        "required_skills": ["Solar PV", "Electrical"],
        "preferred_skills": ["NABCEP Certification", "Construction"]
      },
      "score": 0.85,
      "skill_gaps": ["NABCEP Certification"]
    }
  ]
}`
        },
        { 
          status: 401, 
          description: "Unauthorized", 
          example: `{
  "error": "Unauthorized"
}`
        }
      ]
    },
    {
      id: "internships-masscec",
      name: "MassCEC Internships",
      method: "GET",
      url: "/api/internships/masscec",
      description: "Get active MassCEC internship programs.",
      parameters: [],
      responses: [
        { 
          status: 200, 
          description: "Successful response", 
          example: `{
  "programs": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Clean Energy Internship Program",
      "description": "Connects students and recent graduates with clean energy employers",
      "application_period": "Spring 2023",
      "duration": "10-12 weeks",
      "stipend_amount": "$15-$25/hour",
      "eligibility_criteria": ["Massachusetts resident", "Enrolled in college/university"]
    }
  ]
}`
        }
      ]
    },
    {
      id: "profile-resume-analyze",
      name: "Resume Analysis",
      method: "POST",
      url: "/api/profile/resume/analyze",
      description: "Analyze a resume to extract skills, experience, education, and social links.",
      parameters: [
        { name: "userId", type: "string", required: true, description: "The user ID" },
        { name: "resumeUrl", type: "string", required: true, description: "URL to the uploaded resume" },
        { name: "fileType", type: "string", required: true, description: "File extension (pdf, docx, etc.)" }
      ],
      requestBody: `{
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "resumeUrl": "https://storage.example.com/resumes/user-123.pdf",
  "fileType": "pdf"
}`,
      responses: [
        { 
          status: 200, 
          description: "Successful response", 
          example: `{
  "success": true,
  "profileUpdated": true,
  "extractedData": {
    "skills": {
      "technical": ["Solar PV Installation", "Electrical Wiring"],
      "soft": ["Communication", "Teamwork"],
      "transferable": ["Project Management", "Customer Service"]
    },
    "education": [
      {
        "institution": "University of Massachusetts",
        "degree": "Bachelor of Science",
        "fieldOfStudy": "Electrical Engineering",
        "startDate": "2016",
        "endDate": "2020"
      }
    ],
    "social_links": {
      "linkedin": "linkedin.com/in/johndoe",
      "github": "github.com/johndoe"
    }
  }
}`
        },
        { 
          status: 400, 
          description: "Bad request", 
          example: `{
  "error": "Missing required parameters"
}`
        }
      ]
    },
    {
      id: "profile-verifications",
      name: "Profile Verifications",
      method: "GET",
      url: "/api/profile/verifications",
      description: "Get pending verification items for a user.",
      parameters: [
        { name: "userId", type: "string", required: true, description: "The user ID" }
      ],
      responses: [
        { 
          status: 200, 
          description: "Successful response", 
          example: `{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "category": "social_link",
      "subcategory": "linkedin",
      "value": "linkedin.com/in/johndoe",
      "verified": false,
      "createdAt": "2023-06-15T14:30:00Z"
    }
  ]
}`
        }
      ]
    },
    {
      id: "profile-verify-item",
      name: "Verify Profile Item",
      method: "POST",
      url: "/api/profile/verify-item",
      description: "Verify or correct a profile item.",
      parameters: [],
      requestBody: `{
  "verificationId": "123e4567-e89b-12d3-a456-426614174000",
  "isCorrect": true,
  "correctedValue": null
}`,
      responses: [
        { 
          status: 200, 
          description: "Successful response", 
          example: `{
  "success": true,
  "verified": true
}`
        }
      ]
    }
  ];
  
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">API Documentation</h1>
        
        <p className="text-gray-600 mb-8">
          This documentation provides information about the Climate Economy Ecosystem API endpoints.
          All endpoints require authentication unless otherwise specified.
        </p>
        
        <Tabs defaultValue="health">
          <TabsList className="mb-6">
            {endpoints.map(endpoint => (
              <TabsTrigger key={endpoint.id} value={endpoint.id}>
                {endpoint.name}
              </TabsTrigger>
            ))}
          </TabsList>
          
          {endpoints.map(endpoint => (
            <TabsContent key={endpoint.id} value={endpoint.id}>
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">{endpoint.name}</h2>
                  <Badge variant={endpoint.method === 'GET' ? 'secondary' : 'default'}>
                    {endpoint.method}
                  </Badge>
                </div>
                
                <p className="text-gray-600 mb-4">{endpoint.description}</p>
                
                <div className="flex items-center mb-6 bg-gray-100 p-3 rounded-md">
                  <code className="text-sm font-mono flex-1">
                    {endpoint.method} {endpoint.url}
                  </code>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => copyToClipboard(`${window.location.origin}${endpoint.url}`, endpoint.id)}
                  >
                    {copiedEndpoint === endpoint.id ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                
                {endpoint.parameters.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-2">Parameters</h3>
                    <div className="bg-gray-50 rounded-md p-4">
                      <table className="min-w-full">
                        <thead>
                          <tr>
                            <th className="text-left text-sm font-medium text-gray-500 pb-2">Name</th>
                            <th className="text-left text-sm font-medium text-gray-500 pb-2">Type</th>
                            <th className="text-left text-sm font-medium text-gray-500 pb-2">Required</th>
                            <th className="text-left text-sm font-medium text-gray-500 pb-2">Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {endpoint.parameters.map((param, index) => (
                            <tr key={index} className="border-t border-gray-200">
                              <td className="py-2 text-sm font-mono">{param.name}</td>
                              <td className="py-2 text-sm">{param.type}</td>
                              <td className="py-2 text-sm">{param.required ? 'Yes' : 'No'}</td>
                              <td className="py-2 text-sm">{param.description}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {endpoint.requestBody && (
                  <div className="mb-6">
                    <h3 className="text-lg font-medium mb-2">Request Body</h3>
                    <div className="bg-gray-50 rounded-md p-4">
                      <pre className="text-sm font-mono whitespace-pre-wrap">{endpoint.requestBody}</pre>
                    </div>
                  </div>
                )}
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Responses</h3>
                  {endpoint.responses.map((response, index) => (
                    <div key={index} className="mb-4">
                      <div className="flex items-center mb-2">
                        <Badge variant={response.status === 200 ? 'outline' : 'destructive'}>
                          {response.status}
                        </Badge>
                        <span className="ml-2 text-sm text-gray-600">{response.description}</span>
                      </div>
                      <div className="bg-gray-50 rounded-md p-4">
                        <pre className="text-sm font-mono whitespace-pre-wrap">{response.example}</pre>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </MainLayout>
  );
}
