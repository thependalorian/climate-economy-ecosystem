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
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rlhf_training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("rlhf_trainer")

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Get OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model paths
REWARD_MODEL_PATH = os.getenv("REWARD_MODEL_PATH", "models/reward_model")
POLICY_MODEL_PATH = os.getenv("POLICY_MODEL_PATH", "models/policy_model")

class FeedbackProcessor:
    """Processes chat feedback data for RLHF training"""

    def __init__(self):
        """Initialize Supabase client for data retrieval"""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

        # Initialize Supabase client
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Set up logging for database operations
        logger.info("Initialized FeedbackProcessor with Supabase client")

        # Check if required tables exist
        self._check_tables_exist()

    def _check_tables_exist(self):
        """Check if required tables exist in the database"""
        required_tables = ["chat_feedback", "chats", "reasoning_steps", "feedback_metrics"]
        missing_tables = []

        for table in required_tables:
            try:
                # Try to select a single row to check if table exists
                self.supabase.table(table).select("*").limit(1).execute()
                logger.info(f"Table {table} exists")
            except Exception as e:
                logger.warning(f"Table {table} does not exist or error: {str(e)}")
                missing_tables.append(table)

        if missing_tables:
            logger.warning(f"Missing tables: {', '.join(missing_tables)}")
            logger.warning("Some functionality may be limited")

    def fetch_feedback_data(self) -> pd.DataFrame:
        """Fetch feedback data from Supabase"""
        logger.info("Fetching feedback data from Supabase...")

        try:
            # Get feedback data
            response = self.supabase.table("chat_feedback").select(
                "id, chat_id, feedback_type, feedback_score, user_id, created_at"
            ).execute()

            if not response.data:
                logger.warning("No feedback data found")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            logger.info(f"Fetched {len(df)} feedback entries")

            return df
        except Exception as e:
            logger.error(f"Error fetching feedback data: {str(e)}")
            # Return empty DataFrame on error
            return pd.DataFrame()

    def get_message_content(self, chat_ids: List[str]) -> Dict[str, str]:
        """Get message content for the given chat IDs"""
        if not chat_ids:
            logger.warning("No chat IDs provided")
            return {}

        logger.info(f"Fetching content for {len(chat_ids)} chats...")

        try:
            # Get message content
            response = self.supabase.table("chats").select(
                "id, message, role"
            ).in_("id", chat_ids).execute()

            if not response.data:
                logger.warning("No message content found")
                return {}

            # Create chat ID to content mapping
            message_content = {}
            for msg in response.data:
                # Handle different column names (message or content)
                if "message" in msg:
                    message_content[msg["id"]] = msg["message"]
                elif "content" in msg:
                    message_content[msg["id"]] = msg["content"]
                else:
                    logger.warning(f"Message has no content: {msg}")

            logger.info(f"Fetched content for {len(message_content)} messages")

            return message_content
        except Exception as e:
            logger.error(f"Error fetching message content: {str(e)}")
            return {}

    def prepare_training_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Prepare training data for reward model and policy model"""
        # Fetch feedback data
        feedback_df = self.fetch_feedback_data()

        if feedback_df.empty:
            logger.warning("No feedback data available for training")
            return [], []

        # Get unique chat IDs
        chat_ids = feedback_df["chat_id"].unique().tolist()

        # Get message content
        message_content = self.get_message_content(chat_ids)

        if not message_content:
            logger.warning("No message content available for training")
            return [], []

        # Prepare reward model training data
        reward_data = []
        for _, row in feedback_df.iterrows():
            chat_id = row["chat_id"]
            if chat_id in message_content:
                reward_data.append({
                    "chat_id": chat_id,
                    "content": message_content[chat_id],
                    "score": row["feedback_score"],
                    "feedback_type": row["feedback_type"]
                })

        # Prepare policy model training data (pairs of preferred/dispreferred responses)
        policy_data = []
        # Group by user to find pairs of responses with different scores
        for user_id in feedback_df["user_id"].unique():
            user_feedback = feedback_df[feedback_df["user_id"] == user_id]

            # Find high and low scored messages
            high_scored = user_feedback[user_feedback["feedback_score"] >= 4]
            low_scored = user_feedback[user_feedback["feedback_score"] <= 2]

            # Create pairs
            for _, high_row in high_scored.iterrows():
                high_id = high_row["chat_id"]
                if high_id not in message_content:
                    continue

                for _, low_row in low_scored.iterrows():
                    low_id = low_row["chat_id"]
                    if low_id not in message_content:
                        continue

                    policy_data.append({
                        "chosen_id": high_id,
                        "chosen_content": message_content[high_id],
                        "rejected_id": low_id,
                        "rejected_content": message_content[low_id],
                        "score_diff": high_row["feedback_score"] - low_row["feedback_score"]
                    })

        logger.info(f"Prepared {len(reward_data)} samples for reward model training")
        logger.info(f"Prepared {len(policy_data)} pairs for policy model training")

        return reward_data, policy_data

    def save_training_data(self, reward_data: List[Dict[str, Any]], policy_data: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Save training data to files"""
        # Create output directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Generate filenames with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reward_file = f"data/reward_data_{timestamp}.json"
        policy_file = f"data/policy_data_{timestamp}.json"

        # Save reward data
        with open(reward_file, "w") as f:
            json.dump(reward_data, f, indent=2)

        # Save policy data
        with open(policy_file, "w") as f:
            json.dump(policy_data, f, indent=2)

        logger.info(f"Saved reward data to {reward_file}")
        logger.info(f"Saved policy data to {policy_file}")

        return reward_file, policy_file

