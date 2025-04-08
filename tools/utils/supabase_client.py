#!/usr/bin/env python3
"""
Utility functions for interacting with Supabase in the climate economy ecosystem tools.
"""

import os
import logging
import httpx
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SupabaseClient:
    """
    A client for interacting with Supabase in climate economy ecosystem tools.
    This class provides methods for fetching memories, organizations, and other data.
    """
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("Supabase URL or service key not found in environment variables")
            raise ValueError("Supabase URL or service key not found in environment variables")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        logger.info("Supabase client initialized")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Supabase.
        
        Returns:
            dict: A dictionary with connection status information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/?apikey={self.supabase_key}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info("Successfully connected to Supabase")
                    return {"status": "success", "message": "Successfully connected to Supabase"}
                else:
                    logger.error(f"Failed to connect to Supabase: {response.status_code} - {response.text}")
                    return {"status": "error", "message": f"Failed to connect to Supabase: {response.status_code} - {response.text}"}
        except Exception as e:
            logger.error(f"Error connecting to Supabase: {str(e)}")
            return {"status": "error", "message": f"Error connecting to Supabase: {str(e)}"}

    async def fetch_memories(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Fetch memories from Supabase.
        
        Args:
            limit: The maximum number of memories to fetch
            offset: The offset to start fetching from
            
        Returns:
            list: A list of memories
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/memories",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "order": "created_at.desc",
                        "limit": limit,
                        "offset": offset
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    logger.info(f"Successfully fetched {len(memories)} memories")
                    return memories
                else:
                    logger.error(f"Failed to fetch memories: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching memories: {str(e)}")
            return []

    async def fetch_organizations(self) -> List[Dict[str, Any]]:
        """
        Fetch organizations from Supabase.
        
        Returns:
            list: A list of organizations
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/organizations",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "order": "name"
                    }
                )
                
                if response.status_code == 200:
                    organizations = response.json()
                    logger.info(f"Successfully fetched {len(organizations)} organizations")
                    return organizations
                else:
                    logger.error(f"Failed to fetch organizations: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching organizations: {str(e)}")
            return []

    async def fetch_organization_types(self) -> List[Dict[str, Any]]:
        """
        Fetch organization types from Supabase.
        
        Returns:
            list: A list of organization types
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/organization_types",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "order": "name"
                    }
                )
                
                if response.status_code == 200:
                    org_types = response.json()
                    logger.info(f"Successfully fetched {len(org_types)} organization types")
                    return org_types
                else:
                    logger.error(f"Failed to fetch organization types: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching organization types: {str(e)}")
            return []

    async def fetch_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to fetch
            
        Returns:
            dict: The memory data, or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/memories",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "id": f"eq.{memory_id}"
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    if memories:
                        logger.info(f"Successfully fetched memory {memory_id}")
                        return memories[0]
                    else:
                        logger.error(f"Memory {memory_id} not found")
                        return None
                else:
                    logger.error(f"Failed to fetch memory {memory_id}: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching memory {memory_id}: {str(e)}")
            return None

    async def search_memories(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search memories using full text search.
        
        Args:
            query: The search query
            limit: The maximum number of results to return
            
        Returns:
            list: A list of matching memories
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/memories",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "text_content": f"ilike.%{query}%",
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    logger.info(f"Successfully searched memories, found {len(memories)} results")
                    return memories
                else:
                    logger.error(f"Failed to search memories: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return []

    async def fetch_memories_by_organization(self, organization_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch memories for a specific organization.
        
        Args:
            organization_id: The ID of the organization
            limit: The maximum number of memories to fetch
            
        Returns:
            list: A list of memories for the organization
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/memories",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "organization_id": f"eq.{organization_id}",
                        "order": "created_at.desc",
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    logger.info(f"Successfully fetched {len(memories)} memories for organization {organization_id}")
                    return memories
                else:
                    logger.error(f"Failed to fetch memories for organization {organization_id}: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching memories for organization {organization_id}: {str(e)}")
            return []

    async def fetch_memories_by_domain(self, domain: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch memories for a specific domain.
        
        Args:
            domain: The domain to fetch memories for
            limit: The maximum number of memories to fetch
            
        Returns:
            list: A list of memories for the domain
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/memories",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "source_url": f"ilike.%{domain}%",
                        "order": "created_at.desc",
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    logger.info(f"Successfully fetched {len(memories)} memories for domain {domain}")
                    return memories
                else:
                    logger.error(f"Failed to fetch memories for domain {domain}: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching memories for domain {domain}: {str(e)}")
            return []

    async def get_organization_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get an organization by name.
        
        Args:
            name: The name of the organization
            
        Returns:
            dict: The organization data, or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/organizations",
                    headers=self.headers,
                    params={
                        "select": "*",
                        "name": f"ilike.{name}"
                    }
                )
                
                if response.status_code == 200:
                    orgs = response.json()
                    if orgs:
                        logger.info(f"Successfully found organization: {name}")
                        return orgs[0]
                    else:
                        logger.warning(f"Organization not found: {name}")
                        return None
                else:
                    logger.error(f"Failed to get organization {name}: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error getting organization {name}: {str(e)}")
            return None

    async def save_analysis_result(self, analysis_type: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Save an analysis result to Supabase.
        
        Args:
            analysis_type: The type of analysis (e.g., 'content', 'relationship')
            analysis_data: The analysis data to save
            
        Returns:
            dict: The saved analysis result, or None if there was an error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.supabase_url}/rest/v1/analysis_results",
                    headers=self.headers,
                    json={
                        "analysis_type": analysis_type,
                        "analysis_data": analysis_data
                    }
                )
                
                if response.status_code in (200, 201):
                    result = response.json()
                    logger.info(f"Successfully saved {analysis_type} analysis result")
                    return result
                else:
                    logger.error(f"Failed to save analysis result: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error saving analysis result: {str(e)}")
            return None 