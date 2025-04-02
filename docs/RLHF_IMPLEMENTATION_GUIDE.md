# RLHF Implementation Guide

This guide provides step-by-step instructions for implementing and extending the Reinforcement Learning from Human Feedback (RLHF) system in the Climate Economy Ecosystem.

## Prerequisites

- Python 3.8+ with PyTorch and Transformers
- Node.js 16+ for frontend components
- Supabase account and project set up
- Familiarity with React, Next.js, and machine learning concepts

## Implementation Steps

### 1. Database Setup

Execute the following SQL in your Supabase project:

```sql
-- Create reasoning steps table for tracking LLM reasoning
CREATE TABLE public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES public.chats(id),
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Add feedback columns to existing chat_feedback table
ALTER TABLE public.chat_feedback
ADD COLUMN step_id UUID REFERENCES public.reasoning_steps(id),
ADD COLUMN feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
ADD COLUMN feedback_type VARCHAR(50);

-- Create table for RLHF training runs
CREATE TABLE public.rlhf_training_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_type VARCHAR(50) NOT NULL, -- 'reward' or 'policy'
    training_status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    end_time TIMESTAMP WITH TIME ZONE,
    metrics JSONB,
    model_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

### 2. Machine Learning Components

#### 2.1 Reward Model

Create the file `lib/ml/reward_model.py`:

```python
import os
import torch
import pandas as pd
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from datasets import Dataset

class ClimateRewardModel:
    def __init__(self, model_name="distilbert-base-uncased", model_path=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if model_path and os.path.exists(model_path):
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        else:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, 
                num_labels=1  # Regression task for reward score
            )
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def compute_reward(self, query, response):
        """Predict reward score for a query-response pair"""
        inputs = self.tokenizer(
            query, response, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            reward = outputs.logits.item()
        
        return reward
    
    def batch_compute_rewards(self, queries, responses):
        """Compute rewards for multiple query-response pairs"""
        rewards = []
        for query, response in zip(queries, responses):
            reward = self.compute_reward(query, response)
            rewards.append(reward)
        return rewards
    
    def train(self, feedback_data, output_dir="data/reward_model", epochs=3):
        """Train the reward model on human feedback data
        
        Args:
            feedback_data: DataFrame with columns [query, response, feedback_score]
            output_dir: Directory to save the trained model
            epochs: Number of training epochs
        """
        # Prepare dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples["query"], 
                examples["response"], 
                truncation=True, 
                padding="max_length", 
                max_length=512
            )
        
        # Normalize feedback scores to [0, 1] range
        feedback_data["normalized_score"] = (feedback_data["feedback_score"] - 1) / 4
        
        # Split into train and validation sets
        train_df, val_df = train_test_split(feedback_data, test_size=0.2, random_state=42)
        
        # Convert to datasets
        train_dataset = Dataset.from_pandas(train_df)
        val_dataset = Dataset.from_pandas(val_df)
        
        # Tokenize datasets
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        val_dataset = val_dataset.map(tokenize_function, batched=True)
        
        # Set up training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
        )
        
        # Define compute metrics function
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = predictions.flatten()
            mse = np.mean((predictions - labels) ** 2)
            return {"mse": mse}
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
        )
        
        # Train model
        trainer.train()
        
        # Save best model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        return trainer.evaluate()
    
    def validate(self, test_data):
        """Validate the reward model on test data"""
        queries = test_data["query"].tolist()
        responses = test_data["response"].tolist()
        true_scores = test_data["feedback_score"].tolist()
        
        # Normalize true scores to [0, 1]
        true_scores_norm = [(score - 1) / 4 for score in true_scores]
        
        predicted_scores = self.batch_compute_rewards(queries, responses)
        
        # Calculate MSE
        mse = np.mean([(pred - true) ** 2 for pred, true in zip(predicted_scores, true_scores_norm)])
        
        return {
            "mse": mse,
            "predictions": predicted_scores,
            "true_scores": true_scores
        }
```

#### 2.2 Feedback Processor

Create the file `lib/ml/feedback_processor.py`:

```python
import pandas as pd
import numpy as np
from supabase import create_client
import os
from sklearn.model_selection import train_test_split

