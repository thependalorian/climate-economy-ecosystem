import { NextResponse } from 'next/server';

/**
 * Jobs Search API
 * Handles search requests for job opportunities
 * Location: /app/api/jobs/search/route.js
 */

// Mock job data for demonstration
const MOCK_JOBS = [
  {
    id: '1',
    title: 'Solar Panel Installer',
    company: 'SunPower Solutions',
    location: 'Boston, MA',
    type: 'Full-time',
    salary: '$50,000 - $65,000',
    description: 'Looking for experienced solar panel installers to join our growing team in Boston.',
    skills: ['Solar Installation', 'Electrical Work', 'Safety Protocols'],
    posted_date: '2023-10-15',
    is_ej_friendly: true,
    is_veteran_friendly: true
  },
  {
    id: '2',
    title: 'Energy Efficiency Consultant',
    company: 'GreenBuild Partners',
    location: 'Worcester, MA',
    type: 'Full-time',
    salary: '$60,000 - $75,000',
    description: 'Help businesses and homes reduce their energy consumption through expert consultation.',
    skills: ['Energy Auditing', 'Building Science', 'Customer Service'],
    posted_date: '2023-10-12',
    is_ej_friendly: true,
    is_veteran_friendly: false
  },
  {
    id: '3',
    title: 'Offshore Wind Technician',
    company: 'WindStream Energy',
    location: 'New Bedford, MA',
    type: 'Full-time',
    salary: '$70,000 - $85,000',
    description: 'Maintain and repair offshore wind turbines along the Massachusetts coast.',
    skills: ['Mechanical Repair', 'Wind Turbine Systems', 'Safety Training'],
    posted_date: '2023-10-10',
    is_ej_friendly: false,
    is_veteran_friendly: true
  },
  {
    id: '4',
    title: 'Electric Vehicle Charging Station Installer',
    company: 'Volt Infrastructure',
    location: 'Springfield, MA',
    type: 'Full-time',
    salary: '$55,000 - $70,000',
    description: 'Install and maintain EV charging stations throughout Western Massachusetts.',
    skills: ['Electrical Systems', 'EV Technology', 'Construction'],
    posted_date: '2023-10-08',
    is_ej_friendly: true,
    is_veteran_friendly: true
  },
  {
    id: '5',
    title: 'Heat Pump Specialist',
    company: 'Comfort Climate Solutions',
    location: 'Lowell, MA',
    type: 'Full-time',
    salary: '$60,000 - $80,000',
    description: 'Specialize in the installation and maintenance of energy-efficient heat pump systems.',
    skills: ['HVAC', 'Heat Pump Technology', 'Customer Service'],
    posted_date: '2023-10-05',
    is_ej_friendly: false,
    is_veteran_friendly: false
  }
];

export async function GET(request) {
  try {
    // Get search parameters
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') || '';
    const location = searchParams.get('location') || '';
    const isEjFriendly = searchParams.get('ej_friendly') === 'true';
    const isVeteranFriendly = searchParams.get('veteran_friendly') === 'true';
    
    // Filter jobs based on search criteria
    let results = [...MOCK_JOBS];
    
    if (query) {
      const lowerQuery = query.toLowerCase();
      results = results.filter(job => 
        job.title.toLowerCase().includes(lowerQuery) ||
        job.company.toLowerCase().includes(lowerQuery) ||
        job.description.toLowerCase().includes(lowerQuery) ||
        job.skills.some(skill => skill.toLowerCase().includes(lowerQuery))
      );
    }
    
    if (location) {
      const lowerLocation = location.toLowerCase();
      results = results.filter(job => 
        job.location.toLowerCase().includes(lowerLocation)
      );
    }
    
    if (isEjFriendly) {
      results = results.filter(job => job.is_ej_friendly);
    }
    
    if (isVeteranFriendly) {
      results = results.filter(job => job.is_veteran_friendly);
    }
    
    // Return filtered results
    return NextResponse.json({ 
      jobs: results,
      count: results.length,
      query: { query, location, isEjFriendly, isVeteranFriendly }
    });
  } catch (error) {
    console.error('Error searching jobs:', error);
    return NextResponse.json(
      { error: 'Failed to search jobs' },
      { status: 500 }
    );
  }
} 