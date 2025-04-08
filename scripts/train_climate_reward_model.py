#!/usr/bin/env python3
"""
Script to train a reward model for the Massachusetts Climate Assistant using feedback data
"""

import os
import asyncio
import logging
import json
import sys
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ClimateRewardModelTrainer:
    """Trainer for the Massachusetts Climate Assistant reward model"""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        model_name: str = "distilroberta-base",
        output_dir: str = "models/climate_reward_model",
        device: str = None
    ):
        """Initialize the reward model trainer"""
        from supabase.client import create_client
        
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.model_name = model_name
        self.output_dir = output_dir
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize Supabase client
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=1  # Regression task
        )
        self.model.to(self.device)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Climate Reward Model Trainer with model: {model_name}")
    
    async def fetch_feedback_data(self):
        """Fetch feedback data from Supabase"""
        logger.info("Fetching feedback data from Supabase...")
        
        # Get all messages with feedback
        feedback_query = """
        SELECT m.id as message_id, m.content as response, m.metadata->>'query' as query, 
               cf.rating, cf.feedback_type, cf.created_at as feedback_time
        FROM messages m
        JOIN chat_feedback cf ON m.id = cf.message_id
        WHERE m.role = 'assistant'
          AND m.metadata->>'query' IS NOT NULL
          AND cf.rating IS NOT NULL
        ORDER BY cf.created_at DESC
        """
        
        feedback_result = await self.supabase.rpc('run_sql', {'query': feedback_query}).execute()
        
        if not feedback_result.data:
            logger.warning("No feedback data found")
            return []
        
        # Convert to DataFrame for easier processing
        feedback_df = pd.DataFrame(feedback_result.data)
        logger.info(f"Fetched {len(feedback_df)} feedback entries")
        
        # Get comparison feedback
        comparison_query = """
        SELECT cf1.message_id as preferred_id, cf2.message_id as rejected_id, 
               cf1.comparison_id, cf1.created_at as feedback_time,
               m1.content as preferred_response, m2.content as rejected_response,
               m1.metadata->>'query' as query
        FROM chat_feedback cf1
        JOIN chat_feedback cf2 ON cf1.comparison_id = cf2.comparison_id
        JOIN messages m1 ON cf1.message_id = m1.id
        JOIN messages m2 ON cf2.message_id = m2.id
        WHERE cf1.feedback_type = 'comparison'
          AND cf2.feedback_type = 'comparison'
          AND cf1.rating > cf2.rating
          AND m1.metadata->>'query' = m2.metadata->>'query'
        """
        
        comparison_result = await self.supabase.rpc('run_sql', {'query': comparison_query}).execute()
        
        comparison_data = []
        if comparison_result.data:
            comparison_df = pd.DataFrame(comparison_result.data)
            logger.info(f"Fetched {len(comparison_df)} comparison pairs")
            
            for _, row in comparison_df.iterrows():
                comparison_data.append({
                    'query': row['query'],
                    'preferred': row['preferred_response'],
                    'rejected': row['rejected_response'],
                    'comparison_id': row['comparison_id']
                })
        
        # Prepare training data
        training_data = []
        
        # Add rating feedback
        for _, row in feedback_df.iterrows():
            if row['feedback_type'] != 'comparison':  # Skip comparison feedback as it's handled separately
                # Normalize rating to 0-1 range
                normalized_rating = row['rating'] / 5.0
                
                training_data.append({
                    'query': row['query'],
                    'response': row['response'],
                    'rating': normalized_rating,
                    'feedback_type': row['feedback_type']
                })
        
        # Add comparison feedback
        for item in comparison_data:
            # Preferred response gets a high rating
            training_data.append({
                'query': item['query'],
                'response': item['preferred'],
                'rating': 1.0,
                'feedback_type': 'comparison_preferred'
            })
            
            # Rejected response gets a low rating
            training_data.append({
                'query': item['query'],
                'response': item['rejected'],
                'rating': 0.0,
                'feedback_type': 'comparison_rejected'
            })
        
        logger.info(f"Prepared {len(training_data)} training examples")
        return training_data
    
    def prepare_dataset(self, data, max_length=512, val_split=0.2):
        """Prepare dataset for training"""
        logger.info("Preparing dataset for training...")
        
        # Shuffle data
        np.random.shuffle(data)
        
        # Split into train and validation
        split_idx = int(len(data) * (1 - val_split))
        train_data = data[:split_idx]
        val_data = data[split_idx:]
        
        logger.info(f"Split data into {len(train_data)} training and {len(val_data)} validation examples")
        
        # Process training data
        train_inputs = []
        train_labels = []
        
        for item in train_data:
            combined = f"Query: {item['query']}\nResponse: {item['response']}"
            train_inputs.append(combined)
            train_labels.append(item['rating'])
        
        # Process validation data
        val_inputs = []
        val_labels = []
        
        for item in val_data:
            combined = f"Query: {item['query']}\nResponse: {item['response']}"
            val_inputs.append(combined)
            val_labels.append(item['rating'])
        
        # Tokenize inputs
        train_encodings = self.tokenizer(
            train_inputs,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        )
        
        val_encodings = self.tokenizer(
            val_inputs,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt"
        )
        
        # Create datasets
        train_dataset = TensorDataset(
            train_encodings["input_ids"],
            train_encodings["attention_mask"],
            torch.tensor(train_labels, dtype=torch.float)
        )
        
        val_dataset = TensorDataset(
            val_encodings["input_ids"],
            val_encodings["attention_mask"],
            torch.tensor(val_labels, dtype=torch.float)
        )
        
        return train_dataset, val_dataset
    
    def train(self, train_dataset, val_dataset, batch_size=8, epochs=3, learning_rate=2e-5):
        """Train the reward model"""
        logger.info(f"Training reward model for {epochs} epochs with batch size {batch_size}...")
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Prepare optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(0.1 * total_steps),
            num_training_steps=total_steps
        )
        
        # Training loop
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0
            train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
            
            for batch in train_pbar:
                batch = tuple(t.to(self.device) for t in batch)
                input_ids, attention_mask, labels = batch
                
                optimizer.zero_grad()
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                loss = F.mse_loss(outputs.logits.squeeze(), labels)
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                
                train_loss += loss.item()
                train_pbar.set_postfix({"loss": f"{loss.item():.4f}"})
            
            avg_train_loss = train_loss / len(train_loader)
            train_losses.append(avg_train_loss)
            logger.info(f"Epoch {epoch+1}/{epochs} - Avg. training loss: {avg_train_loss:.4f}")
            
            # Validation
            self.model.eval()
            val_loss = 0
            val_pbar = tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Val]")
            
            with torch.no_grad():
                for batch in val_pbar:
                    batch = tuple(t.to(self.device) for t in batch)
                    input_ids, attention_mask, labels = batch
                    
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    loss = F.mse_loss(outputs.logits.squeeze(), labels)
                    
                    val_loss += loss.item()
                    val_pbar.set_postfix({"loss": f"{loss.item():.4f}"})
            
            avg_val_loss = val_loss / len(val_loader)
            val_losses.append(avg_val_loss)
            logger.info(f"Epoch {epoch+1}/{epochs} - Validation loss: {avg_val_loss:.4f}")
            
            # Save best model
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                logger.info(f"New best validation loss: {best_val_loss:.4f} - Saving model")
                self.save_model(os.path.join(self.output_dir, "best_model"))
        
        # Save final model
        self.save_model(os.path.join(self.output_dir, "final_model"))
        
        # Plot training curves
        self._plot_training_curves(train_losses, val_losses)
        
        return train_losses, val_losses
    
    def save_model(self, path):
        """Save the model and tokenizer"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save training metadata
        metadata = {
            "model_name": self.model_name,
            "saved_at": datetime.now().isoformat(),
            "device": self.device
        }
        
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to {path}")
    
    def _plot_training_curves(self, train_losses, val_losses):
        """Plot training and validation loss curves"""
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label="Training Loss")
        plt.plot(val_losses, label="Validation Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Training and Validation Loss")
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plot_path = os.path.join(self.output_dir, "training_curves.png")
        plt.savefig(plot_path)
        logger.info(f"Training curves saved to {plot_path}")

async def main():
    """Main function to train the reward model"""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not all([supabase_url, supabase_key]):
        logger.error("Missing required environment variables")
        return
    
    # Initialize trainer
    trainer = ClimateRewardModelTrainer(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        model_name="distilroberta-base",
        output_dir="models/climate_reward_model"
    )
    
    # Fetch feedback data
    data = await trainer.fetch_feedback_data()
    
    if not data:
        logger.error("No feedback data available for training")
        return
    
    # Prepare dataset
    train_dataset, val_dataset = trainer.prepare_dataset(data)
    
    # Train model
    trainer.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        batch_size=8,
        epochs=3,
        learning_rate=2e-5
    )
    
    logger.info("Reward model training complete")

if __name__ == "__main__":
    asyncio.run(main())
