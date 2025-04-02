'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

/**
 * StepFeedback Component
 * 
 * Allows users to provide feedback on individual reasoning steps
 * in AI responses.
 */
export default function StepFeedback({ stepId, chatId }) {
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  const submitFeedback = async (isPositive) => {
    if (feedbackGiven || !stepId) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch('/api/assistant/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          step_id: stepId,
          chat_id: chatId,
          feedback_type: isPositive ? 'positive' : 'negative',
          feedback_score: isPositive ? 5 : 1
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      setFeedbackGiven(true);
    } catch (err) {
      console.error('Error submitting feedback:', err);
      setError('Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (feedbackGiven) {
    return (
      <div className="step-feedback-confirmation text-xs text-gray-500 italic mt-1">
        Thanks for your feedback!
      </div>
    );
  }
  
  return (
    <div className="step-feedback flex items-center gap-2 mt-1">
      <button
        onClick={() => submitFeedback(true)}
        disabled={isSubmitting}
        className="text-gray-500 hover:text-green-500 transition-colors"
        aria-label="Thumbs up"
      >
        <ThumbsUp size={14} />
      </button>
      
      <button
        onClick={() => submitFeedback(false)}
        disabled={isSubmitting}
        className="text-gray-500 hover:text-red-500 transition-colors"
        aria-label="Thumbs down"
      >
        <ThumbsDown size={14} />
      </button>
      
      {error && (
        <span className="text-xs text-red-500">{error}</span>
      )}
      
      {isSubmitting && (
        <span className="loading loading-spinner loading-xs"></span>
      )}
    </div>
  );
} 