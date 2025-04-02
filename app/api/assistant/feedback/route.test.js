import { NextRequest, NextResponse } from 'next/server';
import { POST } from './route';

// Mock Supabase
jest.mock('@supabase/auth-helpers-nextjs', () => ({
  createRouteHandlerClient: jest.fn(() => ({
    auth: {
      getUser: jest.fn().mockResolvedValue({
        data: {
          user: { id: 'test-user-id' }
        },
        error: null
      })
    },
    from: jest.fn().mockImplementation((table) => ({
      insert: jest.fn().mockReturnThis(),
      select: jest.fn().mockReturnThis(),
      eq: jest.fn().mockReturnThis(),
      single: jest.fn().mockReturnThis(),
      order: jest.fn().mockReturnThis(),
      limit: jest.fn().mockReturnThis(),
      execute: jest.fn().mockImplementation(() => {
        if (table === 'chat_feedback') {
          return Promise.resolve({
            data: { id: 'feedback-id', user_id: 'test-user-id' },
            error: null
          });
        } else if (table === 'user_engagement') {
          return Promise.resolve({
            data: {
              id: 'engagement-id',
              user_id: 'test-user-id',
              satisfaction_score: 80
            },
            error: null
          });
        } else if (table === 'chat_feedback') {
          return Promise.resolve({
            data: [
              { feedback_type: 'positive', feedback_score: null },
              { feedback_type: 'negative', feedback_score: null },
              { feedback_type: null, feedback_score: 4 }
            ],
            error: null
          });
        }
        return Promise.resolve({ data: null, error: null });
      })
    }))
  }))
}));

// Mock cookies
jest.mock('next/headers', () => ({
  cookies: jest.fn()
}));

// Mock MetricsService
jest.mock('@/lib/monitoring/metrics_service', () => ({
  MetricsService: jest.fn().mockImplementation(() => ({
    trackChatFeedback: jest.fn().mockResolvedValue(true)
  }))
}));

// Mock window
global.window = undefined;

describe('Feedback API Route', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('handles message-level feedback correctly', async () => {
    // Create request
    const request = new NextRequest('http://localhost:3000/api/assistant/feedback', {
      method: 'POST',
      body: JSON.stringify({
        messageId: 'test-message-id',
        feedback: 'positive'
      })
    });
    
    // Call the API route
    const response = await POST(request);
    const result = await response.json();
    
    // Check results
    expect(response.status).toBe(200);
    expect(result.message).toBe('Feedback submitted successfully');
  });

  it('handles step-level feedback correctly', async () => {
    // Create request
    const request = new NextRequest('http://localhost:3000/api/assistant/feedback', {
      method: 'POST',
      body: JSON.stringify({
        step_id: 'test-step-id',
        chat_id: 'test-chat-id',
        feedback_type: 'positive',
        feedback_score: 5
      })
    });
    
    // Call the API route
    const response = await POST(request);
    const result = await response.json();
    
    // Check results
    expect(response.status).toBe(200);
    expect(result.message).toBe('Feedback submitted successfully');
  });

  it('rejects requests without required fields', async () => {
    // Create request with missing fields
    const request = new NextRequest('http://localhost:3000/api/assistant/feedback', {
      method: 'POST',
      body: JSON.stringify({})
    });
    
    // Call the API route
    const response = await POST(request);
    const result = await response.json();
    
    // Check results
    expect(response.status).toBe(400);
    expect(result.error).toBe('Message ID or Step ID, and feedback data are required');
  });

  it('rejects unauthenticated requests', async () => {
    // Mock auth to return no user
    jest.mock('@supabase/auth-helpers-nextjs', () => ({
      createRouteHandlerClient: jest.fn(() => ({
        auth: {
          getUser: jest.fn().mockResolvedValue({
            data: { user: null },
            error: null
          })
        }
      }))
    }));
    
    // Create request
    const request = new NextRequest('http://localhost:3000/api/assistant/feedback', {
      method: 'POST',
      body: JSON.stringify({
        messageId: 'test-message-id',
        feedback: 'positive'
      })
    });
    
    // Call the API route
    const response = await POST(request);
    const result = await response.json();
    
    // Check results
    expect(response.status).toBe(401);
    expect(result.error).toBe('Authentication required');
  });

  it('handles database errors gracefully', async () => {
    // Mock Supabase to return an error
    jest.mock('@supabase/auth-helpers-nextjs', () => ({
      createRouteHandlerClient: jest.fn(() => ({
        auth: {
          getUser: jest.fn().mockResolvedValue({
            data: {
              user: { id: 'test-user-id' }
            },
            error: null
          })
        },
        from: jest.fn().mockImplementation(() => ({
          insert: jest.fn().mockReturnThis(),
          select: jest.fn().mockReturnThis(),
          single: jest.fn().mockRejectedValue(new Error('Database error'))
        }))
      }))
    }));
    
    // Create request
    const request = new NextRequest('http://localhost:3000/api/assistant/feedback', {
      method: 'POST',
      body: JSON.stringify({
        messageId: 'test-message-id',
        feedback: 'positive'
      })
    });
    
    // Call the API route
    const response = await POST(request);
    const result = await response.json();
    
    // Check results
    expect(response.status).toBe(500);
    expect(result.error).toBe('Failed to submit feedback');
  });
}); 