import { NextResponse } from 'next/server';

/**
 * Profile Assessment API
 * Handles user assessment data for matching with career opportunities
 * Location: /app/api/profile/assessment/route.js
 */

export async function POST(request) {
  try {
    // Parse the request body
    const data = await request.json();
    const { resume, userType, background } = data;
    
    if (!resume) {
      return NextResponse.json(
        { error: 'Resume is required' },
        { status: 400 }
      );
    }
    
    // In a real app, this would process the resume and save the data to the database
    // Here we're returning mock assessment results
    
    // Mock skill extraction
    const skills = extractMockSkills(resume, userType);
    
    // Mock job matches based on extracted skills
    const jobMatches = generateMockJobMatches(skills, userType, background);
    
    // Mock training recommendations
    const trainingRecommendations = generateMockTrainingRecommendations(skills, userType, background);
    
    // Return the assessment results
    return NextResponse.json({
      skills,
      jobMatches,
      trainingRecommendations,
      userType,
      assessmentComplete: true
    });
  } catch (error) {
    console.error('Error processing assessment:', error);
    return NextResponse.json(
      { error: 'Failed to process assessment' },
      { status: 500 }
    );
  }
}

// Helper function to extract mock skills from resume
function extractMockSkills(resume, userType) {
  // This would normally use NLP/ML to extract skills from the resume
  // Here we're just returning mock data based on the user type
  
  const commonSkills = [
    { name: 'Communication', level: 'Advanced', relevance: 0.9 },
    { name: 'Problem Solving', level: 'Intermediate', relevance: 0.8 },
    { name: 'Time Management', level: 'Advanced', relevance: 0.85 }
  ];
  
  const userTypeSkills = {
    'veteran': [
      { name: 'Leadership', level: 'Advanced', relevance: 0.95 },
      { name: 'Project Management', level: 'Advanced', relevance: 0.9 },
      { name: 'Team Coordination', level: 'Advanced', relevance: 0.85 },
      { name: 'Electrical Systems', level: 'Intermediate', relevance: 0.7 }
    ],
    'international': [
      { name: 'Multilingual', level: 'Advanced', relevance: 0.9 },
      { name: 'Cultural Awareness', level: 'Advanced', relevance: 0.85 },
      { name: 'Adaptability', level: 'Advanced', relevance: 0.9 },
      { name: 'Engineering', level: 'Advanced', relevance: 0.8 }
    ],
    'student': [
      { name: 'Research', level: 'Intermediate', relevance: 0.8 },
      { name: 'Data Analysis', level: 'Beginner', relevance: 0.7 },
      { name: 'Critical Thinking', level: 'Intermediate', relevance: 0.85 }
    ],
    'career_changer': [
      { name: 'Adaptability', level: 'Advanced', relevance: 0.9 },
      { name: 'Customer Service', level: 'Advanced', relevance: 0.8 },
      { name: 'Project Management', level: 'Intermediate', relevance: 0.75 }
    ],
    'professional': [
      { name: 'Leadership', level: 'Advanced', relevance: 0.9 },
      { name: 'Strategic Planning', level: 'Advanced', relevance: 0.85 },
      { name: 'Industry Knowledge', level: 'Advanced', relevance: 0.95 }
    ],
    'ej_community': [
      { name: 'Community Engagement', level: 'Advanced', relevance: 0.9 },
      { name: 'Resilience', level: 'Advanced', relevance: 0.85 },
      { name: 'Local Knowledge', level: 'Advanced', relevance: 0.95 }
    ]
  };
  
  // Return a combination of common skills and user type specific skills
  return [
    ...commonSkills,
    ...(userTypeSkills[userType] || [])
  ];
}

// Helper function to generate mock job matches
function generateMockJobMatches(skills, userType, background) {
  // This would normally use a matching algorithm to find suitable jobs
  // Here we're just returning mock data
  
  const jobs = [
    {
      id: '1',
      title: 'Solar Installation Technician',
      company: 'SunBright Energy',
      location: 'Boston, MA',
      match_score: 89,
      skills_matched: ['Communication', 'Problem Solving', 'Electrical Systems'],
      description: 'Join our team installing solar panels across Eastern Massachusetts.'
    },
    {
      id: '2',
      title: 'Energy Efficiency Auditor',
      company: 'GreenSave Solutions',
      location: 'Worcester, MA',
      match_score: 82,
      skills_matched: ['Communication', 'Problem Solving', 'Data Analysis'],
      description: 'Help homeowners and businesses reduce their energy consumption through detailed energy audits.'
    },
    {
      id: '3',
      title: 'Project Coordinator - Wind Farm',
      company: 'WindStream Energy',
      location: 'New Bedford, MA',
      match_score: 78,
      skills_matched: ['Leadership', 'Project Management', 'Communication'],
      description: 'Coordinate activities for our offshore wind farm development projects.'
    }
  ];
  
  // Adjust match scores based on user type and background for a personalized feel
  return jobs.map(job => {
    // Apply some mock adjustments to make the results seem personalized
    let adjustedScore = job.match_score;
    
    if (userType === 'veteran' && job.title.includes('Coordinator')) {
      adjustedScore += 7;
    } else if (userType === 'international' && job.title.includes('Engineer')) {
      adjustedScore += 5;
    } else if (userType === 'ej_community' && job.location.includes(background?.location || '')) {
      adjustedScore += 10;
    }
    
    // Cap at 100
    adjustedScore = Math.min(adjustedScore, 100);
    
    return {
      ...job,
      match_score: adjustedScore
    };
  }).sort((a, b) => b.match_score - a.match_score);
}

// Helper function to generate mock training recommendations
function generateMockTrainingRecommendations(skills, userType, background) {
  // This would normally use a matching algorithm to find suitable training programs
  // Here we're just returning mock data
  
  const trainings = [
    {
      id: '1',
      title: 'Solar PV Installer Certification',
      provider: 'Massachusetts Clean Energy Center',
      location: 'Boston, MA',
      duration: '4 weeks',
      format: 'In-person',
      relevance_score: 92,
      description: 'Get certified to install solar photovoltaic systems.'
    },
    {
      id: '2',
      title: 'Building Energy Efficiency Fundamentals',
      provider: 'Worcester Community College',
      location: 'Worcester, MA',
      duration: '8 weeks',
      format: 'Hybrid',
      relevance_score: 85,
      description: 'Learn the basics of building energy efficiency and auditing.'
    },
    {
      id: '3',
      title: 'Wind Turbine Technician Training',
      provider: 'New Bedford Maritime Institute',
      location: 'New Bedford, MA',
      duration: '12 weeks',
      format: 'In-person',
      relevance_score: 78,
      description: 'Comprehensive training program for wind turbine maintenance and repair.'
    }
  ];
  
  // Adjust relevance scores based on user type and background for a personalized feel
  return trainings.map(training => {
    // Apply some mock adjustments to make the results seem personalized
    let adjustedScore = training.relevance_score;
    
    if (userType === 'student' && training.format.includes('Hybrid')) {
      adjustedScore += 8;
    } else if (userType === 'career_changer' && training.duration.includes('4 weeks')) {
      adjustedScore += 5;
    } else if (userType === 'ej_community' && training.location.includes(background?.location || '')) {
      adjustedScore += 10;
    }
    
    // Cap at 100
    adjustedScore = Math.min(adjustedScore, 100);
    
    return {
      ...training,
      relevance_score: adjustedScore
    };
  }).sort((a, b) => b.relevance_score - a.relevance_score);
} 