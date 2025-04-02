import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import StepFeedback from './StepFeedback';

// Mock fetch
global.fetch = jest.fn();

describe('StepFeedback Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    
    // Setup fetch mock to return success
    fetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ message: 'Feedback submitted successfully' })
      })
    );
  });

  it('renders thumbs up and down buttons', () => {
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    expect(screen.getByLabelText('Thumbs up')).toBeInTheDocument();
    expect(screen.getByLabelText('Thumbs down')).toBeInTheDocument();
  });

  it('disables buttons during submission', async () => {
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    const thumbsUpButton = screen.getByLabelText('Thumbs up');
    
    // Setup a delayed response from fetch
    fetch.mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => 
          resolve({
            ok: true,
            json: () => Promise.resolve({ message: 'Feedback submitted successfully' })
          }), 
          100
        )
      )
    );
    
    // Click thumbs up
    fireEvent.click(thumbsUpButton);
    
    // Buttons should be disabled during submission
    expect(thumbsUpButton).toBeDisabled();
    expect(screen.getByLabelText('Thumbs down')).toBeDisabled();
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(screen.getByText('Thanks for your feedback!')).toBeInTheDocument();
    });
  });

  it('shows a thank you message after feedback submission', async () => {
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    // Click thumbs up
    fireEvent.click(screen.getByLabelText('Thumbs up'));
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(screen.getByText('Thanks for your feedback!')).toBeInTheDocument();
    });
    
    // Buttons should be hidden after submission
    expect(screen.queryByLabelText('Thumbs up')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Thumbs down')).not.toBeInTheDocument();
  });

  it('sends the correct data to the API for positive feedback', async () => {
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    // Click thumbs up
    fireEvent.click(screen.getByLabelText('Thumbs up'));
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/assistant/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          step_id: 'test-step-id',
          chat_id: 'test-chat-id',
          feedback_type: 'positive',
          feedback_score: 5
        })
      });
    });
  });

  it('sends the correct data to the API for negative feedback', async () => {
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    // Click thumbs down
    fireEvent.click(screen.getByLabelText('Thumbs down'));
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/assistant/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          step_id: 'test-step-id',
          chat_id: 'test-chat-id',
          feedback_type: 'negative',
          feedback_score: 1
        })
      });
    });
  });

  it('shows an error message when submission fails', async () => {
    // Setup fetch mock to return error
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to submit feedback' })
      })
    );
    
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    // Click thumbs up
    fireEvent.click(screen.getByLabelText('Thumbs up'));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Failed to submit feedback')).toBeInTheDocument();
    });
    
    // Buttons should be enabled again
    expect(screen.getByLabelText('Thumbs up')).not.toBeDisabled();
    expect(screen.getByLabelText('Thumbs down')).not.toBeDisabled();
  });

  it('does nothing when feedback has already been given', async () => {
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    // Click thumbs up
    fireEvent.click(screen.getByLabelText('Thumbs up'));
    
    // Wait for submission to complete
    await waitFor(() => {
      expect(screen.getByText('Thanks for your feedback!')).toBeInTheDocument();
    });
    
    // Reset fetch mock
    fetch.mockClear();
    
    // Render again
    render(<StepFeedback stepId="test-step-id" chatId="test-chat-id" />);
    
    // Feedback has already been given, so fetch should not be called again
    expect(fetch).not.toHaveBeenCalled();
  });
}); 