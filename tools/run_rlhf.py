#!/usr/bin/env python3
"""
RLHF Training Script for Climate Economy Ecosystem

This script runs the RLHF training process for the Climate Economy Ecosystem.
It can train reward models, policy models, or both for specific agent types or all agents.

Usage:
    python run_rlhf.py --agent-type climate_education  # Train a specific agent
    python run_rlhf.py --all-agents                   # Train all agents
    python run_rlhf.py --evaluate                     # Evaluate agents
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime
import torch
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RLHF components
from lib.rlhf.orchestrator import RLHFOrchestrator, RLHFConfig
from lib.rlhf.models import RewardModelFactory
from lib.rlhf.training import PolicyModel

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

def load_config() -> RLHFConfig:
    """
    Load RLHF configuration.
    
    Returns:
        RLHFConfig instance
    """
    # Check if config file exists
    config_path = os.path.join(os.getcwd(), 'config', 'rlhf_config.json')
    
    if os.path.exists(config_path):
        # Load config from file
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Create config
        return RLHFConfig(**config_data)
    else:
        # Use default config
        return RLHFConfig(
            supabase_url=os.environ.get('SUPABASE_URL', ''),
            supabase_key=os.environ.get('SUPABASE_SERVICE_KEY', '')
        )

def generate_test_data(agent_type: str, num_samples: int = 10) -> List[Dict[str, Any]]:
    """
    Generate test data for evaluating agents.
    
    Args:
        agent_type: Type of agent
        num_samples: Number of test samples
        
    Returns:
        List of test samples
    """
    # Define test queries based on agent type
    if agent_type == "climate_education":
        queries = [
            "What are the main causes of climate change?",
            "How does renewable energy work?",
            "What is carbon capture technology?",
            "How do electric vehicles reduce emissions?",
            "What is the Paris Agreement?",
            "How does climate change affect biodiversity?",
            "What are green jobs?",
            "How can I reduce my carbon footprint?",
            "What is sustainable agriculture?",
            "How do solar panels work?"
        ]
    elif agent_type == "job_matching":
        queries = [
            "I'm looking for a job in renewable energy",
            "What skills do I need for a career in sustainability?",
            "Are there any entry-level positions in clean energy?",
            "I have experience in construction, how can I transition to green building?",
            "What certifications are valuable for climate tech jobs?",
            "What companies in Massachusetts are hiring for climate roles?",
            "I'm a software developer interested in climate tech",
            "What are the salary ranges for renewable energy jobs?",
            "I'm a recent graduate with an environmental science degree",
            "What are the growth areas in climate jobs?"
        ]
    elif agent_type == "policy_analysis":
        queries = [
            "What are Massachusetts' climate policies?",
            "How does the Inflation Reduction Act impact clean energy?",
            "What incentives exist for renewable energy in Massachusetts?",
            "How are environmental justice communities supported by policy?",
            "What are the targets for emissions reduction in Massachusetts?",
            "How do building codes address climate change?",
            "What transportation policies reduce emissions?",
            "How does Massachusetts support clean energy workforce development?",
            "What are the key climate regulations for businesses?",
            "How do federal and state climate policies interact?"
        ]
    else:
        # Generic queries
        queries = [
            "Tell me about climate change",
            "How can I get involved in climate action?",
            "What are the best climate solutions?",
            "How is Massachusetts addressing climate change?",
            "What are the economic benefits of clean energy?",
            "How does climate change affect Massachusetts?",
            "What are the latest innovations in climate tech?",
            "How can businesses reduce their carbon footprint?",
            "What resources are available for climate education?",
            "How can communities prepare for climate impacts?"
        ]
    
    # Ensure we have enough queries
    queries = (queries * (num_samples // len(queries) + 1))[:num_samples]
    
    # Create test data
    return [{'query': query} for query in queries]

def main():
    """Main function to parse args and run RLHF training"""
    parser = argparse.ArgumentParser(description="Run RLHF training for Climate Economy Ecosystem")
    
    # Agent selection
    agent_group = parser.add_mutually_exclusive_group()
    agent_group.add_argument("--agent-type", type=str, help="Type of agent to train")
    agent_group.add_argument("--all-agents", action="store_true", help="Train all agents")
    
    # Evaluation
    parser.add_argument("--evaluate", action="store_true", help="Evaluate agents")
    parser.add_argument("--num-eval-samples", type=int, default=10, help="Number of evaluation samples")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Create orchestrator
    orchestrator = RLHFOrchestrator(config)
    
    # Run training or evaluation
    if args.evaluate:
        # Generate test data
        test_data = {}
        
        if args.agent_type:
            # Generate test data for specific agent
            test_data[args.agent_type] = generate_test_data(args.agent_type, args.num_eval_samples)
            
            # Evaluate agent
            results = orchestrator.evaluate_agent(args.agent_type, test_data[args.agent_type])
            logger.info(f"Evaluation results for {args.agent_type}: {results}")
        else:
            # Generate test data for all agents
            for agent_type in config.agent_types:
                test_data[agent_type] = generate_test_data(agent_type, args.num_eval_samples)
            
            # Evaluate all agents
            results = orchestrator.evaluate_all_agents(test_data)
            logger.info(f"Evaluation results: {results}")
            
        # Save evaluation results
        results_dir = os.path.join(os.getcwd(), 'data', 'evaluation_results')
        os.makedirs(results_dir, exist_ok=True)
        
        filename = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Evaluation results saved to {filepath}")
    else:
        # Run training
        if args.agent_type:
            # Train specific agent
            if args.agent_type not in config.agent_types:
                logger.error(f"Unknown agent type: {args.agent_type}")
                sys.exit(1)
                
            logger.info(f"Training agent: {args.agent_type}")
            results = orchestrator.train_agent(args.agent_type)
            logger.info(f"Training results: {results}")
        else:
            # Train all agents
            logger.info("Training all agents")
            results = orchestrator.train_all_agents()
            logger.info(f"Training results: {results}")
            
    logger.info("RLHF process completed")

if __name__ == "__main__":
    main()