class FeedbackProcessor:
    def __init__(self, supabase_url, supabase_key):
        self.supabase = create_client(supabase_url, supabase_key)
    
    def load_feedback_data(self):
        """Load feedback data from Supabase"""
        # Load message-level feedback
        message_feedback = self.supabase.table("chat_feedback") \
            .select("*, messages(content, role, chat_id, chats(query))") \
            .is_("step_id", "NULL") \
            .execute()
        
        # Load step-level feedback
        step_feedback = self.supabase.table("chat_feedback") \
            .select("*, reasoning_steps(step_content, chat_id, reasoning_steps(chats(query)))") \
            .not_.is_("step_id", "NULL") \
            .execute()
        
        # Process message-level feedback
        message_data = []
        for item in message_feedback.data:
            if item["messages"] and item["feedback"] is not None:
                query = item["messages"]["chats"]["query"] if item["messages"]["chats"] else ""
                response = item["messages"]["content"] if item["messages"]["role"] == "assistant" else ""
                
                if query and response:
                    feedback_score = item["feedback_score"] if item["feedback_score"] else \
                                    (5 if item["feedback"] == "positive" else 1)
                    
                    message_data.append({
                        "query": query,
                        "response": response,
                        "feedback_score": feedback_score,
                        "feedback_type": "message",
                        "id": item["id"]
                    })
        
        # Process step-level feedback
        step_data = []
        for item in step_feedback.data:
            if item["reasoning_steps"] and item["feedback"] is not None:
                query = item["reasoning_steps"]["chats"]["query"] if item["reasoning_steps"]["chats"] else ""
                response = item["reasoning_steps"]["step_content"] if item["reasoning_steps"] else ""
                
                if query and response:
                    feedback_score = item["feedback_score"] if item["feedback_score"] else \
                                    (5 if item["feedback"] == "positive" else 1)
                    
                    step_data.append({
                        "query": query,
                        "response": response,
                        "feedback_score": feedback_score,
                        "feedback_type": "step",
                        "id": item["id"]
                    })
        
        # Combine datasets
        all_data = pd.DataFrame(message_data + step_data)
        return all_data
    
    def preprocess_data(self, data):
        """Preprocess feedback data for training"""
        # Drop duplicates
        data = data.drop_duplicates(subset=["query", "response"])
        
        # Filter out very short responses
        data = data[data["response"].str.len() > 10]
        
        # Ensure feedback_score is numeric
        data["feedback_score"] = pd.to_numeric(data["feedback_score"])
        
        # Handle missing scores
        data = data.dropna(subset=["feedback_score"])
        
        return data
    
    def prepare_training_data(self):
        """Prepare data for training reward model"""
        raw_data = self.load_feedback_data()
        processed_data = self.preprocess_data(raw_data)
        
        # Split into train/validation/test
        train_data, test_data = train_test_split(processed_data, test_size=0.2, random_state=42)
        
        return {
            "train": train_data,
            "test": test_data,
            "all": processed_data
        }
    
    def save_datasets(self, data_dict, output_dir="data/feedback"):
        """Save datasets to disk"""
        os.makedirs(output_dir, exist_ok=True)
        
        for name, dataset in data_dict.items():
            dataset.to_csv(f"{output_dir}/{name}.csv", index=False)
        
        return {k: v.shape[0] for k, v in data_dict.items()}
```

#### 2.3 RLHF Training Script

Create the file `tools/train_rlhf.py`:

```python
#!/usr/bin/env python3
import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.ml.reward_model import ClimateRewardModel
from lib.ml.feedback_processor import FeedbackProcessor
from supabase import create_client

def train_reward_model(args):
    """Train the reward model on human feedback data"""
    print("Starting reward model training...")
    
    # Initialize Supabase client
    supabase = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_SERVICE_KEY")
    )
    
    # Create data directories
    os.makedirs("data/feedback", exist_ok=True)
    os.makedirs("data/reward_model", exist_ok=True)
    
    # Process feedback data
    processor = FeedbackProcessor(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_SERVICE_KEY")
    )
    
    # Prepare training data
    print("Preparing training data...")
    data = processor.prepare_training_data()
    stats = processor.save_datasets(data)
    print(f"Dataset statistics: {stats}")
    
    # Check if we have enough data
    if stats["train"] < 100:
        print("Warning: Training dataset is small (<100 samples). Results may not be optimal.")
    
    # Record training run in database
    training_run = supabase.table("rlhf_training_runs").insert({
        "model_type": "reward",
        "training_status": "started",
        "metrics": json.dumps({"dataset_stats": stats})
    }).execute()
    
    run_id = training_run.data[0]["id"] if training_run.data else None
    
    try:
        # Initialize and train reward model
        print("Initializing reward model...")
        model = ClimateRewardModel(
            model_name=args.base_model, 
            model_path=args.model_path
        )
        
        # Train model
        print(f"Training reward model for {args.epochs} epochs...")
        train_metrics = model.train(
            data["train"], 
            output_dir="data/reward_model",
            epochs=args.epochs
        )
        
        # Validate model
        print("Validating reward model...")
        val_metrics = model.validate(data["test"])
        
        # Update training run status
        metrics = {
            "dataset_stats": stats,
            "training_metrics": train_metrics,
            "validation_metrics": {"mse": val_metrics["mse"]}
        }
        
        supabase.table("rlhf_training_runs").update({
            "training_status": "completed",
            "end_time": datetime.now().isoformat(),
            "metrics": json.dumps(metrics),
            "model_path": "data/reward_model"
        }).eq("id", run_id).execute()
        
        print("Reward model training completed successfully!")
        print(f"Validation MSE: {val_metrics['mse']}")
        
    except Exception as e:
        print(f"Error during reward model training: {str(e)}")
        
        # Update training run status
        supabase.table("rlhf_training_runs").update({
            "training_status": "failed",
            "end_time": datetime.now().isoformat(),
            "metrics": json.dumps({"error": str(e)})
        }).eq("id", run_id).execute()
        
        raise e

