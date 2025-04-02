# RLHF and Interim Output Feedback Implementation Documentation

## Overview

This document outlines the implementation strategy for adding Reinforcement Learning from Human Feedback (RLHF) and interim output rating to the Climate Economy Ecosystem platform. These features will enable continuous model improvement based on user feedback and more granular understanding of user preferences.

## 1. System Architecture

![RLHF System Architecture](https://mermaid.ink/img/pako:eNqVVE1v2zAM_SuETjtgaZcedhkKLN1WoJcOG3YodigsM7aAyHQoKl2C5L-PlJzEdoJlPcQWqUfy8ZGkbpgxCVnKZipTCmr-LM9-lCzKGxd0xoKRBYsS3S7qJcl0KZ4VaINXMfBCsYnhb9B6BTTxTmtCpRPtclzqLCXhA7T63QNXpAU6lURrQDjHo7Q_kFoZrE61u1EJJeQoToBQ1x-3GMQE5B3Hm8dqcbA5SsGJjYA81ER8EvU9OA8jPr8qlAE-L1mJ1hF-2g-yJo5SX8h-yiGdoWbq8BkJFzs0Dq15aB0t2kXd_lBOKOvAkb0q4KiHYtcuXeRBb-ej-rUy9lBLcuA2MnqHLy5a-NUP3NdCPmJoMpjIK6_ckL9SHgxDXnWGwzvlv8cK7Qs_nK_KlSnDYrg2yqFWOAJ3QeXkVXdpotZXWhIGylr0-0jroXsPDR-QHtg7c_6Ql4pNSYs6V1n0zF8qUDNY3pWgMDFdRnGzZRG2lV6zj5c3f9xK0XaS9bvfq7e8FfB-7bK0q-dPHU9HLbVkx3Vj3X0lkpG2hXdOsz2Wj1tL6k5U8YSKUocH3pvDmEtBK3VmC1OU7GN4_PNl_3n_eD_8DTH8uR-A_wFWJHO3)

## 2. Prerequisites

- Python 3.9+
- Node.js 18+
- Access to the Climate Economy Ecosystem codebase
- Supabase database access
- OpenAI API key or equivalent LLM API

## 3. Implementation Steps

### Phase 1: Database Schema Updates

1. Create a new SQL migration file at `climate_economy_ecosystem/supabase/migrations/20240405_rlhf_schema.sql`:

```sql
-- Step tracking table
CREATE TABLE public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES public.chats(id),
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Add step_id to chat_feedback
ALTER TABLE public.chat_feedback
ADD COLUMN step_id UUID REFERENCES public.reasoning_steps(id),
ADD COLUMN feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5);

-- Add indices
CREATE INDEX idx_reasoning_steps_chat_id ON public.reasoning_steps(chat_id);
CREATE INDEX idx_chat_feedback_step_id ON public.chat_feedback(step_id);

-- RLS policies
ALTER TABLE public.reasoning_steps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view steps from their chats"
    ON public.reasoning_steps
    FOR SELECT
    TO authenticated
    USING (chat_id IN (SELECT id FROM public.chats WHERE user_id = auth.uid()));

-- Grant privileges
GRANT SELECT ON public.reasoning_steps TO authenticated;
GRANT INSERT, UPDATE ON public.chat_feedback TO authenticated;
```

2. Run the migration:

```bash
cd climate_economy_ecosystem
npx supabase db push
```

### Phase 2: Implement Reward Model

1. Create a new file at `climate_economy_ecosystem/lib/ml/reward_model.py`:

```python
"""
Reward Model for Climate Economy Ecosystem RLHF

This module provides a reward model that predicts user satisfaction
with LLM responses based on human feedback.
"""

import os
import torch
import numpy as np
from typing import List, Dict, Any, Tuple
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datetime import datetime

class ClimateRewardModel:
    """Reward model for Climate Economy assistant responses"""
    
    def __init__(self, 
                 model_name: str = "distilroberta-base", 
                 device: str = None):
        """
        Initialize the reward model.
        
        Args:
            model_name: Base model to use (will be fine-tuned)
            device: Device to run inference on ('cuda', 'cpu', etc.)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_dir = os.path.join(os.getcwd(), 'data', 'reward_model')
        
        # If fine-tuned model exists, load it
        if os.path.exists(os.path.join(self.model_dir, 'config.json')):
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        else:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, 
                num_labels=1  # Scalar reward score
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
        self.model.to(self.device)
        
    def compute_reward(self, 
                       query: str, 
                       response: str, 
                       include_metadata: bool = False) -> float:
        """
        Compute reward score for a query-response pair.
        
        Args:
            query: User query
            response: Model response
            include_metadata: Whether to return prediction metadata
            
        Returns:
            Float reward score (or dict with score and metadata)
        """
        # Format input
        input_text = f"User: {query}\n\nAssistant: {response}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            reward = outputs.logits.item()
        
        if include_metadata:
            return {
                "score": reward,
                "timestamp": datetime.now().isoformat(),
                "model_version": getattr(self.model, "_name_or_path", "unknown")
            }
        return reward
        
    def compute_batch_rewards(self, 
                              pairs: List[Dict[str, str]]) -> List[float]:
        """
        Compute rewards for a batch of query-response pairs.
        
        Args:
            pairs: List of dicts with 'query' and 'response' keys
            
        Returns:
            List of reward scores
        """
        input_texts = [
            f"User: {pair['query']}\n\nAssistant: {pair['response']}"
            for pair in pairs
        ]
        
        inputs = self.tokenizer(
            input_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            rewards = outputs.logits.squeeze().cpu().tolist()
            
        # Handle single-item batch
        if not isinstance(rewards, list):
            rewards = [rewards]
            
        return rewards
    
    def train(self, 
              train_data: List[Dict[str, Any]], 
              validation_data: List[Dict[str, Any]] = None,
              batch_size: int = 8,
              epochs: int = 3,
              learning_rate: float = 2e-5) -> Dict[str, List[float]]:
        """
        Train the reward model on human feedback data.
        
        Args:
            train_data: List of training examples with 'query', 'response', and 'score' keys
            validation_data: Optional validation dataset
            batch_size: Training batch size
            epochs: Number of training epochs
            learning_rate: Learning rate for optimization
            
        Returns:
            Dict with training metrics
        """
        # Prepare optimizer
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        self.model.train()
        train_losses = []
        val_losses = []
        
        for epoch in range(epochs):
            # Shuffle training data
            np.random.shuffle(train_data)
            
            # Process in batches
            epoch_loss = 0
            for i in range(0, len(train_data), batch_size):
                batch = train_data[i:i+batch_size]
                
                # Prepare inputs
                input_texts = [
                    f"User: {item['query']}\n\nAssistant: {item['response']}"
                    for item in batch
                ]
                scores = torch.tensor(
                    [item['score'] for item in batch], 
                    dtype=torch.float
                ).to(self.device)
                
                # Tokenize
                inputs = self.tokenizer(
                    input_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                ).to(self.device)
                
                # Forward pass
                outputs = self.model(**inputs)
                logits = outputs.logits.squeeze()
                
                # Calculate MSE loss
                loss = torch.nn.functional.mse_loss(logits, scores)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
            
            # Record epoch loss
            avg_epoch_loss = epoch_loss / (len(train_data) / batch_size)
            train_losses.append(avg_epoch_loss)
            
            # Validation if provided
            if validation_data:
                val_loss = self._validate(validation_data, batch_size)
                val_losses.append(val_loss)
                print(f"Epoch {epoch+1}/{epochs}: Train Loss = {avg_epoch_loss:.4f}, Val Loss = {val_loss:.4f}")
            else:
                print(f"Epoch {epoch+1}/{epochs}: Train Loss = {avg_epoch_loss:.4f}")
        
        # Save the fine-tuned model
        os.makedirs(self.model_dir, exist_ok=True)
        self.model.save_pretrained(self.model_dir)
        self.tokenizer.save_pretrained(self.model_dir)
        
        return {
            "train_losses": train_losses,
            "val_losses": val_losses
        }
    
    def _validate(self, validation_data: List[Dict[str, Any]], batch_size: int) -> float:
        """Calculate validation loss"""
        self.model.eval()
        val_loss = 0
        
        with torch.no_grad():
            for i in range(0, len(validation_data), batch_size):
                batch = validation_data[i:i+batch_size]
                
                # Prepare inputs
                input_texts = [
                    f"User: {item['query']}\n\nAssistant: {item['response']}"
                    for item in batch
                ]
                scores = torch.tensor(
                    [item['score'] for item in batch], 
                    dtype=torch.float
                ).to(self.device)
                
                # Tokenize
                inputs = self.tokenizer(
                    input_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                ).to(self.device)
                
                # Forward pass
                outputs = self.model(**inputs)
                logits = outputs.logits.squeeze()
                
                # Calculate loss
                loss = torch.nn.functional.mse_loss(logits, scores)
                val_loss += loss.item()
        
        self.model.train()
        return val_loss / (len(validation_data) / batch_size)
```

### Phase 3: Implement Feedback Processing

1. Create a data preparation script at `climate_economy_ecosystem/lib/ml/feedback_processor.py`:

```python
"""
Feedback Processor for RLHF Training

Prepares Supabase feedback data for reward model training.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class FeedbackProcessor:
    """Process and prepare feedback data for RLHF training"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize feedback processor.
        
        Args:
            data_dir: Directory to store processed datasets
        """
        self.data_dir = data_dir or os.path.join(os.getcwd(), 'data', 'rlhf')
        os.makedirs(self.data_dir, exist_ok=True)
        
    def fetch_feedback_data(self, 
                           days_back: int = 30) -> pd.DataFrame:
        """
        Fetch recent feedback data from Supabase.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            DataFrame with feedback data
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # First fetch feedback with scores (1-5 scale)
        response = supabase.table('chat_feedback') \
            .select('*, chats(query, response)') \
            .gte('created_at', cutoff_date) \
            .execute()
            
        feedback_data = response.data
        
        # Convert to DataFrame
        data = []
        for item in feedback_data:
            # Skip items without chat data
            if not item.get('chats') or not item['chats'].get('query'):
                continue
                
            # Convert feedback_type to numerical score if needed
            score = item.get('feedback_score')
            if not score and item.get('feedback_type'):
                # Convert string feedback to numerical
                if item['feedback_type'] == 'positive':
                    score = 5  # Positive feedback gets highest score
                elif item['feedback_type'] == 'negative':
                    score = 1  # Negative feedback gets lowest score
                else:
                    score = 3  # Neutral feedback
            
            data.append({
                'query': item['chats']['query'],
                'response': item['chats']['response'],
                'score': score,
                'user_id': item['user_id'],
                'created_at': item['created_at'],
                'message_id': item['message_id'],
                'step_id': item.get('step_id')
            })
            
        return pd.DataFrame(data)
    
    def prepare_training_data(self, 
                             test_split: float = 0.2,
                             save: bool = True) -> Tuple[List[Dict], List[Dict]]:
        """
        Prepare training and testing datasets.
        
        Args:
            test_split: Fraction of data to use for testing
            save: Whether to save datasets to disk
            
        Returns:
            Tuple of (training_data, testing_data)
        """
        # Fetch feedback data
        df = self.fetch_feedback_data()
        
        # Filter out rows without scores
        df = df.dropna(subset=['score'])
        
        if len(df) == 0:
            raise ValueError("No feedback data available for training")
            
        # Convert to list of dicts
        records = df.to_dict('records')
        
        # Shuffle data
        np.random.shuffle(records)
        
        # Split into train and test
        split_idx = int(len(records) * (1 - test_split))
        train_data = records[:split_idx]
        test_data = records[split_idx:]
        
        if save:
            # Save to disk
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            train_file = os.path.join(self.data_dir, f'train_data_{timestamp}.json')
            test_file = os.path.join(self.data_dir, f'test_data_{timestamp}.json')
            
            with open(train_file, 'w') as f:
                json.dump(train_data, f)
                
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
                
            print(f"Saved training data to {train_file}")
            print(f"Saved testing data to {test_file}")
        
        return train_data, test_data
```

### Phase 4: Implement RLHF Training Pipeline

1. Create a training script at `climate_economy_ecosystem/tools/train_rlhf.py`:

```python
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
```

### Phase 5: Implement Step-Level Feedback UI

1. Create a React component for step-level feedback at `climate_economy_ecosystem/components/Chat/StepFeedback.jsx`:

```jsx
'use client';

import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';

/**
 * StepFeedback Component
 * 
 * Allows users to provide feedback on individual reasoning steps
 * in AI responses.
 */
export default function StepFeedback({ stepId, chatId }) {
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  const submitFeedback = async (isPositive) => {
    if (feedbackGiven || !stepId) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch('/api/assistant/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          step_id: stepId,
          chat_id: chatId,
          feedback_type: isPositive ? 'positive' : 'negative',
          feedback_score: isPositive ? 5 : 1
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      setFeedbackGiven(true);
    } catch (err) {
      console.error('Error submitting feedback:', err);
      setError('Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (feedbackGiven) {
    return (
      <div className="step-feedback-confirmation text-xs text-gray-500 italic mt-1">
        Thanks for your feedback!
      </div>
    );
  }
  
  return (
    <div className="step-feedback flex items-center gap-2 mt-1">
      <button
        onClick={() => submitFeedback(true)}
        disabled={isSubmitting}
        className="text-gray-500 hover:text-green-500 transition-colors"
        aria-label="Thumbs up"
      >
        <ThumbsUp size={14} />
      </button>
      
      <button
        onClick={() => submitFeedback(false)}
        disabled={isSubmitting}
        className="text-gray-500 hover:text-red-500 transition-colors"
        aria-label="Thumbs down"
      >
        <ThumbsDown size={14} />
      </button>
      
      {error && (
        <span className="text-xs text-red-500">{error}</span>
      )}
      
      {isSubmitting && (
        <span className="loading loading-spinner loading-xs"></span>
      )}
    </div>
  );
}
```

2. Modify the `StreamingResponse.jsx` component to include step feedback:

```jsx
// In components/Chat/StreamingResponse.jsx

import React, { useState, useEffect, useRef } from 'react';
import { useSession } from 'next-auth/react';
import { Spinner } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import StepFeedback from './StepFeedback';

// Add handling for step metadata
const processStepMetadata = (chunk) => {
  try {
    const data = JSON.parse(chunk);
    if (data.type === 'step_start' || data.type === 'step_end') {
      return {
        isStepMetadata: true,
        data
      };
    }
  } catch (e) {
    // Not JSON or not step metadata
  }
  return { isStepMetadata: false };
};

// Add rendering for steps with feedback UI
const ReasoningStep = ({ content, stepId, chatId }) => {
  return (
    <div className="reasoning-step border-l-2 border-gray-200 pl-2 my-2 relative">
      <div className="step-content prose prose-sm max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content}
        </ReactMarkdown>
      </div>
      <StepFeedback stepId={stepId} chatId={chatId} />
    </div>
  );
};
```

## 4. Usage Examples

### Training the Reward Model

```bash
cd climate_economy_ecosystem
python tools/train_rlhf.py reward --epochs 5 --batch-size 16
```

### Fine-tuning with PPO

```bash
cd climate_economy_ecosystem
python tools/train_rlhf.py ppo --base-model gpt-neo-1.3B --ppo-steps 200
```

### Viewing Feedback in Admin Dashboard

Navigate to `/admin/metrics` in the application to view aggregated feedback metrics, including:

- Overall feedback scores
- Step-level feedback distribution
- Model improvement trends
- Most problematic reasoning steps

## 5. Integration with Existing Codebase

1. Add the feedback context to the chat metrics:

```javascript
// In lib/monitoring/metrics_service.js

async trackChatFeedback(chatId, feedbackData) {
  try {
    const userId = await this.getCurrentUserId();
    if (!userId) return;
    
    const eventData = {
      userId,
      timestamp: new Date().toISOString(),
      eventType: 'chat_feedback',
      eventDetails: {
        chatId,
        ...feedbackData
      }
    };
    
    // Log client-side metrics
    this._logClientEvent(eventData);
    
    // Send to server
    await this._sendToServer('/api/metrics/chat-feedback', {
      userId,
      chatId,
      feedbackData
    });
    
  } catch (error) {
    console.error('Error tracking chat feedback:', error);
  }
}
```

2. Update the deployment pipeline to periodically retrain the model:

```yaml
# In .github/workflows/rlhf_training.yml

name: RLHF Training Pipeline

on:
  schedule:
    # Run weekly on Sunday at 1 AM UTC
    - cron: '0 1 * * 0'
  workflow_dispatch:
    # Allow manual triggering

jobs:
  train_reward_model:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Train reward model
        run: |
          python tools/train_rlhf.py reward
      - name: Upload model artifacts
        uses: actions/upload-artifact@v3
        with:
          name: reward-model
          path: data/reward_model/
```

## 6. Best Practices for RLHF Implementation

1. **Data Quality**: Regularly audit feedback data to ensure it's representative and unbiased.

2. **Monitoring**: Track reward model performance over time to detect drift or degradation.

3. **Roll-out Strategy**: Use canary deployments for new RLHF-trained models:
   - Deploy to 5% of users first
   - Monitor quality metrics
   - Gradually increase to 100% if successful

4. **Feedback Collection Tips**:
   - Keep feedback UI minimal and non-intrusive
   - Collect both explicit (ratings) and implicit (engagement) feedback
   - Use targeted prompts for feedback on specific aspects

5. **Privacy Considerations**:
   - Anonymize user data in training datasets
   - Get explicit consent for using feedback data
   - Allow users to delete their feedback history

## 7. Conclusion

This implementation provides a comprehensive RLHF system with step-level feedback for the Climate Economy Ecosystem. By continuously learning from user interactions, the system will improve over time, providing more relevant and helpful responses for users seeking clean energy opportunities in Massachusetts.
