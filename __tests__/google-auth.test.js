/**
 * Google Authentication Tests
 * 
 * Tests for the Google authentication implementation
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

// Mock NextAuth
jest.mock('next-auth', () => {
  const originalModule = jest.requireActual('next-auth');
  return {
    __esModule: true,
    ...originalModule,
    default: jest.fn(() => ({ GET: jest.fn(), POST: jest.fn() }))
  };
});

// Mock GoogleProvider
jest.mock('next-auth/providers/google', () => {
  return jest.fn(() => ({ id: 'google', name: 'Google' }));
});

// Mock Supabase client
const mockSupabase = {
  from: jest.fn().mockReturnThis(),
  select: jest.fn().mockReturnThis(),
  insert: jest.fn().mockReturnThis(),
  eq: jest.fn().mockReturnThis(),
  single: jest.fn().mockReturnThis(),
  auth: {
    admin: {
      createUser: jest.fn()
    }
  }
};

// Mock supabase-client
jest.mock('../lib/supabase-client', () => {
  return {
    __esModule: true,
    default: mockSupabase
  };
});

// Import the route handler
import { handler } from '../app/api/auth/[...nextauth]/route';

describe('Google Authentication', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock environment variables
    process.env.GOOGLE_CLIENT_ID = 'mock-google-client-id';
    process.env.GOOGLE_CLIENT_SECRET = 'mock-google-client-secret';
  });
  
  it('should configure GoogleProvider correctly', () => {
    // Check that NextAuth was called
    expect(NextAuth).toHaveBeenCalled();
    
    // Check that GoogleProvider was configured
    expect(GoogleProvider).toHaveBeenCalledWith({
      clientId: 'mock-google-client-id',
      clientSecret: 'mock-google-client-secret',
      profile: expect.any(Function)
    });
    
    // Get the profile function
    const profileFn = GoogleProvider.mock.calls[0][0].profile;
    
    // Test the profile function
    const mockGoogleProfile = {
      sub: 'google-user-id',
      email: 'user@example.com',
      name: 'Test User',
      picture: 'https://example.com/profile.jpg'
    };
    
    const profileResult = profileFn(mockGoogleProfile);
    
    expect(profileResult).toEqual({
      id: 'google-user-id',
      email: 'user@example.com',
      name: 'Test User',
      image: 'https://example.com/profile.jpg',
      role: 'user'
    });
  });
  
  it('should have signIn callback for Google authentication', () => {
    // Get the options passed to NextAuth
    const options = NextAuth.mock.calls[0][0];
    
    // Check that signIn callback exists
    expect(options.callbacks).toBeDefined();
    expect(options.callbacks.signIn).toBeDefined();
    expect(typeof options.callbacks.signIn).toBe('function');
  });
  
  it('should have jwt callback to include provider information', () => {
    // Get the options passed to NextAuth
    const options = NextAuth.mock.calls[0][0];
    
    // Check that jwt callback exists
    expect(options.callbacks.jwt).toBeDefined();
    expect(typeof options.callbacks.jwt).toBe('function');
    
    // Test the jwt callback
    const jwtCallback = options.callbacks.jwt;
    
    const result = jwtCallback({
      token: {},
      user: {
        id: 'user-id',
        email: 'user@example.com',
        name: 'Test User',
        role: 'user'
      },
      account: {
        provider: 'google'
      }
    });
    
    expect(result).toEqual({
      id: 'user-id',
      email: 'user@example.com',
      name: 'Test User',
      role: 'user',
      provider: 'google'
    });
  });
  
  it('should have session callback to include provider information', () => {
    // Get the options passed to NextAuth
    const options = NextAuth.mock.calls[0][0];
    
    // Check that session callback exists
    expect(options.callbacks.session).toBeDefined();
    expect(typeof options.callbacks.session).toBe('function');
    
    // Test the session callback
    const sessionCallback = options.callbacks.session;
    
    const result = sessionCallback({
      session: {
        user: {}
      },
      token: {
        id: 'user-id',
        role: 'user',
        profile: { name: 'Test User' },
        provider: 'google'
      }
    });
    
    expect(result.user).toEqual({
      id: 'user-id',
      role: 'user',
      profile: { name: 'Test User' },
      provider: 'google'
    });
  });
});