def train_ppo(args):
    """Train policy model using PPO"""
    print("Starting PPO training...")
    print("PPO training not yet implemented.")
    # TODO: Implement PPO training using trl library

def main():
    parser = argparse.ArgumentParser(description="RLHF Training Script")
    parser.add_argument(
        "mode", 
        choices=["reward", "ppo", "both"], 
        help="Training mode: reward (train reward model), ppo (fine-tune using PPO), or both"
    )
    parser.add_argument(
        "--base-model", 
        default="distilbert-base-uncased", 
        help="Base model to use for training"
    )
    parser.add_argument(
        "--model-path", 
        default=None, 
        help="Path to existing model to continue training from"
    )
    parser.add_argument(
        "--epochs", 
        type=int, 
        default=3, 
        help="Number of training epochs"
    )
    
    args = parser.parse_args()
    
    # Check for required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    for var in required_vars:
        if not os.environ.get(var):
            print(f"Error: {var} environment variable is required.")
            sys.exit(1)
    
    if args.mode in ["reward", "both"]:
        train_reward_model(args)
    
    if args.mode in ["ppo", "both"]:
        train_ppo(args)

if __name__ == "__main__":
    main()
```

### 3. Frontend Components

#### 3.1 Step Feedback Component

Create the file `components/Chat/StepFeedback.jsx`:

```jsx
import React, { useState } from 'react';
import { ThumbUpIcon, ThumbDownIcon } from '@heroicons/react/solid';

