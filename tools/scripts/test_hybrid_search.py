#!/usr/bin/env python3
"""
Test script for hybrid search functionality in the climate economy ecosystem.
This script demonstrates using a combination of text-based search and 
vector similarity search to find relevant climate economy data.
"""

import os
import sys
import asyncio
import logging
import argparse
from typing import List, Dict, Any, Tuple
import numpy as np
from dotenv import load_dotenv

# Add parent directory to path so we can import the utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.supabase_client import SupabaseClient
from utils.data_processing import clean_text, setup_nltk
from utils.vector_search import VectorSearchClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hybrid_search.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hybrid_search")

# Load environment variables
load_dotenv()

# Initialize NLTK
setup_nltk()

class HybridSearch:
    """Class for performing hybrid search on climate economy data."""
    
    def __init__(self, text_weight=0.6, vector_weight=0.4):
        """
        Initialize the hybrid search engine.
        
        Args:
            text_weight: Weight for text search results (0-1)
            vector_weight: Weight for vector similarity results (0-1)
        """
        self.supabase_client = SupabaseClient()
        self.vector_client = VectorSearchClient()
        self.text_search_weight = text_weight
        self.vector_search_weight = vector_weight
        
        logger.info(f"Initialized hybrid search with text_weight={text_weight}, vector_weight={vector_weight}")
    
    async def text_search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Perform text-based search using Supabase.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of search results
        """
        logger.info(f"Performing text search for: '{query}'")
        return await self.supabase_client.search_memories(query, limit=limit)
    
    async def vector_search(self, query_embedding: List[float], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query_embedding: The query embedding vector
            limit: Maximum number of results to return
            
        Returns:
            List of search results
        """
        logger.info("Performing vector similarity search")
        
        # In a production implementation, this would fetch embeddings from the database
        # and compare them to the query embedding
        
        # For demonstration, we'll:
        # 1. Get some memories from Supabase
        # 2. Generate embeddings for their content
        # 3. Calculate similarity with the query embedding
        # 4. Return the most similar memories
        
        try:
            # Get some memories to compare against
            memories = await self.supabase_client.fetch_memories(limit=100)
            
            if not memories:
                logger.warning("No memories found for vector search")
                return []
            
            # Create a list to hold memory tuples (id, content)
            memory_data = []
            for memory in memories:
                memory_id = memory.get('id')
                content = memory.get('content', '')
                if memory_id and content:
                    memory_data.append((memory_id, content))
            
            # Generate embeddings for memory content
            # In a real implementation, these would be pre-computed and stored
            memory_embeddings = []
            for memory_id, content in memory_data:
                logger.info(f"Generating embedding for memory {memory_id}")
                
                # For testing speed, we can use mock embeddings
                use_mock = False
                if use_mock:
                    embedding = self.vector_client._mock_embedding()
                else:
                    embedding = await self.vector_client.generate_embedding(content)
                
                if embedding:
                    memory_embeddings.append((memory_id, embedding))
            
            # Calculate similarity scores
            if not memory_embeddings:
                logger.warning("No memory embeddings generated")
                return []
            
            # Get similarity scores
            similarities = await self.vector_client.calculate_similarities(
                query_embedding, 
                memory_embeddings
            )
            
            # Retrieve full memory objects for the top results
            result_memories = []
            for memory_id, score in similarities[:limit]:
                for memory in memories:
                    if memory.get('id') == memory_id:
                        # Add similarity score to the memory object
                        memory['similarity_score'] = score
                        result_memories.append(memory)
                        break
            
            logger.info(f"Vector search found {len(result_memories)} similar memories")
            return result_memories
            
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            
            # Fallback to text search
            logger.info("Falling back to text search for vector search results")
            fallback_results = await self.supabase_client.search_memories("climate economy", limit=limit)
            return fallback_results
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate an embedding vector for the query.
        
        Args:
            query: The search query
            
        Returns:
            Embedding vector for the query
        """
        logger.info(f"Generating embedding for query: '{query}'")
        
        # Use VectorSearchClient to generate the embedding
        embedding = await self.vector_client.generate_embedding(query)
        
        # Fallback to mock embedding if real one fails
        if not embedding:
            logger.warning("Using mock embedding as fallback")
            embedding = self.vector_client._mock_embedding()
        
        return embedding
    
    def combine_search_results(
        self, 
        text_results: List[Dict[str, Any]], 
        vector_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine and rank results from text search and vector search.
        
        Args:
            text_results: Results from text search
            vector_results: Results from vector search
            
        Returns:
            Combined and ranked search results
        """
        logger.info("Combining text and vector search results")
        
        # Create a dictionary to store combined results with scores
        combined_results = {}
        
        # Process text search results
        for i, result in enumerate(text_results):
            result_id = result.get('id')
            if result_id:
                # Calculate a score based on position (higher position = higher score)
                text_score = 1.0 - (i / len(text_results)) if len(text_results) > 0 else 0
                
                combined_results[result_id] = {
                    'result': result,
                    'text_score': text_score,
                    'vector_score': 0,  # Will be updated if found in vector results
                    'combined_score': text_score * self.text_search_weight
                }
        
        # Process vector search results
        for i, result in enumerate(vector_results):
            result_id = result.get('id')
            if result_id:
                # Get vector score (either from similarity score or position)
                if 'similarity_score' in result:
                    # Use actual similarity score if available
                    vector_score = result['similarity_score']
                else:
                    # Otherwise, calculate score based on position
                    vector_score = 1.0 - (i / len(vector_results)) if len(vector_results) > 0 else 0
                
                if result_id in combined_results:
                    # Update existing result
                    combined_results[result_id]['vector_score'] = vector_score
                    combined_results[result_id]['combined_score'] += vector_score * self.vector_search_weight
                else:
                    # Add new result
                    combined_results[result_id] = {
                        'result': result,
                        'text_score': 0,  # Not found in text results
                        'vector_score': vector_score,
                        'combined_score': vector_score * self.vector_search_weight
                    }
        
        # Sort combined results by combined score
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        # Extract just the result data
        final_results = [item['result'] for item in sorted_results]
        
        return final_results
    
    async def hybrid_search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Perform hybrid search using both text and vector similarity.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of search results
        """
        logger.info(f"Performing hybrid search for: '{query}'")
        
        # Clean the query
        clean_query = clean_text(query)
        if not clean_query:
            clean_query = query  # Use original if cleaning removes everything
        
        # Perform text search
        text_results = await self.text_search(clean_query, limit=limit*2)
        
        # Generate query embedding
        query_embedding = await self.generate_query_embedding(clean_query)
        
        # Perform vector search
        vector_results = await self.vector_search(query_embedding, limit=limit*2)
        
        # Combine and rank results
        combined_results = self.combine_search_results(text_results, vector_results)
        
        # Return top results
        return combined_results[:limit]

async def run_single_query(query: str, limit: int, text_weight: float, vector_weight: float):
    """
    Run a hybrid search with a single query.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        text_weight: Weight for text search results
        vector_weight: Weight for vector similarity results
    """
    print("\n" + "=" * 50)
    print(f"HYBRID SEARCH: '{query}'")
    print("=" * 50)
    
    # Initialize hybrid search with weights
    search_engine = HybridSearch(text_weight=text_weight, vector_weight=vector_weight)
    
    # Perform hybrid search
    results = await search_engine.hybrid_search(query, limit=limit)
    
    # Display results
    if results:
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            content_preview = result.get('content', '')[:150] + '...' if result.get('content') else 'No content'
            source = result.get('source_url', 'Unknown source')
            
            # Display scores if available
            text_score = result.get('text_score', 'N/A')
            vector_score = result.get('vector_score', 'N/A')
            combined_score = result.get('combined_score', 'N/A')
            
            print(f"\n{i}. {title}")
            print(f"   Source: {source}")
            print(f"   Preview: {content_preview}")
            
            if isinstance(text_score, (int, float)) and isinstance(vector_score, (int, float)) and isinstance(combined_score, (int, float)):
                print(f"   Scores: Text={text_score:.2f}, Vector={vector_score:.2f}, Combined={combined_score:.2f}")
    else:
        print("\nNo results found.")

async def test_hybrid_search():
    """Test the hybrid search functionality with multiple predefined queries."""
    logger.info("Starting hybrid search test with multiple queries")
    
    # Initialize hybrid search
    search_engine = HybridSearch()
    
    # Test queries
    test_queries = [
        "renewable energy technologies",
        "climate finance initiatives",
        "carbon capture projects",
        "green hydrogen development",
        "climate adaptation strategies"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 50)
        print(f"TESTING HYBRID SEARCH: '{query}'")
        print("=" * 50)
        
        # Perform hybrid search
        results = await search_engine.hybrid_search(query, limit=5)
        
        # Display results
        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                content_preview = result.get('content', '')[:150] + '...' if result.get('content') else 'No content'
                source = result.get('source_url', 'Unknown source')
                
                print(f"\n{i}. {title}")
                print(f"   Source: {source}")
                print(f"   Preview: {content_preview}")
        else:
            print("\nNo results found.")
    
    print("\n" + "=" * 50)
    print("HYBRID SEARCH TEST COMPLETED")
    print("=" * 50)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Hybrid search for climate economy data")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    parser.add_argument("--text-weight", type=float, default=0.6, help="Weight for text search results (0-1, default: 0.6)")
    parser.add_argument("--vector-weight", type=float, default=0.4, help="Weight for vector search results (0-1, default: 0.4)")
    parser.add_argument("--test", action="store_true", help="Run test with multiple predefined queries")
    return parser.parse_args()

async def main():
    """Main entry point."""
    print("\n" + "=" * 50)
    print(" CLIMATE ECONOMY ECOSYSTEM - HYBRID SEARCH ")
    print("=" * 50 + "\n")
    
    # Parse command line arguments
    args = parse_args()
    
    try:
        # Test Supabase connection first
        client = SupabaseClient()
        connection_result = await client.test_connection()
        
        if connection_result["status"] == "success":
            logger.info("✅ Successfully connected to Supabase")
            
            if args.test:
                # Run hybrid search test with multiple queries
                await test_hybrid_search()
            elif args.query:
                # Run hybrid search with a single query
                await run_single_query(
                    query=args.query,
                    limit=args.limit,
                    text_weight=args.text_weight,
                    vector_weight=args.vector_weight
                )
            else:
                print("Please provide a search query using --query or run the test with --test")
                return 1
            
            print("\n" + "=" * 50)
            print(" ✅ HYBRID SEARCH COMPLETED ")
            print("=" * 50 + "\n")
            
            return 0
            
        else:
            logger.error(f"❌ Failed to connect to Supabase: {connection_result['message']}")
            print("\n" + "=" * 50)
            print(" ❌ SUPABASE CONNECTION FAILED - CANNOT RUN HYBRID SEARCH ")
            print("=" * 50 + "\n")
            
            return 1
            
    except Exception as e:
        logger.error(f"Error during hybrid search: {str(e)}")
        print("\n" + "=" * 50)
        print(" ❌ HYBRID SEARCH FAILED WITH ERROR ")
        print("=" * 50 + "\n")
        print(f"Error: {str(e)}")
        
        return 1
    
    finally:
        print("Check hybrid_search.log for detailed information.")

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 