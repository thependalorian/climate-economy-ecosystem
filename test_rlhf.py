#!/usr/bin/env python3
"""
Test script for RLHF system in Climate Economy Ecosystem

This script tests the RLHF system by:
1. Creating mock feedback data
2. Processing the feedback
3. Training a simple reward model
4. Using the reward model to score responses
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone
import asyncio
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import RLHF components
from climate_economy_ecosystem.tools.train_rlhf import (
    FeedbackProcessor,
    ClimateRewardModel,
    train_reward_model
)

# Create directories if they don't exist
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("models/reward_model", exist_ok=True)

def create_mock_feedback_data():
    """Create mock feedback data for testing"""
    print("\n=== Creating Mock Feedback Data ===")
    
    # Create mock feedback data
    feedback_data = []
    
    # Positive feedback examples
    positive_responses = [
        "I can help you find clean energy job opportunities in Massachusetts. The state has a growing renewable energy sector with jobs in solar installation, energy efficiency, and offshore wind. Would you like me to search for specific roles or provide information about training programs?",
        "Based on your background in electrical engineering, you might be interested in solar PV installation or grid modernization roles. Massachusetts has several companies like Solect Energy and Eversource that hire for these positions. Would you like more information about specific companies or training programs?",
        "As a veteran with experience in logistics, you have valuable skills for the clean energy sector. Companies like Vineyard Wind and Ameresco often look for professionals with your background for supply chain and project management roles. The Mass Clean Energy Center also has resources specifically for veterans."
    ]
    
    # Negative feedback examples
    negative_responses = [
        "I don't have information about clean energy jobs in Massachusetts.",
        "Your background doesn't seem relevant to clean energy careers.",
        "There aren't many opportunities for veterans in the clean energy sector."
    ]
    
    # Create positive feedback examples
    for i, response in enumerate(positive_responses):
        feedback_data.append({
            "id": str(uuid.uuid4()),
            "chat_id": str(uuid.uuid4()),
            "user_id": "test_user",
            "message": response,
            "feedback_type": "rating",
            "feedback_score": 5,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Create negative feedback examples
    for i, response in enumerate(negative_responses):
        feedback_data.append({
            "id": str(uuid.uuid4()),
            "chat_id": str(uuid.uuid4()),
            "user_id": "test_user",
            "message": response,
            "feedback_type": "rating",
            "feedback_score": 1,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Save mock data to file
    with open("data/mock_feedback.json", "w") as f:
        json.dump(feedback_data, f, indent=2)
    
    print(f"Created {len(feedback_data)} mock feedback entries")
    print(f"Saved to data/mock_feedback.json")
    
    return feedback_data

def test_reward_model_scoring():
    """Test the reward model by scoring some responses"""
    print("\n=== Testing Reward Model Scoring ===")
    
    # Initialize reward model
    reward_model = ClimateRewardModel()
    
    # Test queries
    test_queries = [
        "I'm a veteran looking for clean energy jobs in Massachusetts.",
        "What clean energy careers are available for someone with an electrical background?",
        "Are there any training programs for solar installation in Boston?"
    ]
    
    # Test responses (good, medium, poor)
    test_responses = [
        # Good responses
        "As a veteran, you have valuable skills that transfer well to the clean energy sector in Massachusetts. The state has programs specifically for veterans through the Mass Clean Energy Center, including the Clean Energy Careers Training Program. Companies like Vineyard Wind, Solect Energy, and Ameresco actively recruit veterans. Would you like information about specific roles based on your military background?",
        
        # Medium responses
        "There are several clean energy jobs in Massachusetts. You might want to check job boards or the Mass Clean Energy Center website for listings.",
        
        # Poor responses
        "I don't have specific information about clean energy jobs for veterans."
    ]
    
    # Score each query-response pair
    for query in test_queries:
        print(f"\nQuery: {query}")
        for response in test_responses:
            score = reward_model.compute_reward(query, response)
            print(f"Response: {response[:50]}...\nScore: {score:.2f}\n")

async def main():
    """Main function to test RLHF components"""
    print("=== RLHF System Test ===")
    
    # Create mock feedback data
    feedback_data = create_mock_feedback_data()
    
    # Train reward model
    print("\n=== Training Reward Model ===")
    success = train_reward_model()
    
    if success:
        print("Reward model training completed successfully!")
    else:
        print("Reward model training failed. Using default model.")
    
    # Test reward model scoring
    test_reward_model_scoring()

if __name__ == "__main__":
    asyncio.run(main())