const StepFeedback = ({ stepId, chatId, onFeedbackSubmitted }) => {
  const [feedbackState, setFeedbackState] = useState({
    submitted: false,
    loading: false,
    type: null,
    error: null
  });

  const submitFeedback = async (feedbackType, feedbackScore = null) => {
    if (feedbackState.submitted || feedbackState.loading) return;
    
    setFeedbackState({
      ...feedbackState,
      loading: true,
      error: null
    });

    try {
      const response = await fetch('/api/assistant/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          step_id: stepId,
          chat_id: chatId,
          feedback_type: feedbackType,
          feedback: feedbackType === 'positive' ? 'positive' : 'negative',
          feedback_score: feedbackScore
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }

      setFeedbackState({
        submitted: true,
        loading: false,
        type: feedbackType,
        error: null
      });

      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(feedbackType, stepId);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setFeedbackState({
        ...feedbackState,
        loading: false,
        error: error.message
      });
    }
  };

  if (feedbackState.submitted) {
    return (
      <div className="flex items-center text-xs text-gray-500 mt-1">
        <span className="text-green-600">
          {feedbackState.type === 'positive' ? 'Helpful' : 'Not helpful'} feedback recorded
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 mt-1">
      <div className="text-xs text-gray-500">Was this step helpful?</div>
      <button
        onClick={() => submitFeedback('positive', 5)}
        className={`btn btn-xs btn-circle btn-ghost text-gray-400 hover:text-green-500 ${
          feedbackState.loading ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        disabled={feedbackState.loading}
        aria-label="Thumbs up"
      >
        <ThumbUpIcon className="h-3.5 w-3.5" />
      </button>
      <button
        onClick={() => submitFeedback('negative', 1)}
        className={`btn btn-xs btn-circle btn-ghost text-gray-400 hover:text-red-500 ${
          feedbackState.loading ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        disabled={feedbackState.loading}
        aria-label="Thumbs down"
      >
        <ThumbDownIcon className="h-3.5 w-3.5" />
      </button>
      {feedbackState.error && (
        <div className="text-xs text-red-500">{feedbackState.error}</div>
      )}
    </div>
  );
};

export default StepFeedback;
```

#### 3.2 Stream Response Update

Update the file `components/Chat/StreamingResponse.jsx` to include step-level feedback:

```jsx
// Find where the streaming response renders steps
// Add the StepFeedback component after each reasoning step

import StepFeedback from './StepFeedback';

// Inside your StreamingResponse component where steps are rendered:
{message.content.steps && message.content.steps.map((step, idx) => (
  <div key={`step-${idx}`} className="mb-2 border-l-2 border-gray-200 pl-3">
    <div className="text-sm">{step.content}</div>
    <StepFeedback 
      stepId={step.id}
      chatId={message.chatId}
      onFeedbackSubmitted={(type) => {
        // Optional: track feedback in analytics
        console.log(`Step feedback: ${type} for step ${idx}`);
      }}
    />
  </div>
))}
```

### 4. Backend API Updates

#### 4.1 Create Migration Script

Create a migration script in `migrations/rlhf_tables.sql`:

```sql
-- Migration script for RLHF tables
BEGIN;

-- Check if reasoning_steps table exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'reasoning_steps') THEN
        CREATE TABLE public.reasoning_steps (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            chat_id UUID REFERENCES public.chats(id),
            step_content TEXT NOT NULL,
            step_order INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );
        
        -- Add RLS policies
        ALTER TABLE public.reasoning_steps ENABLE ROW LEVEL SECURITY;
        
        -- Allow authenticated users to select and insert
        CREATE POLICY "Allow authenticated users to select their reasoning steps" 
        ON public.reasoning_steps 
        FOR SELECT 
        TO authenticated 
        USING (EXISTS (
            SELECT 1 FROM public.chats 
            WHERE chats.id = reasoning_steps.chat_id AND chats.user_id = auth.uid()
        ));
        
        CREATE POLICY "Allow authenticated users to create reasoning steps" 
        ON public.reasoning_steps 
        FOR INSERT 
        TO authenticated 
        WITH CHECK (true);
        
        -- Allow service role full access
        CREATE POLICY "Allow service role full access to reasoning steps" 
        ON public.reasoning_steps 
        FOR ALL 
        TO service_role 
        USING (true) 
        WITH CHECK (true);
    END IF;
END $$;

-- Add columns to chat_feedback table if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'chat_feedback' AND column_name = 'step_id') THEN
        ALTER TABLE public.chat_feedback ADD COLUMN step_id UUID REFERENCES public.reasoning_steps(id);
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'chat_feedback' AND column_name = 'feedback_score') THEN
        ALTER TABLE public.chat_feedback ADD COLUMN feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5);
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'chat_feedback' AND column_name = 'feedback_type') THEN
        ALTER TABLE public.chat_feedback ADD COLUMN feedback_type VARCHAR(50);
    END IF;
END $$;

-- Create RLHF training runs table
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'rlhf_training_runs') THEN
        CREATE TABLE public.rlhf_training_runs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            model_type VARCHAR(50) NOT NULL,
            training_status VARCHAR(50) NOT NULL,
            start_time TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
            end_time TIMESTAMP WITH TIME ZONE,
            metrics JSONB,
            model_path TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
        );
        
        -- Add RLS policies
        ALTER TABLE public.rlhf_training_runs ENABLE ROW LEVEL SECURITY;
        
        -- Allow service role full access
        CREATE POLICY "Allow service role full access to rlhf_training_runs" 
        ON public.rlhf_training_runs 
        FOR ALL 
        TO service_role 
        USING (true) 
        WITH CHECK (true);
        
        -- Allow authenticated admins to view
        CREATE POLICY "Allow admins to select rlhf_training_runs" 
        ON public.rlhf_training_runs 
        FOR SELECT 
        TO authenticated 
        USING (EXISTS (
            SELECT 1 FROM public.users 
            WHERE users.id = auth.uid() AND users.role = 'admin'
        ));
    END IF;
END $$;

COMMIT;
```

### 5. Deployment Configuration

#### 5.1 GitHub Workflow

Create the file `.github/workflows/rlhf_training.yml`:

```yaml
name: RLHF Training Pipeline

on:
  schedule:
    # Run weekly on Sunday at 1 AM UTC
    - cron: '0 1 * * 0'
  workflow_dispatch:
    # Allow manual trigger

jobs:
  train_rlhf:
    name: Train RLHF Models
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install torch transformers trl pandas numpy tqdm
      
      - name: Train Reward Model
        run: python tools/train_rlhf.py reward
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
      
      - name: Upload Model Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: reward-model
          path: data/reward_model/
          retention-days: 90
