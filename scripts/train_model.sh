#!/bin/bash

# RLHF Training Script for Climate Economy Ecosystem
# 
# This script trains the reward model based on human feedback data
# and then fine-tunes the language model with reinforcement learning.
#
# Usage:
#   ./scripts/train_model.sh [reward|ppo|both]
#     - reward: Train only the reward model
#     - ppo: Train only the policy model with PPO (requires existing reward model)
#     - both: Train both reward model and policy (default)

cd "$(dirname "$0")/.."
echo "Working directory: $(pwd)"

# Create data directories if they don't exist
mkdir -p data/reward_model
mkdir -p data/rlhf_model

# Set default mode
MODE=${1:-both}

# Check Python and dependencies
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Check for required packages
required_packages=("torch" "transformers" "trl" "pandas" "numpy" "tqdm")
missing_packages=()

for package in "${required_packages[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -ne 0 ]; then
    echo "Missing required packages: ${missing_packages[*]}"
    echo "Installing missing packages..."
    python3 -m pip install ${missing_packages[*]}
fi

# Train reward model
if [ "$MODE" = "reward" ] || [ "$MODE" = "both" ]; then
    echo "=== Training reward model ==="
    python3 tools/train_rlhf.py reward --epochs 5 --batch-size 16 --reward-base-model distilroberta-base
fi

# Train policy with PPO
if [ "$MODE" = "ppo" ] || [ "$MODE" = "both" ]; then
    echo "=== Training language model with PPO ==="
    
    # Use a smaller model for demonstration purposes
    # In production, you would use a larger model or your fine-tuned model
    BASE_MODEL="gpt2"  # Small model for testing
    
    python3 tools/train_rlhf.py ppo --base-model $BASE_MODEL --ppo-steps 100 --batch-size 4
fi

echo "=== Training complete ==="
echo "Model artifacts are stored in data/reward_model and data/rlhf_model" 