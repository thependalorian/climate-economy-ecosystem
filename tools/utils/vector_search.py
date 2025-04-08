#!/usr/bin/env python3
"""
Utility functions for vector embedding generation and similarity search.
These functions provide vector search capabilities for the climate economy ecosystem.
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VectorSearchClient:
    """Client for generating embeddings and performing vector similarity search."""
    
    def __init__(self):
        """Initialize the vector search client."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client if API key is available
        self.openai_client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
        # Default embedding model
        self.embedding_model = "text-embedding-3-small"
        
        logger.info("Vector search client initialized")
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            Embedding vector or None if API key is missing or an error occurs
        """
        if not self.openai_client:
            logger.error("Cannot generate embedding: OpenAI API key not available")
            return None
        
        try:
            logger.info(f"Generating embedding for text (length: {len(text)})")
            
            # Truncate text if necessary (OpenAI has token limits)
            if len(text) > 8000:
                logger.warning(f"Text too long ({len(text)} chars), truncating to 8000 chars")
                text = text[:8000]
            
            # Generate embedding using OpenAI API
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            
            # Extract the embedding vector
            embedding = response.data[0].embedding
            
            logger.info(f"Successfully generated embedding (dimensions: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (float between -1 and 1)
        """
        if not vec1 or not vec2:
            return 0.0
        
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            cosine_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            return float(cosine_sim)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    async def calculate_similarities(self, query_embedding: List[float], item_embeddings: List[Tuple[str, List[float]]]) -> List[Tuple[str, float]]:
        """
        Calculate similarities between a query embedding and a list of item embeddings.
        
        Args:
            query_embedding: The query embedding vector
            item_embeddings: A list of tuples (item_id, embedding_vector)
            
        Returns:
            A list of tuples (item_id, similarity_score) sorted by similarity
        """
        if not query_embedding or not item_embeddings:
            return []
        
        try:
            # Calculate similarity for each item
            similarities = []
            for item_id, embedding in item_embeddings:
                similarity = self.cosine_similarity(query_embedding, embedding)
                similarities.append((item_id, similarity))
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error calculating similarities: {str(e)}")
            return []
    
    def _mock_embedding(self, dimensions: int = 1536) -> List[float]:
        """
        Generate a mock embedding for testing purposes.
        
        Args:
            dimensions: Number of dimensions for the mock embedding
            
        Returns:
            Mock embedding vector
        """
        return list(np.random.randn(dimensions).astype(float))
    
    async def generate_bulk_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors (or None for failed embeddings)
        """
        if not self.openai_client:
            logger.error("Cannot generate embeddings: OpenAI API key not available")
            return [None] * len(texts)
        
        embeddings = []
        try:
            for i, text in enumerate(texts):
                logger.info(f"Generating embedding {i+1}/{len(texts)}")
                embedding = await self.generate_embedding(text)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating bulk embeddings: {str(e)}")
            return [None] * len(texts)

# Example usage:
# async def example():
#     vector_client = VectorSearchClient()
#     
#     # Generate an embedding for a query
#     query = "renewable energy policies"
#     query_embedding = await vector_client.generate_embedding(query)
#     
#     # Generate embeddings for some documents
#     docs = [
#         "Renewable energy policies in the United States",
#         "Climate change mitigation strategies",
#         "Fossil fuel industry challenges"
#     ]
#     
#     # Create mock embeddings for documents (in real use, you would use generate_embedding)
#     doc_embeddings = []
#     for i, doc in enumerate(docs):
#         doc_embedding = await vector_client.generate_embedding(doc)
#         doc_embeddings.append((f"doc_{i}", doc_embedding))
#     
#     # Calculate similarities
#     similarities = await vector_client.calculate_similarities(query_embedding, doc_embeddings)
#     
#     # Print results
#     for doc_id, score in similarities:
#         doc_index = int(doc_id.split("_")[1])
#         print(f"Score: {score:.4f} - {docs[doc_index]}") 