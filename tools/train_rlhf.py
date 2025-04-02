#!/usr/bin/env python3
"""
RLHF Training Script for Climate Economy Ecosystem

This script trains the reward model and policy model (PPO) for the 
reinforcement learning from human feedback (RLHF) system.

Usage:
    python train_rlhf.py reward  # Train only the reward model
    python train_rlhf.py ppo     # Train only the policy model
    python train_rlhf.py both    # Train both reward and policy models
"""

import os
import sys
import argparse
import logging
import json
import torch
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments
)
from datasets import Dataset
import supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rlhf_training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
REWARD_MODEL_DIR = os.path.join(os.getcwd(), 'data', 'reward_model')
POLICY_MODEL_DIR = os.path.join(os.getcwd(), 'data', 'rlhf_model')

# Make sure directories exist
os.makedirs(REWARD_MODEL_DIR, exist_ok=True)
os.makedirs(POLICY_MODEL_DIR, exist_ok=True)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

class FeedbackProcessor:
    """Processes chat feedback data for RLHF training"""
    
    def __init__(self):
        """Initialize Supabase client for data retrieval"""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        # Initialize Supabase client
        self.supabase = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def fetch_feedback_data(self):
        """Fetch feedback data from Supabase"""
        logger.info("Fetching feedback data from Supabase...")
        
        # Get feedback data
        response = self.supabase.table("chat_feedback").select(
            "id, message_id, step_id, feedback_type, feedback_score, user_id, feedback_time"
        ).execute()
        
        if not response.data:
            logger.warning("No feedback data found")
            return None
        
        # Convert to DataFrame
        feedback_df = pd.DataFrame(response.data)
        logger.info(f"Retrieved {len(feedback_df)} feedback entries")
        
        # Get chat messages data
        message_ids = feedback_df.message_id.dropna().unique().tolist()
        if message_ids:
            messages_response = self.supabase.table("chat_messages").select(
                "id, content, user_query"
            ).in_("id", message_ids).execute()
            
            messages_df = pd.DataFrame(messages_response.data)
            if not messages_df.empty:
                messages_dict = dict(zip(messages_df.id, zip(messages_df.user_query, messages_df.content)))
            else:
                messages_dict = {}
        else:
            messages_dict = {}
        
        # Get reasoning steps data
        step_ids = feedback_df.step_id.dropna().unique().tolist()
        if step_ids:
            steps_response = self.supabase.table("reasoning_steps").select(
                "id, chat_id, step_content, step_order"
            ).in_("id", step_ids).execute()
            
            steps_df = pd.DataFrame(steps_response.data)
            if not steps_df.empty:
                chat_ids = steps_df.chat_id.unique().tolist()
                
                # Get chat data for user queries
                chats_response = self.supabase.table("chats").select(
                    "id, query"
                ).in_("id", chat_ids).execute()
                
                chats_df = pd.DataFrame(chats_response.data)
                chats_dict = dict(zip(chats_df.id, chats_df.query))
                
                # Map chat queries to steps
                steps_df['user_query'] = steps_df.chat_id.map(lambda x: chats_dict.get(x, ""))
                steps_dict = dict(zip(steps_df.id, zip(steps_df.user_query, steps_df.step_content)))
            else:
                steps_dict = {}
        else:
            steps_dict = {}
        
        # Add query and response to feedback data
        def get_query_response(row):
            if pd.notna(row.message_id) and row.message_id in messages_dict:
                return messages_dict[row.message_id]
            elif pd.notna(row.step_id) and row.step_id in steps_dict:
                return steps_dict[row.step_id]
            return (None, None)
        
        # Add query and response columns
        query_response = feedback_df.apply(get_query_response, axis=1)
        feedback_df['query'] = [qr[0] for qr in query_response]
        feedback_df['response'] = [qr[1] for qr in query_response]
        
        # Convert feedback to scores
        feedback_df['score'] = feedback_df.apply(
            lambda x: x.feedback_score if pd.notna(x.feedback_score) else 
                      (5 if x.feedback_type == 'positive' else 1), 
            axis=1
        )
        
        # Filter out rows without query or response
        complete_df = feedback_df.dropna(subset=['query', 'response']).copy()
        logger.info(f"Processed {len(complete_df)} feedback entries with complete data")
        
        return complete_df
    
    def prepare_training_data(self, test_size=0.2, random_state=42):
        """Prepare training and test datasets"""
        # Fetch and process data
        data_df = self.fetch_feedback_data()
        if data_df is None or len(data_df) < 10:
            logger.error("Insufficient data for training")
            return None, None
        
        # Normalize scores to [0, 1] range
        data_df['normalized_score'] = (data_df['score'] - 1) / 4  # Convert 1-5 to 0-1
        
        # Shuffle data
        data_df = data_df.sample(frac=1, random_state=random_state).reset_index(drop=True)
        
        # Split into train and test
        split_idx = int(len(data_df) * (1 - test_size))
        train_df = data_df.iloc[:split_idx]
        test_df = data_df.iloc[split_idx:]
        
        logger.info(f"Split data into {len(train_df)} training and {len(test_df)} test samples")
        
        return train_df, test_df

