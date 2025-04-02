#!/usr/bin/env python3
"""
RLHF Training Pipeline for Climate Economy Ecosystem

This script trains the reward model and performs RL fine-tuning
using human feedback data.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.ml.reward_model import ClimateRewardModel
from lib.ml.feedback_processor import FeedbackProcessor
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import PPOTrainer, PPOConfig
from trl.core import LengthSampler

def train_reward_model(args):
    """Train the reward model on feedback data"""
    print("Training reward model...")
    
    # Initialize processor and prepare data
    processor = FeedbackProcessor()
    train_data, test_data = processor.prepare_training_data()
    
    print(f"Prepared training data: {len(train_data)} examples")
    print(f"Prepared testing data: {len(test_data)} examples")
    
    # Initialize and train reward model
    reward_model = ClimateRewardModel(model_name=args.reward_base_model)
    training_stats = reward_model.train(
        train_data=train_data,
        validation_data=test_data,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate
    )
    
    # Save training stats
    stats_file = os.path.join(
        os.getcwd(), 
        'data', 
        'reward_model', 
        f'training_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )
    
    with open(stats_file, 'w') as f:
        json.dump(training_stats, f)
        
    print(f"Saved training stats to {stats_file}")
    print("Reward model training complete!")

def train_ppo(args):
    """Train language model with PPO using reward model"""
    print("Setting up PPO training...")
    
    # Load base model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(args.base_model)
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    
    # Ensure tokenizer has padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load reward model
    reward_model = ClimateRewardModel()
    
    # Initialize PPO config
    ppo_config = PPOConfig(
        batch_size=args.batch_size,
        mini_batch_size=args.mini_batch_size,
        learning_rate=args.ppo_learning_rate,
        optimize_cuda_cache=True,
        early_stopping=True,
        target_kl=0.1,
        kl_penalty=0.2
    )
    
    # Initialize PPO trainer
    ppo_trainer = PPOTrainer(
        config=ppo_config,
        model=model,
        tokenizer=tokenizer,
        ref_model=model,
        dataset=None  # Will use on-the-fly generation
    )
    
    # Get query data - use processor to get recent questions from chats
    processor = FeedbackProcessor()
    feedback_data = processor.fetch_feedback_data(days_back=90)
    queries = feedback_data['query'].unique().tolist()
    
    # If no queries, use some examples
    if not queries:
        queries = [
            "What clean energy jobs are available near Boston?",
            "How can I transition from oil and gas to renewable energy?",
            "What training programs are available for solar installation?",
            "How can I translate my military experience to clean energy?",
            "Are there clean energy opportunities in Springfield?"
        ]
    
    # Response length sampling
    response_length_sampler = LengthSampler(128, 384)
    
    # Train for specified number of steps
    print(f"Starting PPO training for {args.ppo_steps} steps...")
    
    for step in range(args.ppo_steps):
        # Sample queries
        batch_indices = list(range(len(queries)))
        if len(batch_indices) > args.batch_size:
            batch_indices = batch_indices[:args.batch_size]
        batch_queries = [queries[i] for i in batch_indices]
        
        # Tokenize queries
        query_tensors = [
            tokenizer(query, return_tensors="pt").input_ids.squeeze()
            for query in batch_queries
        ]
        
        # Generate responses from model
        response_tensors = []
        for query in query_tensors:
            response_length = response_length_sampler()
            response = ppo_trainer.generate(
                query.unsqueeze(0), 
                max_new_tokens=response_length
            )
            response_tensors.append(response.squeeze())
        
        # Decode responses
        batch_responses = [
            tokenizer.decode(response_tensor)
            for response_tensor in response_tensors
        ]
        
        # Compute rewards
        rewards = []
        for query, response in zip(batch_queries, batch_responses):
            reward = reward_model.compute_reward(query, response)
            rewards.append(reward)
        
        # Run PPO step
        stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
        
        # Log progress
        if step % 10 == 0:
            print(f"Step {step}: Mean reward = {stats['ppo/mean_scores']:.4f}")
    
    # Save fine-tuned model
    output_dir = os.path.join(
        os.getcwd(), 
        'data', 
        'rlhf_model', 
        f'model_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    )
    os.makedirs(output_dir, exist_ok=True)
    
    ppo_trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"Saved fine-tuned model to {output_dir}")
    print("PPO training complete!")

def main():
    parser = argparse.ArgumentParser(description="RLHF Training Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Reward model training arguments
    reward_parser = subparsers.add_parser("reward", help="Train reward model")
    reward_parser.add_argument("--reward-base-model", type=str, default="distilroberta-base",
                              help="Base model for reward model")
    reward_parser.add_argument("--batch-size", type=int, default=8,
                             help="Batch size for training")
    reward_parser.add_argument("--epochs", type=int, default=3,
                             help="Number of training epochs")
    reward_parser.add_argument("--learning-rate", type=float, default=2e-5,
                             help="Learning rate for optimizer")
    
    # PPO training arguments
    ppo_parser = subparsers.add_parser("ppo", help="Train with PPO")
    ppo_parser.add_argument("--base-model", type=str, required=True,
                          help="Base language model to fine-tune")
    ppo_parser.add_argument("--batch-size", type=int, default=4,
                          help="Batch size for PPO")
    ppo_parser.add_argument("--mini-batch-size", type=int, default=2,
                          help="Mini-batch size for PPO")
    ppo_parser.add_argument("--ppo-steps", type=int, default=100,
                          help="Number of PPO training steps")
    ppo_parser.add_argument("--ppo-learning-rate", type=float, default=1e-5,
                          help="Learning rate for PPO")
    
    args = parser.parse_args()
    
    if args.command == "reward":
        train_reward_model(args)
    elif args.command == "ppo":
        train_ppo(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 