class ClimateRewardModel:
    """Reward model for climate assistant responses"""

    def __init__(self, model_path: Optional[str] = None, model_name: str = "distilbert-base-uncased"):
        """Initialize the reward model"""
        self.model_path = model_path or REWARD_MODEL_PATH
        self.model = None
        self.tokenizer = None
        self.model_name = model_name

        # Try to load the model if it exists
        try:
            if os.path.exists(self.model_path):
                from transformers import AutoModelForSequenceClassification, AutoTokenizer

                logger.info(f"Loading reward model from {self.model_path}")
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            else:
                logger.warning(f"Reward model not found at {self.model_path}")
                # Initialize with base model
                from transformers import AutoModelForSequenceClassification, AutoTokenizer
                logger.info(f"Initializing new model with {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_name,
                    num_labels=1  # Regression task for reward score
                )
        except Exception as e:
            logger.error(f"Error loading reward model: {str(e)}")

    def compute_reward(self, query: str, response: str) -> float:
        """Compute reward score for a response to a query"""
        if not self.model or not self.tokenizer:
            logger.warning("Reward model not loaded, returning default score")
            return 0.5

        try:
            # Prepare input
            inputs = self.tokenizer(
                f"Query: {query}\nResponse: {response}",
                return_tensors="pt",
                truncation=True,
                max_length=512
            )

            # Compute reward
            with torch.no_grad():
                outputs = self.model(**inputs)
                reward = torch.sigmoid(outputs.logits).item()

            return reward
        except Exception as e:
            logger.error(f"Error computing reward: {str(e)}")
            return 0.5

    def train(self, data_file: str) -> bool:
        """Train the reward model on feedback data"""
        try:
            # Import required libraries
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
                Trainer,
                TrainingArguments,
                DataCollatorWithPadding
            )
            from datasets import Dataset

            # Load data
            with open(data_file, "r") as f:
                data = json.load(f)

            if not data:
                logger.warning("No data available for training")
                return False

            # Prepare dataset
            dataset_dict = {
                "text": [],
                "label": []
            }

            for item in data:
                # Handle different data formats
                if "content" in item:
                    content = item["content"]
                elif "message" in item:
                    content = item["message"]
                else:
                    logger.warning(f"Skipping item with no content: {item}")
                    continue

                if "score" in item:
                    score = item["score"]
                elif "feedback_score" in item:
                    score = item["feedback_score"]
                else:
                    logger.warning(f"Skipping item with no score: {item}")
                    continue

                dataset_dict["text"].append(content)
                dataset_dict["label"].append(float(score) / 5.0)  # Normalize to [0, 1]

            if not dataset_dict["text"]:
                logger.warning("No valid data entries for training")
                return False

            dataset = Dataset.from_dict(dataset_dict)

            # Split dataset
            dataset = dataset.train_test_split(test_size=0.2)

            # Use the model name from initialization
            tokenizer = self.tokenizer or AutoTokenizer.from_pretrained(self.model_name)
            model = self.model or AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=1)

            # Tokenize dataset
            def tokenize_function(examples):
                return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

            tokenized_dataset = dataset.map(tokenize_function, batched=True)

            # Data collator
            data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

            # Create output directory if it doesn't exist
            os.makedirs(self.model_path, exist_ok=True)

            # Training arguments
            training_args = TrainingArguments(
                output_dir=self.model_path,
                learning_rate=5e-5,
                per_device_train_batch_size=8,
                per_device_eval_batch_size=8,
                num_train_epochs=3,
                weight_decay=0.01,
                evaluation_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True,
                logging_dir=os.path.join(self.model_path, "logs"),
                logging_steps=10,
            )

            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset["train"],
                eval_dataset=tokenized_dataset["test"],
                tokenizer=tokenizer,
                data_collator=data_collator,
            )

            # Train model
            logger.info(f"Training reward model on {len(dataset_dict['text'])} examples...")
            trainer.train()

            # Save model
            logger.info(f"Saving reward model to {self.model_path}")
            trainer.save_model(self.model_path)
            tokenizer.save_pretrained(self.model_path)

            # Update model and tokenizer
            self.model = model
            self.tokenizer = tokenizer

            # Log evaluation results
            eval_results = trainer.evaluate()
            logger.info(f"Evaluation results: {eval_results}")

            return True
        except Exception as e:
            logger.error(f"Error training reward model: {str(e)}")
            return False

