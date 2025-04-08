#!/usr/bin/env node

/**
 * Database Migration Script
 * 
 * This script applies database migrations to the Supabase database.
 * Run with: node scripts/run-migrations.js
 */

require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const migrations = require('../lib/db/migrations').default;

// Get Supabase credentials from environment variables
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Error: Supabase credentials are missing. Please check environment variables.');
  process.exit(1);
}

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Apply migrations to the database
 */
async function applyMigrations() {
  console.log('Starting database migrations...');
  
  try {
    // Check if migrations table exists
    const { error: tableCheckError } = await supabase
      .from('migrations')
      .select('id')
      .limit(1);
    
    // Create migrations table if it doesn't exist
    if (tableCheckError) {
      console.log('Creating migrations table...');
      
      const { error: createTableError } = await supabase.rpc('execute_sql', {
        query: `
          CREATE TABLE IF NOT EXISTS migrations (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            success BOOLEAN NOT NULL
          );
        `
      });
      
      if (createTableError) {
        console.error('Error creating migrations table:', createTableError);
        process.exit(1);
      }
      
      console.log('✅ Migrations table created');
    }
    
    // Get applied migrations
    const { data: appliedMigrations, error: fetchError } = await supabase
      .from('migrations')
      .select('id')
      .eq('success', true);
    
    if (fetchError) {
      console.error('Error fetching applied migrations:', fetchError);
      process.exit(1);
    }
    
    const appliedMigrationIds = appliedMigrations?.map(m => m.id) || [];
    console.log(`Found ${appliedMigrationIds.length} previously applied migrations`);
    
    // Apply migrations in order
    let appliedCount = 0;
    let skippedCount = 0;
    let failedCount = 0;
    
    for (const migration of migrations) {
      // Skip if already applied
      if (appliedMigrationIds.includes(migration.id)) {
        console.log(`⏭️  Skipping migration ${migration.id}: already applied`);
        skippedCount++;
        continue;
      }
      
      console.log(`🔄 Applying migration ${migration.id}: ${migration.description}`);
      
      try {
        // Apply migration
        const { error } = await supabase.rpc('execute_sql', {
          query: migration.sql
        });
        
        if (error) {
          throw error;
        }
        
        // Record successful migration
        const { error: recordError } = await supabase
          .from('migrations')
          .insert({
            id: migration.id,
            description: migration.description,
            success: true
          });
        
        if (recordError) {
          throw recordError;
        }
        
        console.log(`✅ Migration ${migration.id} applied successfully`);
        appliedCount++;
      } catch (error) {
        console.error(`❌ Error applying migration ${migration.id}:`, error);
        
        // Record failed migration
        await supabase
          .from('migrations')
          .insert({
            id: migration.id,
            description: migration.description,
            success: false
          });
        
        failedCount++;
      }
    }
    
    // Print summary
    console.log('\n===== Migration Summary =====');
    console.log(`Applied: ${appliedCount}`);
    console.log(`Skipped: ${skippedCount}`);
    console.log(`Failed: ${failedCount}`);
    
    if (failedCount > 0) {
      console.error('\n⚠️  Some migrations failed. Please check the logs and fix the issues.');
      process.exit(1);
    } else if (appliedCount === 0 && skippedCount > 0) {
      console.log('\n✅ All migrations have already been applied.');
    } else {
      console.log('\n✅ All migrations applied successfully.');
    }
  } catch (error) {
    console.error('Error in migration process:', error);
    process.exit(1);
  }
}

// Run migrations
applyMigrations()
  .then(() => {
    process.exit(0);
  })
  .catch((error) => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