```

### 6. Local Training Script

Create the file `scripts/train_model.sh`:

```bash
#!/bin/bash

# RLHF Training Script
# Usage: ./train_model.sh [reward|ppo|both]
# Default: both (train both reward and policy models)

# Change to project root directory
cd "$(dirname "$0")/.."

# Create necessary directories
mkdir -p data/reward_model
mkdir -p data/rlhf_model

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check for required packages
REQUIRED_PACKAGES=("torch" "transformers" "trl" "pandas" "numpy" "tqdm")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "The following required packages are missing: ${MISSING_PACKAGES[*]}"
    read -p "Would you like to install them now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install "${MISSING_PACKAGES[@]}"
    else
        echo "Cannot proceed without required packages."
        exit 1
    fi
fi

# Check environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables must be set."
    echo "You can set them using:"
    echo "export SUPABASE_URL=your_supabase_url"
    echo "export SUPABASE_SERVICE_KEY=your_service_key"
    exit 1
fi

# Determine training mode
MODE=${1:-both}

if [ "$MODE" = "reward" ] || [ "$MODE" = "both" ]; then
    echo "=== Training Reward Model ==="
    python3 tools/train_rlhf.py reward --epochs 3
    
    if [ $? -ne 0 ]; then
        echo "Error: Reward model training failed."
        exit 1
    fi
    
    echo "Reward model training completed. Model saved to data/reward_model/"
fi

if [ "$MODE" = "ppo" ] || [ "$MODE" = "both" ]; then
    echo "=== Training Policy Model with PPO ==="
    python3 tools/train_rlhf.py ppo --base-model "gpt2"
    
    if [ $? -ne 0 ]; then
        echo "Error: PPO training failed."
        exit 1
    fi
    
    echo "PPO training completed. Model saved to data/rlhf_model/"
fi

echo "=== RLHF Training Complete ==="
echo "Models are stored in the data/ directory"
```

## Integration Guidelines

### 1. Storing Reasoning Steps

When generating responses in your AI service, ensure you're storing the reasoning steps:

```javascript
// In your AI service when processing responses
const storeReasoningSteps = async (chatId, steps) => {
  try {
    for (let i = 0; i < steps.length; i++) {
      await supabase.from('reasoning_steps').insert({
        chat_id: chatId,
        step_content: steps[i].content,
        step_order: i
      });
    }
  } catch (error) {
    console.error('Error storing reasoning steps:', error);
  }
};
```

### 2. Integrating with Existing Metrics

In your metrics service:

```javascript
// In your MetricsService class

trackChatFeedback({ chatId, feedbackData }) {
  const userId = this._getCurrentUser();
  
  const eventData = {
    userId,
    timestamp: new Date().toISOString(),
    eventType: 'chat_feedback',
    eventDetails: {
      chatId,
      feedbackType: feedbackData.feedbackType,
      feedbackScore: feedbackData.feedbackScore,
      stepId: feedbackData.stepId,
      messageId: feedbackData.messageId
    }
  };
  
  console.log('Tracking chat feedback:', eventData);
  
  // Send to server
  try {
    fetch('/api/metrics/chat-feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventData)
    });
  } catch (error) {
    console.error('Error tracking chat feedback:', error);
  }
}
```

### 3. Running Migrations

To apply the database migrations:

```bash
# Connect to your Supabase project
export SUPABASE_URL=your_supabase_url
export SUPABASE_SERVICE_KEY=your_service_key

# Run the SQL migration
psql "$SUPABASE_URL/postgres/psql" -f migrations/rlhf_tables.sql
```

## Monitoring and Maintenance

### 1. Monitoring Training Runs

View training runs in the Supabase dashboard by querying the `rlhf_training_runs` table.

### 2. Model Performance

Monitor model performance by:

1. Tracking average reward scores over time
2. Measuring user satisfaction metrics before and after model updates
3. A/B testing between baseline and RLHF-trained models

### 3. Feedback Quality

Regularly audit feedback data for:

1. Balance between positive and negative feedback
2. Distribution across different user segments
3. Correlation with other satisfaction metrics

## Conclusion

This implementation guide provides a comprehensive approach to integrating RLHF into the Climate Economy Ecosystem. By following these steps, you'll create a robust system for collecting user feedback, training reward models, and fine-tuning language models to better align with user preferences.

For advanced use cases, consider exploring:

1. Multi-objective optimization (balancing helpfulness, accuracy, and safety)
2. Alternative RLHF techniques like Direct Preference Optimization (DPO)
3. Model distillation for improved inference performance

The RLHF system should be maintained and improved over time based on user feedback and evolving requirements. 