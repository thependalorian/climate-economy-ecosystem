#!/bin/bash
# Script to run RLHF training

# Set environment variables
export PYTHONPATH=$(pwd)

# Check if agent type is provided
if [ "$1" == "" ]; then
    echo "Usage: $0 [agent_type|all] [evaluate]"
    echo "  agent_type: Type of agent to train (climate_education, job_matching, policy_analysis, ej_community)"
    echo "  all: Train all agents"
    echo "  evaluate: Evaluate agents instead of training"
    exit 1
fi

# Check if evaluation flag is provided
if [ "$2" == "evaluate" ]; then
    EVALUATE="--evaluate"
else
    EVALUATE=""
fi

# Run RLHF training
if [ "$1" == "all" ]; then
    echo "Training all agents..."
    python tools/run_rlhf.py --all-agents $EVALUATE
else
    echo "Training agent: $1..."
    python tools/run_rlhf.py --agent-type $1 $EVALUATE
fi
