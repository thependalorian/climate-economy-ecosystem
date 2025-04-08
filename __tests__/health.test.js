/**
 * Health Check API Tests
 * 
 * Tests for the health check API endpoint
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { GET } from '../app/api/health/route';
import { NextResponse } from 'next/server';

// Mock Supabase client
const mockSupabaseClient = {
  from: jest.fn().mockReturnThis(),
  select: jest.fn().mockReturnThis(),
  limit: jest.fn().mockReturnThis(),
  storage: {
    getBucket: jest.fn(),
    createBucket: jest.fn()
  }
};

// Mock fetch
global.fetch = jest.fn();

// Mock NextResponse
jest.mock('next/server', () => ({
  NextResponse: {
    json: jest.fn((data, options) => ({ data, options }))
  }
}));

// Mock Supabase
jest.mock('@supabase/supabase-js', () => ({
  createClient: jest.fn(() => mockSupabaseClient)
}));

describe('Health Check API', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock environment variables
    process.env.NEXT_PUBLIC_SUPABASE_URL = 'https://example.supabase.co';
    process.env.SUPABASE_SERVICE_KEY = 'mock-service-key';
    process.env.OPENAI_API_KEY = 'mock-openai-key';
    
    // Mock successful responses
    mockSupabaseClient.from().select().limit().mockResolvedValue({ data: [], error: null });
    mockSupabaseClient.storage.getBucket.mockResolvedValue({ data: {}, error: null });
    global.fetch.mockResolvedValue({ ok: true, json: () => Promise.resolve({ data: [] }) });
  });
  
  it('should return 200 when all services are healthy', async () => {
    const response = await GET();
    
    expect(NextResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        status: 'ok',
        services: expect.objectContaining({
          database: expect.objectContaining({ status: 'ok' }),
          openai: expect.objectContaining({ status: 'ok' }),
          storage: expect.objectContaining({ status: 'ok' })
        })
      }),
      expect.objectContaining({ status: 200 })
    );
    
    expect(mockSupabaseClient.from).toHaveBeenCalledWith('migrations');
    expect(mockSupabaseClient.storage.getBucket).toHaveBeenCalledWith('user-documents');
    expect(global.fetch).toHaveBeenCalledWith('https://api.openai.com/v1/models', expect.any(Object));
  });
  
  it('should return 503 when database is unhealthy', async () => {
    // Mock database error
    mockSupabaseClient.from().select().limit().mockResolvedValue({ data: null, error: new Error('Database error') });
    
    const response = await GET();
    
    expect(NextResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        status: 'degraded',
        services: expect.objectContaining({
          database: expect.objectContaining({ status: 'error' }),
          openai: expect.objectContaining({ status: 'ok' }),
          storage: expect.objectContaining({ status: 'ok' })
        })
      }),
      expect.objectContaining({ status: 503 })
    );
  });
  
  it('should return 503 when OpenAI API is unhealthy', async () => {
    // Mock OpenAI API error
    global.fetch.mockResolvedValue({ ok: false, status: 401 });
    
    const response = await GET();
    
    expect(NextResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        status: 'degraded',
        services: expect.objectContaining({
          database: expect.objectContaining({ status: 'ok' }),
          openai: expect.objectContaining({ status: 'error' }),
          storage: expect.objectContaining({ status: 'ok' })
        })
      }),
      expect.objectContaining({ status: 503 })
    );
  });
  
  it('should return 503 when storage is unhealthy', async () => {
    // Mock storage error
    mockSupabaseClient.storage.getBucket.mockResolvedValue({ data: null, error: new Error('Storage error') });
    mockSupabaseClient.storage.createBucket.mockResolvedValue({ data: null, error: new Error('Cannot create bucket') });
    
    const response = await GET();
    
    expect(NextResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        status: 'degraded',
        services: expect.objectContaining({
          database: expect.objectContaining({ status: 'ok' }),
          openai: expect.objectContaining({ status: 'ok' }),
          storage: expect.objectContaining({ status: 'error' })
        })
      }),
      expect.objectContaining({ status: 503 })
    );
  });
  
  it('should create storage bucket if it does not exist', async () => {
    // Mock bucket not found error
    const notFoundError = new Error('The resource was not found');
    mockSupabaseClient.storage.getBucket.mockResolvedValue({ data: null, error: notFoundError });
    mockSupabaseClient.storage.createBucket.mockResolvedValue({ data: {}, error: null });
    
    const response = await GET();
    
    expect(mockSupabaseClient.storage.createBucket).toHaveBeenCalledWith('user-documents', expect.any(Object));
    expect(NextResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        status: 'ok',
        services: expect.objectContaining({
          storage: expect.objectContaining({ status: 'ok' })
        })
      }),
      expect.objectContaining({ status: 200 })
    );
  });
});
