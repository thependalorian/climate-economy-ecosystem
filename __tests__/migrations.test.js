/**
 * Database Migrations Tests
 * 
 * Tests for the database migration system
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import migrations, { applyMigrations, getMigrationStatus } from '../lib/db/migrations';

// Mock Supabase client
const mockSupabase = {
  from: jest.fn().mockReturnThis(),
  select: jest.fn().mockReturnThis(),
  insert: jest.fn().mockReturnThis(),
  eq: jest.fn().mockReturnThis(),
  limit: jest.fn().mockReturnThis(),
  order: jest.fn().mockReturnThis(),
  rpc: jest.fn().mockReturnThis(),
  execute: jest.fn()
};

// Mock createClientComponentClient
jest.mock('@supabase/auth-helpers-nextjs', () => ({
  createClientComponentClient: jest.fn(() => mockSupabase)
}));

describe('Database Migrations', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });
  
  it('should have migrations defined', () => {
    expect(migrations).toBeDefined();
    expect(Array.isArray(migrations)).toBe(true);
    expect(migrations.length).toBeGreaterThan(0);
    
    // Check migration structure
    const firstMigration = migrations[0];
    expect(firstMigration).toHaveProperty('id');
    expect(firstMigration).toHaveProperty('description');
    expect(firstMigration).toHaveProperty('sql');
  });
  
  it('should apply migrations successfully', async () => {
    // Mock successful migration
    mockSupabase.execute.mockResolvedValueOnce({ data: [], error: null }); // Check migrations table
    mockSupabase.execute.mockResolvedValueOnce({ data: [], error: null }); // Get applied migrations
    mockSupabase.execute.mockResolvedValueOnce({ data: [], error: null }); // Apply migration
    mockSupabase.execute.mockResolvedValueOnce({ data: [], error: null }); // Record migration
    
    const result = await applyMigrations();
    
    expect(result.success).toBe(true);
    expect(result.applied.length).toBeGreaterThan(0);
    expect(result.failed.length).toBe(0);
    expect(mockSupabase.rpc).toHaveBeenCalledWith('execute_sql', expect.any(Object));
    expect(mockSupabase.from).toHaveBeenCalledWith('migrations');
    expect(mockSupabase.insert).toHaveBeenCalled();
  });
  
  it('should handle migration failures', async () => {
    // Mock migration failure
    mockSupabase.execute.mockResolvedValueOnce({ data: [], error: null }); // Check migrations table
    mockSupabase.execute.mockResolvedValueOnce({ data: [], error: null }); // Get applied migrations
    mockSupabase.execute.mockResolvedValueOnce({ data: null, error: new Error('SQL error') }); // Apply migration
    
    const result = await applyMigrations();
    
    expect(result.success).toBe(false);
    expect(result.failed.length).toBeGreaterThan(0);
    expect(mockSupabase.from).toHaveBeenCalledWith('migrations');
    expect(mockSupabase.insert).toHaveBeenCalled();
  });
  
  it('should get migration status', async () => {
    // Mock successful status check
    mockSupabase.execute.mockResolvedValueOnce({
      data: [
        { id: '001_initial_schema', description: 'Initial schema', applied_at: new Date().toISOString(), success: true }
      ],
      error: null
    });
    
    const status = await getMigrationStatus();
    
    expect(status.success).toBe(true);
    expect(status.applied.length).toBeGreaterThan(0);
    expect(status.pending.length).toBe(migrations.length - 1);
    expect(mockSupabase.from).toHaveBeenCalledWith('migrations');
    expect(mockSupabase.select).toHaveBeenCalled();
    expect(mockSupabase.order).toHaveBeenCalled();
  });
  
  it('should handle status check failures', async () => {
    // Mock status check failure
    mockSupabase.execute.mockResolvedValueOnce({ data: null, error: new Error('Database error') });
    
    const status = await getMigrationStatus();
    
    expect(status.success).toBe(false);
    expect(status.pending.length).toBe(migrations.length);
    expect(mockSupabase.from).toHaveBeenCalledWith('migrations');
    expect(mockSupabase.select).toHaveBeenCalled();
  });
});
