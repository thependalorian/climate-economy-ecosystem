#!/usr/bin/env python3
"""
Script to optimize the policy for the Massachusetts Climate Assistant using the trained reward model
"""

import os
import asyncio
import logging
import json
import sys
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoModelForSequenceClassification,
    Trainer, 
    TrainingArguments
)
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from trl.core import respond_to_batch
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ClimatePolicyOptimizer:
    """Policy optimizer for the Massachusetts Climate Assistant"""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        base_model_name: str = "gpt2",
        reward_model_path: str = "models/climate_reward_model/best_model",
        output_dir: str = "models/climate_policy_model",
        device: str = None
    ):
        """Initialize the policy optimizer"""
        from supabase.client import create_client
        
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.base_model_name = base_model_name
        self.reward_model_path = reward_model_path
        self.output_dir = output_dir
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize Supabase client
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize tokenizer and models
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        
        # Add special tokens if needed
        special_tokens = {"pad_token": "<PAD>"}
        if self.tokenizer.pad_token is None:
            self.tokenizer.add_special_tokens(special_tokens)
        
        # Load base policy model
        self.policy_model = AutoModelForCausalLMWithValueHead.from_pretrained(base_model_name)
        self.policy_model.to(self.device)
        
        # Resize token embeddings if special tokens were added
        self.policy_model.resize_token_embeddings(len(self.tokenizer))
        
        # Load reward model
        self.reward_model = AutoModelForSequenceClassification.from_pretrained(reward_model_path)
        self.reward_model.to(self.device)
        self.reward_model.eval()  # Set to evaluation mode
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Climate Policy Optimizer with base model: {base_model_name}")
    
    async def fetch_training_queries(self, limit=1000):
        """Fetch training queries from Supabase"""
        logger.info(f"Fetching up to {limit} training queries from Supabase...")
        
        # Get queries from messages
        query = f"""
        SELECT DISTINCT m.metadata->>'query' as query
        FROM messages m
        WHERE m.role = 'assistant'
          AND m.metadata->>'query' IS NOT NULL
        ORDER BY random()
        LIMIT {limit}
        """
        
        result = await self.supabase.rpc('run_sql', {'query': query}).execute()
        
        if not result.data:
            logger.warning("No queries found")
            return []
        
        # Extract queries
        queries = [item['query'] for item in result.data if item['query']]
        logger.info(f"Fetched {len(queries)} unique queries")
        
        return queries
    
    def compute_reward(self, queries, responses):
        """Compute rewards using the reward model"""
        rewards = []
        
        # Process in batches to avoid OOM
        batch_size = 8
        num_batches = (len(queries) + batch_size - 1) // batch_size
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(queries))
            
            batch_queries = queries[start_idx:end_idx]
            batch_responses = responses[start_idx:end_idx]
            
            # Combine queries and responses
            inputs = [f"Query: {q}\nResponse: {r}" for q, r in zip(batch_queries, batch_responses)]
            
            # Tokenize
            encodings = self.tokenizer(
                inputs,
                truncation=True,
                padding="max_length",
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Get reward scores
            with torch.no_grad():
                outputs = self.reward_model(**encodings)
                batch_rewards = outputs.logits.squeeze().cpu().numpy()
            
            rewards.extend(batch_rewards.tolist() if isinstance(batch_rewards, np.ndarray) else [batch_rewards])
        
        # Normalize rewards
        rewards = np.array(rewards)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-8)
        
        return rewards
    
    def train_ppo(self, queries, batch_size=4, epochs=3, learning_rate=1e-5):
        """Train the policy model using PPO"""
        logger.info(f"Training policy model with PPO for {epochs} epochs...")
        
        # Configure PPO
        ppo_config = PPOConfig(
            batch_size=batch_size,
            learning_rate=learning_rate,
            ppo_epochs=epochs,
            model_name=self.base_model_name,
            remove_unused_columns=False
        )
        
        # Initialize PPO trainer
        ppo_trainer = PPOTrainer(
            config=ppo_config,
            model=self.policy_model,
            tokenizer=self.tokenizer
        )
        
        # Training loop
        for epoch in range(epochs):
            logger.info(f"Starting epoch {epoch+1}/{epochs}")
            
            # Process queries in batches
            for i in range(0, len(queries), batch_size):
                batch_queries = queries[i:i+batch_size]
                
                # Tokenize queries
                query_tensors = [
                    self.tokenizer.encode(query, return_tensors="pt").to(self.device)
                    for query in batch_queries
                ]
                
                # Generate responses
                response_tensors = []
                for query_tensor in query_tensors:
                    response = respond_to_batch(
                        ppo_trainer.model,
                        query_tensor,
                        self.tokenizer,
                        max_new_tokens=128
                    )
                    response_tensors.append(response)
                
                # Decode responses
                responses = [
                    self.tokenizer.decode(response_tensor[0], skip_special_tokens=True)
                    for response_tensor in response_tensors
                ]
                
                # Remove the query from the response
                responses = [
                    response[len(query):].strip() 
                    for query, response in zip(batch_queries, responses)
                ]
                
                # Compute rewards
                rewards = self.compute_reward(batch_queries, responses)
                
                # Update model with PPO
                stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
                
                # Log stats
                logger.info(f"Epoch {epoch+1}/{epochs} - Batch {i//batch_size + 1} - "
                           f"Mean reward: {stats['ppo/mean_reward']:.4f}, "
                           f"Policy loss: {stats['ppo/loss/policy']:.4f}, "
                           f"Value loss: {stats['ppo/loss/value']:.4f}")
        
        # Save the optimized model
        self.save_model(os.path.join(self.output_dir, "final_model"))
        
        return self.policy_model
    
    def save_model(self, path):
        """Save the policy model and tokenizer"""
        self.policy_model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save training metadata
        metadata = {
            "base_model_name": self.base_model_name,
            "reward_model_path": self.reward_model_path,
            "saved_at": datetime.now().isoformat(),
            "device": self.device
        }
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Policy model saved to {path}")

async def main():
    """Main function to optimize the policy"""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not all([supabase_url, supabase_key]):
        logger.error("Missing required environment variables")
        return
    
    # Initialize optimizer
    optimizer = ClimatePolicyOptimizer(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        base_model_name="gpt2",
        reward_model_path="models/climate_reward_model/best_model",
        output_dir="models/climate_policy_model"
    )
    
    # Fetch training queries
    queries = await optimizer.fetch_training_queries(limit=100)  # Start with a small number for testing
    
    if not queries:
        logger.error("No queries available for training")
        return
    
    # Train policy model
    optimizer.train_ppo(
        queries=queries,
        batch_size=4,
        epochs=3,
        learning_rate=1e-5
    )
    
    logger.info("Policy optimization complete")

if __name__ == "__main__":
    asyncio.run(main())
