#!/usr/bin/env python3
"""
Setup script for the Massachusetts Climate Retriever
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.retrieval.massachusetts_climate_retriever import MassachusettsClimateRetriever, MassachusettsClimateConstraints

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

async def setup_retriever():
    """Set up the Massachusetts Climate Retriever and ingest reports"""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not all([supabase_url, supabase_key, openai_api_key]):
        logger.error("Missing required environment variables")
        return False
    
    # Create custom constraints
    constraints = MassachusettsClimateConstraints(
        geographic_focus="Massachusetts",
        allowed_topics=[
            "clean energy careers", 
            "renewable energy", 
            "energy efficiency", 
            "workforce development",
            "climate economy",
            "green jobs",
            "training programs",
            "environmental justice",
            "clean energy policy",
            "Massachusetts climate initiatives"
        ],
        prohibited_topics=[
            "climate change denial",
            "fossil fuel advocacy",
            "political endorsements",
            "non-Massachusetts specific programs",
            "personal financial advice",
            "medical advice"
        ],
        source_requirements={
            "require_massachusetts_source": True,
            "max_source_age_years": 3,
            "preferred_sources": [
                "MassCEC", 
                "Massachusetts government", 
                "NECEC",
                "Massachusetts educational institutions"
            ]
        },
        response_requirements={
            "cite_sources": True,
            "acknowledge_uncertainty": True,
            "provide_massachusetts_context": True,
            "highlight_ej_considerations": True
        }
    )
    
    # Initialize retriever
    retriever = MassachusettsClimateRetriever(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_api_key=openai_api_key,
        constraints=constraints,
        collection_name="climate_memories",
        model_name="gpt-4o"
    )
    
    # Ingest required reports
    logger.info("Ingesting required reports...")
    results = await retriever.ingest_required_reports()
    
    # Log results
    success_count = sum(1 for result in results.values() if result)
    logger.info(f"Ingestion complete: {success_count}/{len(results)} reports successfully ingested")
    
    return retriever

if __name__ == "__main__":
    asyncio.run(setup_retriever())
