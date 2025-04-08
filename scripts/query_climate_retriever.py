#!/usr/bin/env python3
"""
Script to query the Massachusetts Climate Retriever
"""

import os
import asyncio
import logging
import json
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.retrieval.massachusetts_climate_retriever import MassachusettsClimateRetriever, MassachusettsClimateConstraints

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def query_retriever(query: str):
    """Query the Massachusetts Climate Retriever"""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not all([supabase_url, supabase_key, openai_api_key]):
        logger.error("Missing required environment variables")
        return json.dumps({
            "error": "Missing required environment variables",
            "success": False
        })
    
    # Create constraints
    constraints = MassachusettsClimateConstraints()
    
    # Initialize retriever
    retriever = MassachusettsClimateRetriever(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_api_key=openai_api_key,
        constraints=constraints,
        collection_name="climate_memories",
        model_name="gpt-4o"
    )
    
    # Query the retriever
    result = await retriever.query(query)
    
    # Return the result as JSON
    return json.dumps(result, default=str)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_climate_retriever.py 'your query here'")
        sys.exit(1)
    
    query = sys.argv[1]
    result = asyncio.run(query_retriever(query))
    print(result)
