'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { v4 as uuidv4 } from 'uuid';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/textarea';
import { AlertCircle, CheckCircle, X } from 'lucide-react';

/**
 * Feedback Component
 * 
 * Provides an interface for users to rate their experience and provide feedback.
 * Automatically tracks the current session and page context.
 */
export default function Feedback() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedRating, setSelectedRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [thankYouMessage, setThankYouMessage] = useState('');
  const { data: session } = useSession();
  
  // Generate a session ID if one doesn't exist
  const getSessionId = () => {
    if (typeof window === 'undefined') return '';
    
    let sessionId = localStorage.getItem('feedback_session_id');
    if (!sessionId) {
      sessionId = uuidv4();
      localStorage.setItem('feedback_session_id', sessionId);
    }
    return sessionId;
  };
  
  const handleRatingClick = (rating) => {
    setSelectedRating(rating);
  };
  
  const handleSubmit = async () => {
    if (!session) {
      setSubmitStatus('error');
      setThankYouMessage('Please sign in to submit feedback');
      return;
    }
    
    if (selectedRating === 0) {
      return;
    }
    
    setIsSubmitting(true);
    setSubmitStatus(null);
    
    try {
      const sessionId = getSessionId();
      const currentUrl = typeof window !== 'undefined' ? window.location.href : '';
      
      const response = await fetch('/api/feedback/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          satisfaction_score: selectedRating,
          feedback: feedbackText,
          session_id: sessionId,
          page_url: currentUrl,
          context: {
            userType: session?.user?.userType || 'unknown'
          }
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSubmitStatus('success');
        setThankYouMessage(data.thankyou_message || 'Thank you for your feedback!');
        
        // Reset form after a success
        setTimeout(() => {
          setSelectedRating(0);
          setFeedbackText('');
          setIsOpen(false);
          setSubmitStatus(null);
        }, 5000);
      } else {
        setSubmitStatus('error');
        setThankYouMessage(data.message || 'Error submitting feedback. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setSubmitStatus('error');
      setThankYouMessage('Error submitting feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleDismiss = () => {
    setIsOpen(false);
    setSelectedRating(0);
    setFeedbackText('');
    setSubmitStatus(null);
  };
  
  // Don't render if user is not signed in
  if (!session) {
    return null;
  }
  
  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen ? (
        <Button 
          onClick={() => setIsOpen(true)} 
          className="rounded-full shadow-lg"
          variant="default"
        >
          Feedback
        </Button>
      ) : (
        <Card className="w-80 shadow-lg">
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg">Share Your Feedback</CardTitle>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8" 
                onClick={handleDismiss}
              >
                <X size={16} />
              </Button>
            </div>
            <CardDescription>How was your experience?</CardDescription>
          </CardHeader>
          
          <CardContent>
            {submitStatus === 'success' ? (
              <div className="py-6 text-center space-y-2">
                <CheckCircle className="mx-auto h-10 w-10 text-green-500" />
                <p>{thankYouMessage}</p>
              </div>
            ) : submitStatus === 'error' ? (
              <div className="py-6 text-center space-y-2">
                <AlertCircle className="mx-auto h-10 w-10 text-red-500" />
                <p>{thankYouMessage}</p>
              </div>
            ) : (
              <>
                <div className="flex justify-center space-x-1 py-4">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        selectedRating >= rating 
                          ? 'bg-primary text-primary-foreground' 
                          : 'bg-muted text-muted-foreground hover:bg-muted/80'
                      }`}
                      onClick={() => handleRatingClick(rating)}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
                
                <Textarea
                  placeholder="Tell us more (optional)"
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  rows={3}
                  className="resize-none"
                />
              </>
            )}
          </CardContent>
          
          {!submitStatus && (
            <CardFooter>
              <Button 
                onClick={handleSubmit} 
                disabled={selectedRating === 0 || isSubmitting}
                className="w-full"
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <span className="loading loading-spinner loading-xs mr-2"></span>
                    Submitting...
                  </span>
                ) : (
                  'Submit Feedback'
                )}
              </Button>
            </CardFooter>
          )}
        </Card>
      )}
    </div>
  );
} 