class RewardModel:
    """Reward model for Climate Economy assistant responses"""
    
    def __init__(self, 
                 model_name="distilroberta-base", 
                 device=None):
        """Initialize the reward model"""
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # If fine-tuned model exists, load it
        if os.path.exists(os.path.join(REWARD_MODEL_DIR, 'config.json')):
            logger.info(f"Loading existing model from {REWARD_MODEL_DIR}")
            self.model = AutoModelForSequenceClassification.from_pretrained(REWARD_MODEL_DIR)
            self.tokenizer = AutoTokenizer.from_pretrained(REWARD_MODEL_DIR)
        else:
            logger.info(f"Initializing new model: {model_name}")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, 
                num_labels=1  # Scalar reward score
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
        self.model.to(self.device)
        
    def tokenize_data(self, query, response):
        """Tokenize query-response pairs"""
        return self.tokenizer(
            [f"User: {q}\n\nAssistant: {r}" for q, r in zip(query, response)],
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
    
    def train(self, train_df, test_df=None, epochs=3, batch_size=8, learning_rate=2e-5):
        """Train the reward model on human feedback data"""
        logger.info("Preparing datasets for training...")
        
        # Create datasets
        def preprocess_function(examples):
            return self.tokenize_data(examples["query"], examples["response"])
        
        train_dataset = Dataset.from_pandas(train_df[['query', 'response', 'normalized_score']])
        train_dataset = train_dataset.map(
            preprocess_function, 
            batched=True,
            remove_columns=['query', 'response']
        )
        train_dataset.set_format(
            type='torch', 
            columns=['input_ids', 'attention_mask', 'normalized_score'],
            output_all_columns=True
        )
        
        if test_df is not None:
            test_dataset = Dataset.from_pandas(test_df[['query', 'response', 'normalized_score']])
            test_dataset = test_dataset.map(
                preprocess_function, 
                batched=True,
                remove_columns=['query', 'response']
            )
            test_dataset.set_format(
                type='torch', 
                columns=['input_ids', 'attention_mask', 'normalized_score'],
                output_all_columns=True
            )
        else:
            test_dataset = None
        
        # Setup training arguments
        training_args = TrainingArguments(
            output_dir=REWARD_MODEL_DIR,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=0.01,
            evaluation_strategy="epoch" if test_dataset else "no",
            save_strategy="epoch",
            load_best_model_at_end=True if test_dataset else False,
            push_to_hub=False,
            report_to="none",
        )
        
        # Define data collator
        def data_collator(features):
            batch = {
                'input_ids': torch.stack([f['input_ids'] for f in features]),
                'attention_mask': torch.stack([f['attention_mask'] for f in features]),
                'labels': torch.tensor([f['normalized_score'] for f in features], dtype=torch.float)
            }
            return batch
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            data_collator=data_collator,
        )
        
        # Train the model
        logger.info("Starting reward model training...")
        trainer.train()
        
        # Save the model
        logger.info(f"Saving model to {REWARD_MODEL_DIR}")
        trainer.save_model(REWARD_MODEL_DIR)
        self.tokenizer.save_pretrained(REWARD_MODEL_DIR)
        
        # Evaluate on test set
        if test_dataset:
            metrics = trainer.evaluate()
            logger.info(f"Evaluation metrics: {metrics}")
            
            # Save metrics
            with open(os.path.join(REWARD_MODEL_DIR, 'metrics.json'), 'w') as f:
                json.dump(metrics, f)
                
            return metrics
        
        return None

def train_reward_model():
    """Train the reward model"""
    logger.info("Starting reward model training process")
    
    # Initialize processor and model
    processor = FeedbackProcessor()
    train_df, test_df = processor.prepare_training_data()
    
    if train_df is None or len(train_df) < 10:
        logger.error("Insufficient data for training")
        return False
    
    model = RewardModel()
    metrics = model.train(train_df, test_df)
    
    logger.info("Reward model training completed")
    return True

def train_policy_model():
    """Train the policy model using PPO"""
    logger.info("Starting policy model training process")
    
    # Check if reward model exists
    if not os.path.exists(os.path.join(REWARD_MODEL_DIR, 'config.json')):
        logger.error("Reward model not found. Run 'python train_rlhf.py reward' first")
        return False
    
    # TODO: Implement PPO training with TRL library
    logger.info("PPO training not implemented yet")
    
    return True

def main():
    """Main function to parse args and run training"""
    parser = argparse.ArgumentParser(description="Train RLHF models")
    parser.add_argument("mode", choices=["reward", "ppo", "both"], 
                      help="Which model to train: reward, ppo, or both")
    args = parser.parse_args()
    
    # Train models based on mode
    if args.mode in ["reward", "both"]:
        success = train_reward_model()
        if not success and args.mode == "both":
            logger.error("Reward model training failed, skipping policy model training")
            return
    
    if args.mode in ["ppo", "both"]:
        train_policy_model()
    
    logger.info("Training completed")

if __name__ == "__main__":
    main() 