#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
import json
import time
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize base headers for Supabase requests
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0
        self.lock = asyncio.Lock()
    
    async def wait(self):
        """Wait if necessary to comply with rate limits."""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call_time
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self.last_call_time = time.time()

class ClimateDatabase:
    """Database adapter for the climate economy ecosystem."""
    
    def __init__(self):
        """Initialize the database adapter."""
        # Initialize OpenAI client if API key is available
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI()
        else:
            self.openai_client = None
            
        # Initialize rate limiter for Supabase calls
        self.rate_limiter = RateLimiter(2.0)  # 2 calls per second
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        if not self.openai_client:
            logger.warning("OpenAI client not available, skipping embedding generation")
            return None
            
        try:
            # Use OpenAI's embedding model
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"  # 1536 dimensions
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding with OpenAI: {str(e)}")
            return None
    
    async def store_climate_memory(self, data: Dict) -> Optional[str]:
        """Store a memory in the climate_memories table.
        
        Args:
            data: Dictionary containing memory data with the following fields:
                content: Text content
                metadata: JSON metadata
                embedding: Vector embedding (optional)
                source_type: Type of source document (will be stored in metadata)
                url: URL of source (optional, will be stored in metadata)
                title: Title of document (optional, will be stored in metadata)
                chunk_index: Index of chunk in document (optional, will be stored in metadata)
                total_chunks: Total number of chunks in document (optional, will be stored in metadata)
        
        Returns:
            str: ID of inserted record or None if failed
        """
        try:
            await self.rate_limiter.wait()
            
            # Skip if content is too short
            if not data.get('content') or len(data['content'].strip()) < 50:
                logger.warning(f"Content too short from {data.get('url', 'unknown')}, skipping")
                return None
            
            # Ensure metadata exists
            if 'metadata' not in data:
                data['metadata'] = {}
            
            # Move fields into metadata that aren't direct columns
            for field in ['source_type', 'url', 'title', 'chunk_index', 'total_chunks', 'company', 'sector']:
                if field in data:
                    data['metadata'][field] = data.pop(field)
            
            # Add timestamp
            metadata_timestamp = datetime.now(timezone.utc).isoformat()
            if 'created_at' not in data:
                data['metadata']['indexed_at'] = metadata_timestamp
            
            # Format the record for insertion
            record = {
                'content': data['content'],
                'metadata': data['metadata']
            }
            
            # Add embedding if present
            if 'embedding' in data:
                record['embedding'] = data['embedding']
            
            # Insert into Supabase
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/climate_memories",
                headers=SUPABASE_HEADERS,
                json=record
            )
            
            if response.status_code == 201 and response.json():
                record_id = response.json()[0]['id']
                logger.info(f"Successfully inserted memory: {data.get('metadata', {}).get('title', 'Untitled')}")
                return record_id
            else:
                logger.error(f"Failed to insert memory: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return None
    
    async def memory_exists(self, url: str, chunk_index: Optional[int] = None) -> bool:
        """Check if a memory with the given URL and chunk index already exists."""
        try:
            await self.rate_limiter.wait()
            
            # Encode for URL
            encoded_url = requests.utils.quote(url)
            
            # Build the query to search in metadata
            query_url = f"{SUPABASE_URL}/rest/v1/climate_memories?select=id&metadata->>url=eq.{encoded_url}"
            
            # Add chunk index filter if provided
            if chunk_index is not None:
                query_url += f"&metadata->>chunk_index=eq.{chunk_index}"
            
            # Make request
            response = requests.get(
                query_url,
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200:
                return len(response.json()) > 0
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking if memory exists: {str(e)}")
            return False
    
    async def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get profile for a user."""
        try:
            await self.rate_limiter.wait()
            
            # Encode user_id to handle special characters
            encoded_user_id = requests.utils.quote(user_id)
            
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{encoded_user_id}",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200 and response.json():
                return response.json()[0]
                
            return None
                
        except Exception as e:
            logger.error(f"Error getting profile for user {user_id}: {str(e)}")
            return None
    
    async def store_job(self, job_data: Dict) -> Optional[str]:
        """Store a job opportunity in the jobs table.
        
        Args:
            job_data: Dictionary containing job data with the following fields:
                title: Job title
                company: Company name
                description: Job description
                requirements: List of job requirements
                location: Job location
                salary_range: Salary range (optional)
        
        Returns:
            str: ID of inserted record or None if failed
        """
        try:
            await self.rate_limiter.wait()
            
            # Insert into Supabase
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/jobs",
                headers=SUPABASE_HEADERS,
                json=job_data
            )
            
            if response.status_code == 201 and response.json():
                job_id = response.json()[0]['id']
                logger.info(f"Successfully inserted job: {job_data.get('title', 'Untitled')}")
                return job_id
            else:
                logger.error(f"Failed to insert job: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error storing job: {str(e)}")
            return None
    
    async def store_training_program(self, program_data: Dict) -> Optional[str]:
        """Store a training program in the training_programs table.
        
        Args:
            program_data: Dictionary containing program data with the following fields:
                title: Program title
                provider: Program provider
                description: Program description
                duration: Program duration
                cost: Program cost (optional)
                skills_covered: List of skills covered by the program
        
        Returns:
            str: ID of inserted record or None if failed
        """
        try:
            await self.rate_limiter.wait()
            
            # Insert into Supabase
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/training_programs",
                headers=SUPABASE_HEADERS,
                json=program_data
            )
            
            if response.status_code == 201 and response.json():
                program_id = response.json()[0]['id']
                logger.info(f"Successfully inserted training program: {program_data.get('title', 'Untitled')}")
                return program_id
            else:
                logger.error(f"Failed to insert training program: {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error storing training program: {str(e)}")
            return None
    
    async def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search climate memories using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        try:
            # Get embedding for query
            embedding = await self.get_embedding(query)
            if not embedding:
                logger.warning("Could not generate embedding for query, using text search only")
                return await self.text_search_memories(query, limit)
            
            await self.rate_limiter.wait()
            
            # Call the match_memories function
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/rpc/match_memories",
                headers=SUPABASE_HEADERS,
                json={
                    "query_embedding": embedding,
                    "match_threshold": 0.5,
                    "match_count": limit
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to search memories: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return []
    
    async def text_search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search climate memories using text search.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching memories
        """
        try:
            await self.rate_limiter.wait()
            
            # Encode the query to handle special characters
            encoded_query = requests.utils.quote(query)
            
            # Search using text similarity
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/climate_memories?select=*&content=ilike.*{encoded_query}*&limit={limit}",
                headers=SUPABASE_HEADERS
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to text search memories: {response.status_code} {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error text searching memories: {str(e)}")
            return [] 