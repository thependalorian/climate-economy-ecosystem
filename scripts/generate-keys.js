#!/usr/bin/env node

/**
 * Script to generate secure keys for local development
 * 
 * This script generates secure random keys for JWT tokens and other secrets
 * and updates the .env file with these values.
 * 
 * Usage: node scripts/generate-keys.js
 */

const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

// Function to generate a secure random string
function generateSecureKey(length = 64) {
  return crypto.randomBytes(length).toString('hex');
}

// Function to generate a JWT token
function generateJWT(payload, secret) {
  // Simple JWT implementation (for demo purposes only)
  const header = { alg: 'HS256', typ: 'JWT' };
  const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64').replace(/=/g, '');
  const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64').replace(/=/g, '');
  const signature = crypto
    .createHmac('sha256', secret)
    .update(`${encodedHeader}.${encodedPayload}`)
    .digest('base64')
    .replace(/=/g, '');
  
  return `${encodedHeader}.${encodedPayload}.${signature}`;
}

// Main function
async function main() {
  try {
    console.log('Generating secure keys for local development...');
    
    // Define the path to the .env file
    const envPath = path.join(process.cwd(), '.env');
    
    // Check if .env file exists
    let envContent = '';
    if (fs.existsSync(envPath)) {
      envContent = fs.readFileSync(envPath, 'utf8');
      console.log('Found existing .env file');
    } else {
      // If .env doesn't exist, check for .env.example
      const examplePath = path.join(process.cwd(), '.env.example');
      if (fs.existsSync(examplePath)) {
        envContent = fs.readFileSync(examplePath, 'utf8');
        console.log('Using .env.example as template');
      } else {
        console.log('No .env or .env.example found, creating new .env file');
      }
    }
    
    // Generate secure keys
    const jwtSecret = generateSecureKey(32);
    
    // Generate JWT tokens for Supabase
    const anonPayload = {
      iss: 'supabase',
      role: 'anon',
      exp: 1983812996 // Far future expiration for development
    };
    
    const servicePayload = {
      iss: 'supabase',
      role: 'service_role',
      exp: 1983812996 // Far future expiration for development
    };
    
    const anonKey = generateJWT(anonPayload, jwtSecret);
    const serviceKey = generateJWT(servicePayload, jwtSecret);
    
    // Update environment variables
    const envVars = {
      JWT_SECRET: jwtSecret,
      SUPABASE_ANON_KEY: anonKey,
      SUPABASE_SERVICE_KEY: serviceKey,
      NEXTAUTH_SECRET: generateSecureKey(16)
    };
    
    // Update the .env content
    Object.entries(envVars).forEach(([key, value]) => {
      // Check if the variable already exists in the .env file
      const regex = new RegExp(`^${key}=.*`, 'm');
      if (regex.test(envContent)) {
        // Replace existing value
        envContent = envContent.replace(regex, `${key}=${value}`);
      } else {
        // Add new variable
        envContent += `\n${key}=${value}`;
      }
    });
    
    // Write the updated content to the .env file
    fs.writeFileSync(envPath, envContent);
    
    console.log('Secure keys generated and added to .env file');
    console.log('');
    console.log('Generated the following keys:');
    console.log('- JWT_SECRET: [Secure random key]');
    console.log('- SUPABASE_ANON_KEY: [JWT token for anonymous role]');
    console.log('- SUPABASE_SERVICE_KEY: [JWT token for service role]');
    console.log('- NEXTAUTH_SECRET: [Secure random key]');
    console.log('');
    console.log('IMPORTANT: These keys are for local development only.');
    console.log('           Do not commit the .env file to version control.');
    
  } catch (error) {
    console.error('Error generating keys:', error);
    process.exit(1);
  }
}

// Run the main function
main();