def train_reward_model() -> bool:
    """Train the reward model"""
    try:
        # Initialize feedback processor
        logger.info("Initializing feedback processor...")
        processor = FeedbackProcessor()

        # Prepare training data
        logger.info("Preparing training data...")
        reward_data, _ = processor.prepare_training_data()

        if not reward_data:
            logger.warning("No reward data available for training")
            return False

        logger.info(f"Collected {len(reward_data)} examples for training")

        # Create output directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        os.makedirs(REWARD_MODEL_PATH, exist_ok=True)

        # Save training data
        logger.info("Saving training data...")
        reward_file, _ = processor.save_training_data(reward_data, [])

        # Initialize reward model
        logger.info("Initializing reward model...")
        reward_model = ClimateRewardModel()

        # Train reward model
        logger.info("Training reward model...")
        success = reward_model.train(reward_file)

        if success:
            logger.info("Reward model training completed successfully!")
        else:
            logger.warning("Reward model training failed")

        return success
    except Exception as e:
        logger.error(f"Error training reward model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def train_policy_model() -> bool:
    """Train the policy model using PPO"""
    try:
        # This is a placeholder for policy model training
        # In a real implementation, this would use a library like TRL (Transformer Reinforcement Learning)
        # to fine-tune a language model with PPO
        logger.info("Policy model training not implemented yet")

        # Here's what a real implementation would do:
        # 1. Initialize feedback processor
        # processor = FeedbackProcessor()
        #
        # 2. Prepare training data (pairs of preferred/dispreferred responses)
        # _, policy_data = processor.prepare_training_data()
        #
        # 3. Initialize reward model for PPO training
        # reward_model = ClimateRewardModel()
        #
        # 4. Initialize PPO trainer
        # from trl import PPOTrainer, PPOConfig
        # from transformers import AutoTokenizer, AutoModelForCausalLM
        #
        # 5. Load base model
        # model_name = "gpt2" # or other suitable base model
        # model = AutoModelForCausalLM.from_pretrained(model_name)
        # tokenizer = AutoTokenizer.from_pretrained(model_name)
        #
        # 6. Configure PPO
        # ppo_config = PPOConfig(
        #     learning_rate=1e-5,
        #     batch_size=8,
        #     mini_batch_size=1,
        # )
        #
        # 7. Initialize PPO trainer
        # ppo_trainer = PPOTrainer(
        #     config=ppo_config,
        #     model=model,
        #     tokenizer=tokenizer,
        #     dataset=policy_data,
        # )
        #
        # 8. Train with PPO
        # for epoch in range(3):
        #     for batch in ppo_trainer.dataloader:
        #         # Generate responses
        #         responses = ppo_trainer.generate(batch["query"])
        #         # Compute rewards
        #         rewards = [reward_model.compute_reward(q, r) for q, r in zip(batch["query"], responses)]
        #         # Run PPO step
        #         stats = ppo_trainer.step(batch["query"], responses, rewards)
        #
        # 9. Save the trained model
        # ppo_trainer.save_pretrained(POLICY_MODEL_PATH)

        logger.info("To implement PPO training, install the TRL library: pip install trl")
        return False
    except Exception as e:
        logger.error(f"Error training policy model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

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