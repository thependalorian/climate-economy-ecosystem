#!/usr/bin/env python3
"""
Script to evaluate the improvements from RLHF for the Massachusetts Climate Assistant
"""

import os
import asyncio
import logging
import json
import sys
import torch
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
from sklearn.metrics import mean_squared_error, mean_absolute_error
import seaborn as sns

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RLHFEvaluator:
    """Evaluator for RLHF improvements"""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        base_model_name: str = "gpt2",
        optimized_model_path: str = "models/climate_policy_model/final_model",
        reward_model_path: str = "models/climate_reward_model/best_model",
        output_dir: str = "evaluation_results",
        device: str = None
    ):
        """Initialize the RLHF evaluator"""
        from supabase.client import create_client
        
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.base_model_name = base_model_name
        self.optimized_model_path = optimized_model_path
        self.reward_model_path = reward_model_path
        self.output_dir = output_dir
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize Supabase client
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize tokenizers and models
        self.base_tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
        self.base_model.to(self.device)
        
        # Add special tokens if needed
        if self.base_tokenizer.pad_token is None:
            self.base_tokenizer.pad_token = self.base_tokenizer.eos_token
        
        # Load optimized model if it exists
        if os.path.exists(optimized_model_path):
            self.optimized_tokenizer = AutoTokenizer.from_pretrained(optimized_model_path)
            self.optimized_model = AutoModelForCausalLM.from_pretrained(optimized_model_path)
            self.optimized_model.to(self.device)
        else:
            logger.warning(f"Optimized model not found at {optimized_model_path}")
            self.optimized_tokenizer = None
            self.optimized_model = None
        
        # Load reward model
        self.reward_tokenizer = AutoTokenizer.from_pretrained(reward_model_path)
        self.reward_model = AutoModelForSequenceClassification.from_pretrained(reward_model_path)
        self.reward_model.to(self.device)
        self.reward_model.eval()  # Set to evaluation mode
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("Initialized RLHF Evaluator")
    
    async def fetch_test_queries(self, limit=100):
        """Fetch test queries from Supabase"""
        logger.info(f"Fetching up to {limit} test queries from Supabase...")
        
        # Get queries with high-quality feedback
        query = f"""
        SELECT DISTINCT m.metadata->>'query' as query
        FROM messages m
        JOIN chat_feedback cf ON m.id = cf.message_id
        WHERE m.role = 'assistant'
          AND m.metadata->>'query' IS NOT NULL
          AND cf.rating >= 4
        ORDER BY random()
        LIMIT {limit}
        """
        
        result = await self.supabase.rpc('run_sql', {'query': query}).execute()
        
        if not result.data:
            logger.warning("No high-quality queries found, fetching random queries")
            
            # Fall back to random queries
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
            logger.error("No queries found")
            return []
        
        # Extract queries
        queries = [item['query'] for item in result.data if item['query']]
        logger.info(f"Fetched {len(queries)} test queries")
        
        return queries
    
    def generate_responses(self, queries, model, tokenizer, max_length=256):
        """Generate responses using the specified model"""
        responses = []
        
        for query in tqdm(queries, desc="Generating responses"):
            # Tokenize query
            inputs = tokenizer(query, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                output = model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=tokenizer.pad_token_id
                )
            
            # Decode response
            response = tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Remove the query from the response
            response = response[len(query):].strip()
            responses.append(response)
        
        return responses
    
    def compute_rewards(self, queries, responses):
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
            encodings = self.reward_tokenizer(
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
        
        return rewards
    
    def evaluate(self, queries):
        """Evaluate base and optimized models"""
        logger.info("Evaluating models...")
        
        # Check if optimized model is available
        if self.optimized_model is None:
            logger.error("Optimized model not available for evaluation")
            return None
        
        # Generate responses from base model
        logger.info("Generating responses from base model...")
        base_responses = self.generate_responses(
            queries, 
            self.base_model, 
            self.base_tokenizer
        )
        
        # Generate responses from optimized model
        logger.info("Generating responses from optimized model...")
        optimized_responses = self.generate_responses(
            queries, 
            self.optimized_model, 
            self.optimized_tokenizer
        )
        
        # Compute rewards
        logger.info("Computing rewards for base model responses...")
        base_rewards = self.compute_rewards(queries, base_responses)
        
        logger.info("Computing rewards for optimized model responses...")
        optimized_rewards = self.compute_rewards(queries, optimized_responses)
        
        # Prepare results
        results = {
            "queries": queries,
            "base_responses": base_responses,
            "optimized_responses": optimized_responses,
            "base_rewards": base_rewards,
            "optimized_rewards": optimized_rewards,
            "base_mean_reward": np.mean(base_rewards),
            "optimized_mean_reward": np.mean(optimized_rewards),
            "reward_improvement": np.mean(optimized_rewards) - np.mean(base_rewards),
            "reward_improvement_percentage": (np.mean(optimized_rewards) - np.mean(base_rewards)) / np.abs(np.mean(base_rewards)) * 100
        }
        
        # Save results
        self._save_results(results)
        
        # Generate visualizations
        self._generate_visualizations(results)
        
        return results
    
    def _save_results(self, results):
        """Save evaluation results"""
        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(self.output_dir, f"evaluation_{timestamp}")
        os.makedirs(results_dir, exist_ok=True)
        
        # Save summary
        summary = {
            "base_model": self.base_model_name,
            "optimized_model": self.optimized_model_path,
            "reward_model": self.reward_model_path,
            "num_queries": len(results["queries"]),
            "base_mean_reward": float(results["base_mean_reward"]),
            "optimized_mean_reward": float(results["optimized_mean_reward"]),
            "reward_improvement": float(results["reward_improvement"]),
            "reward_improvement_percentage": float(results["reward_improvement_percentage"]),
            "evaluation_time": datetime.now().isoformat()
        }
        
        with open(os.path.join(results_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
        
        # Save detailed results
        detailed_results = []
        for i in range(len(results["queries"])):
            detailed_results.append({
                "query": results["queries"][i],
                "base_response": results["base_responses"][i],
                "optimized_response": results["optimized_responses"][i],
                "base_reward": float(results["base_rewards"][i]),
                "optimized_reward": float(results["optimized_rewards"][i]),
                "reward_improvement": float(results["optimized_rewards"][i] - results["base_rewards"][i])
            })
        
        with open(os.path.join(results_dir, "detailed_results.json"), "w") as f:
            json.dump(detailed_results, f, indent=2)
        
        # Save as CSV for easier analysis
        df = pd.DataFrame(detailed_results)
        df.to_csv(os.path.join(results_dir, "results.csv"), index=False)
        
        logger.info(f"Results saved to {results_dir}")
    
    def _generate_visualizations(self, results):
        """Generate visualizations of the evaluation results"""
        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(self.output_dir, f"evaluation_{timestamp}")
        os.makedirs(results_dir, exist_ok=True)
        
        # Reward distribution comparison
        plt.figure(figsize=(10, 6))
        sns.histplot(results["base_rewards"], kde=True, label="Base Model", alpha=0.6)
        sns.histplot(results["optimized_rewards"], kde=True, label="Optimized Model", alpha=0.6)
        plt.xlabel("Reward Score")
        plt.ylabel("Frequency")
        plt.title("Reward Distribution Comparison")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(results_dir, "reward_distribution.png"))
        
        # Reward improvement by query
        plt.figure(figsize=(12, 6))
        improvements = np.array(results["optimized_rewards"]) - np.array(results["base_rewards"])
        plt.bar(range(len(improvements)), improvements)
        plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        plt.xlabel("Query Index")
        plt.ylabel("Reward Improvement")
        plt.title("Reward Improvement by Query")
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(results_dir, "reward_improvement.png"))
        
        # Mean reward comparison
        plt.figure(figsize=(8, 6))
        models = ["Base Model", "Optimized Model"]
        mean_rewards = [results["base_mean_reward"], results["optimized_mean_reward"]]
        plt.bar(models, mean_rewards)
        plt.ylabel("Mean Reward")
        plt.title("Mean Reward Comparison")
        plt.grid(True, alpha=0.3)
        
        # Add values on top of bars
        for i, v in enumerate(mean_rewards):
            plt.text(i, v + 0.02, f"{v:.3f}", ha='center')
        
        plt.savefig(os.path.join(results_dir, "mean_reward_comparison.png"))
        
        logger.info(f"Visualizations saved to {results_dir}")

async def main():
    """Main function to evaluate RLHF improvements"""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not all([supabase_url, supabase_key]):
        logger.error("Missing required environment variables")
        return
    
    # Initialize evaluator
    evaluator = RLHFEvaluator(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        base_model_name="gpt2",
        optimized_model_path="models/climate_policy_model/final_model",
        reward_model_path="models/climate_reward_model/best_model",
        output_dir="evaluation_results"
    )
    
    # Fetch test queries
    queries = await evaluator.fetch_test_queries(limit=20)  # Start with a small number for testing
    
    if not queries:
        logger.error("No queries available for evaluation")
        return
    
    # Evaluate models
    results = evaluator.evaluate(queries)
    
    if results:
        logger.info(f"Evaluation complete. Reward improvement: {results['reward_improvement']:.4f} ({results['reward_improvement_percentage']:.2f}%)")
    else:
        logger.error("Evaluation failed")

if __name__ == "__main__":
    asyncio.run(main())
