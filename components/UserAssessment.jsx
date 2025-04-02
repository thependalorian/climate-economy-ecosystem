import { useState, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { 
  Alert, 
  Button, 
  Card, 
  Checkbox, 
  FileInput, 
  Input, 
  Radio, 
  Select, 
  Spinner, 
  Textarea
} from 'daisyui';

const USER_TYPES = [
  {
    id: 'veteran',
    label: 'Military veteran or transitioning service member'
  },
  {
    id: 'international',
    label: 'International professional with foreign credentials'
  },
  {
    id: 'student',
    label: 'Student (vocational/community college/university)'
  },
  {
    id: 'career_changer',
    label: 'Career changer from another industry'
  },
  {
    id: 'clean_energy_professional',
    label: 'Current clean energy professional seeking advancement'
  },
  {
    id: 'ej_community',
    label: 'Massachusetts resident from an Environmental Justice community'
  }
];

const CLEAN_ENERGY_SECTORS = [
  'High-Performance Buildings',
  'Renewable Energy',
  'Clean Transportation',
  'Energy Storage',
  'Grid Modernization',
  'Offshore Wind',
  'Workforce Development',
  'Energy Efficiency'
];

// Maps user types to their specific questions
const USER_TYPE_QUESTIONS = {
  veteran: [
    {
      id: 'transition_time',
      question: 'How recently did you transition from military service?',
      type: 'select',
      options: [
        'Currently transitioning',
        'Less than 1 year',
        '1-3 years',
        '3-5 years',
        'More than 5 years'
      ]
    },
    {
      id: 'mos',
      question: 'What was your primary military occupational specialty (MOS)?',
      type: 'text'
    },
    {
      id: 'interested_sector',
      question: 'What clean energy sector are you most interested in?',
      type: 'select',
      options: CLEAN_ENERGY_SECTORS
    }
  ],
  international: [
    {
      id: 'credential_country',
      question: 'In which country did you obtain your credentials?',
      type: 'text'
    },
    {
      id: 'expertise_field',
      question: 'What is your professional field of expertise?',
      type: 'text'
    },
    {
      id: 'credential_evaluation',
      question: 'Have you had your credentials evaluated in the US?',
      type: 'radio',
      options: ['Yes', 'No', 'In process']
    }
  ],
  student: [
    {
      id: 'institution_type',
      question: 'What type of educational institution are you attending?',
      type: 'select',
      options: [
        'Vocational/Technical School',
        'Community College',
        'Four-Year College/University',
        'Graduate School',
        'Certificate Program',
        'Other'
      ]
    },
    {
      id: 'field_of_study',
      question: 'What is your field of study?',
      type: 'text'
    },
    {
      id: 'completion_date',
      question: 'When do you expect to complete your program?',
      type: 'select',
      options: [
        'Less than 3 months',
        '3-6 months',
        '6-12 months',
        '1-2 years',
        'More than 2 years',
        'Already completed'
      ]
    }
  ],
  career_changer: [
    {
      id: 'previous_industry',
      question: 'What industry are you transitioning from?',
      type: 'text'
    },
    {
      id: 'transferable_skills',
      question: 'What skills from your current role do you believe are transferable?',
      type: 'textarea'
    },
    {
      id: 'employment_status',
      question: 'Are you currently employed?',
      type: 'radio',
      options: ['Yes, full-time', 'Yes, part-time', 'No']
    }
  ],
  clean_energy_professional: [
    {
      id: 'current_sector',
      question: 'Which clean energy sector do you currently work in?',
      type: 'select',
      options: CLEAN_ENERGY_SECTORS
    },
    {
      id: 'experience_level',
      question: 'How many years of experience do you have in clean energy?',
      type: 'select',
      options: [
        'Less than 1 year',
        '1-3 years',
        '3-5 years',
        '5-10 years',
        'More than 10 years'
      ]
    },
    {
      id: 'advancement_goals',
      question: 'What are your career advancement goals?',
      type: 'textarea'
    }
  ],
  ej_community: [
    {
      id: 'ma_city',
      question: 'Which Massachusetts city or town do you live in?',
      type: 'text'
    },
    {
      id: 'clean_energy_interest',
      question: 'What aspect of clean energy are you most interested in?',
      type: 'select',
      options: CLEAN_ENERGY_SECTORS
    },
    {
      id: 'community_involvement',
      question: 'Are you involved with any community organizations?',
      type: 'radio',
      options: ['Yes', 'No']
    }
  ]
};

/**
 * User Assessment Component
 * 
 * Collects information about the user's background, asks targeted questions,
 * and collects their resume for personalized recommendations.
 */
const UserAssessment = ({ onComplete }) => {
  const { data: session } = useSession();
  const fileInputRef = useRef(null);
  
  const [step, setStep] = useState(1);
  const [userType, setUserType] = useState('');
  const [answers, setAnswers] = useState({});
  const [resumeMethod, setResumeMethod] = useState('upload');
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [linkedInUrl, setLinkedInUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const handleUserTypeSelect = (type) => {
    setUserType(type);
    // Initialize answers for this user type
    const initialAnswers = {};
    USER_TYPE_QUESTIONS[type].forEach(q => {
      initialAnswers[q.id] = '';
    });
    setAnswers(initialAnswers);
  };
  
  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };
  
  const handleResumeFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };
  
  const validateCurrentStep = () => {
    if (step === 1 && !userType) {
      setError('Please select your background');
      return false;
    }
    
    if (step === 2) {
      const unansweredQuestions = USER_TYPE_QUESTIONS[userType].filter(
        q => !answers[q.id]
      );
      
      if (unansweredQuestions.length > 0) {
        setError(`Please answer all questions`);
        return false;
      }
    }
    
    if (step === 3) {
      if (resumeMethod === 'upload' && !resumeFile) {
        setError('Please upload your resume');
        return false;
      }
      
      if (resumeMethod === 'paste' && resumeText.trim().length < 100) {
        setError('Please paste your resume with sufficient detail');
        return false;
      }
    }
    
    setError(null);
    return true;
  };
  
  const goToNextStep = () => {
    if (validateCurrentStep()) {
      setStep(prev => prev + 1);
    }
  };
  
  const goToPreviousStep = () => {
    setStep(prev => prev - 1);
    setError(null);
  };
  
  const handleSubmit = async () => {
    if (!validateCurrentStep()) {
      return;
    }
    
    if (!session) {
      setError('You must be signed in to submit your profile');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append('user_type', userType);
      formData.append('answers', JSON.stringify(answers));
      formData.append('resume_method', resumeMethod);
      
      if (resumeMethod === 'upload' && resumeFile) {
        formData.append('resume_file', resumeFile);
      } else if (resumeMethod === 'paste') {
        formData.append('resume_text', resumeText);
      }
      
      if (linkedInUrl) {
        formData.append('linkedin_url', linkedInUrl);
      }
      
      // Submit to API
      const response = await fetch('/api/profile/assessment', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit assessment');
      }
      
      const data = await response.json();
      
      // Set success and call onComplete with the profile data
      setSuccess(true);
      if (onComplete) {
        onComplete(data.profile);
      }
      
    } catch (err) {
      setError(err.message || 'An error occurred during submission');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Render different content based on the current step
  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Which best describes your current situation?</h3>
            <div className="space-y-3">
              {USER_TYPES.map((type) => (
                <div key={type.id} className="flex items-center">
                  <Radio
                    id={`user-type-${type.id}`}
                    name="user-type"
                    checked={userType === type.id}
                    onChange={() => handleUserTypeSelect(type.id)}
                    className="mr-2"
                  />
                  <label htmlFor={`user-type-${type.id}`} className="cursor-pointer">
                    {type.label}
                  </label>
                </div>
              ))}
            </div>
          </div>
        );
        
      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Tell us a bit more about yourself</h3>
            <div className="space-y-4">
              {USER_TYPE_QUESTIONS[userType].map((question) => (
                <div key={question.id} className="space-y-2">
                  <label className="font-medium">{question.question}</label>
                  
                  {question.type === 'text' && (
                    <Input
                      type="text"
                      value={answers[question.id] || ''}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      className="w-full"
                    />
                  )}
                  
                  {question.type === 'textarea' && (
                    <Textarea
                      value={answers[question.id] || ''}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      className="w-full"
                      rows={3}
                    />
                  )}
                  
                  {question.type === 'select' && (
                    <Select
                      value={answers[question.id] || ''}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      className="w-full"
                    >
                      <option value="">Select an option</option>
                      {question.options.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </Select>
                  )}
                  
                  {question.type === 'radio' && (
                    <div className="space-y-2">
                      {question.options.map((option) => (
                        <div key={option} className="flex items-center">
                          <Radio
                            id={`${question.id}-${option}`}
                            name={question.id}
                            checked={answers[question.id] === option}
                            onChange={() => handleAnswerChange(question.id, option)}
                            className="mr-2"
                          />
                          <label htmlFor={`${question.id}-${option}`} className="cursor-pointer">
                            {option}
                          </label>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
        
      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Share your resume</h3>
            
            <div className="space-y-2">
              <div className="flex space-x-4">
                <div className="flex items-center">
                  <Radio
                    id="resume-upload"
                    name="resume-method"
                    checked={resumeMethod === 'upload'}
                    onChange={() => setResumeMethod('upload')}
                    className="mr-2"
                  />
                  <label htmlFor="resume-upload" className="cursor-pointer">
                    Upload resume
                  </label>
                </div>
                
                <div className="flex items-center">
                  <Radio
                    id="resume-paste"
                    name="resume-method"
                    checked={resumeMethod === 'paste'}
                    onChange={() => setResumeMethod('paste')}
                    className="mr-2"
                  />
                  <label htmlFor="resume-paste" className="cursor-pointer">
                    Paste resume text
                  </label>
                </div>
              </div>
              
              {resumeMethod === 'upload' && (
                <div className="mt-4">
                  <FileInput
                    ref={fileInputRef}
                    onChange={handleResumeFileChange}
                    accept=".pdf,.doc,.docx,.txt"
                    className="w-full"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Accepted formats: PDF, DOCX, TXT (max 5MB)
                  </p>
                  {resumeFile && (
                    <p className="text-sm text-green-600 mt-1">
                      Selected file: {resumeFile.name}
                    </p>
                  )}
                </div>
              )}
              
              {resumeMethod === 'paste' && (
                <div className="mt-4">
                  <Textarea
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    className="w-full"
                    rows={10}
                    placeholder="Paste your resume text here..."
                  />
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              <label className="font-medium">LinkedIn Profile URL (Optional)</label>
              <Input
                type="text"
                value={linkedInUrl}
                onChange={(e) => setLinkedInUrl(e.target.value)}
                placeholder="https://www.linkedin.com/in/yourprofile"
                className="w-full"
              />
            </div>
          </div>
        );
        
      default:
        return null;
    }
  };
  
  // If the assessment was successful, show success message
  if (success) {
    return (
      <Card className="bg-base-100 shadow-xl">
        <Card.Body>
          <div className="text-center py-6">
            <div className="text-success text-5xl mb-4">✓</div>
            <h2 className="card-title justify-center mb-2">Assessment Complete!</h2>
            <p className="mb-6">
              Thank you for completing your profile assessment. We'll use this information to provide personalized clean energy career recommendations.
            </p>
            <Button 
              color="primary" 
              onClick={() => {
                // Navigate or perform some action
                if (onComplete) onComplete();
              }}
            >
              View My Recommendations
            </Button>
          </div>
        </Card.Body>
      </Card>
    );
  }
  
  return (
    <Card className="bg-base-100 shadow-xl">
      <Card.Body>
        <h2 className="card-title">Your Clean Energy Career Profile</h2>
        <p className="mb-6">
          Let's get to know you better so we can provide the most relevant clean energy career opportunities in Massachusetts.
        </p>
        
        {/* Progress Indicators */}
        <div className="flex justify-between mb-6">
          <Button 
            size="sm" 
            variant={step === 1 ? 'primary' : 'outline'}
            className="btn-circle"
            disabled={step !== 1}
          >
            1
          </Button>
          <div className="h-1 flex-1 self-center mx-1 bg-base-300">
            <div 
              className="h-full bg-primary transition-all" 
              style={{ width: `${(step - 1) * 50}%` }}
            ></div>
          </div>
          <Button 
            size="sm" 
            variant={step === 2 ? 'primary' : 'outline'}
            className="btn-circle"
            disabled={step !== 2}
          >
            2
          </Button>
          <div className="h-1 flex-1 self-center mx-1 bg-base-300">
            <div 
              className="h-full bg-primary transition-all" 
              style={{ width: step === 3 ? '100%' : '0%' }}
            ></div>
          </div>
          <Button 
            size="sm" 
            variant={step === 3 ? 'primary' : 'outline'}
            className="btn-circle"
            disabled={step !== 3}
          >
            3
          </Button>
        </div>
        
        {/* Error Message */}
        {error && (
          <Alert className="alert-error mb-4">
            <span>{error}</span>
          </Alert>
        )}
        
        {/* Step Content */}
        {renderStepContent()}
        
        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          {step > 1 ? (
            <Button variant="outline" onClick={goToPreviousStep}>
              Back
            </Button>
          ) : (
            <div></div> {/* Empty div to maintain layout */}
          )}
          
          {step < 3 ? (
            <Button color="primary" onClick={goToNextStep}>
              Next
            </Button>
          ) : (
            <Button 
              color="primary" 
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? <Spinner size="sm" /> : 'Submit'}
            </Button>
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

export default UserAssessment; 