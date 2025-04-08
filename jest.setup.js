/**
 * Jest Setup
 * 
 * This file sets up the testing environment for Jest
 */

// Mock environment variables
process.env.NEXT_PUBLIC_SUPABASE_URL = 'https://example.supabase.co';
process.env.SUPABASE_SERVICE_KEY = 'mock-service-key';
process.env.OPENAI_API_KEY = 'mock-openai-key';
process.env.NEXTAUTH_URL = 'http://localhost:3000';
process.env.NEXTAUTH_SECRET = 'mock-nextauth-secret';
process.env.GOOGLE_CLIENT_ID = 'mock-google-client-id';
process.env.GOOGLE_CLIENT_SECRET = 'mock-google-client-secret';

// Mock fetch
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
);

// Mock console.error to avoid cluttering test output
console.error = jest.fn();

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
