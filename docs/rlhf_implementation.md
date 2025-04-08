# Reinforcement Learning from Human Feedback (RLHF) Implementation

This document provides an overview of the RLHF implementation in the Climate Economy Ecosystem.

## Overview

The RLHF implementation enables the Climate Economy Ecosystem to continuously improve its agents based on human feedback. It consists of the following components:

1. **Feedback Collection**: Collecting feedback from users on agent responses
2. **Reward Modeling**: Training models to predict user satisfaction
3. **Policy Optimization**: Fine-tuning language models using PPO
4. **Continuous Improvement**: Automating the improvement process

## Architecture

The RLHF implementation follows a modular architecture:

```
lib/rlhf/
├── __init__.py        # Module exports
├── models.py          # Reward models
├── training.py        # PPO training
├── pipeline.py        # Continuous improvement
└── orchestrator.py    # Orchestration
```

### Components

#### Reward Models (`models.py`)

The reward models predict user satisfaction with agent responses:

- `BaseRewardModel`: Abstract base class for all reward models
- `ClimateRewardModel`: General reward model for all responses
- `AgentSpecificRewardModel`: Specialized models for different agent types
- `RewardModelFactory`: Factory for creating reward models

#### PPO Training (`training.py`)

The PPO training module implements Proximal Policy Optimization:

- `PolicyModel`: Model for generating responses
- `ValueModel`: Model for estimating expected rewards
- `PPOTrainer`: Implementation of PPO for RLHF

#### Continuous Improvement (`pipeline.py`)

The continuous improvement pipeline automates the improvement process:

- `FeedbackDataset`: Dataset for feedback data
- `FeedbackCollector`: Collects feedback from Supabase
- `ContinuousImprovementPipeline`: Pipeline for continuous model improvement

#### Orchestration (`orchestrator.py`)

The orchestrator coordinates the RLHF process:

- `RLHFConfig`: Configuration for RLHF
- `RLHFOrchestrator`: Orchestrates the RLHF training process

## Database Schema

The RLHF implementation uses the following database tables:

- `chat_feedback`: Stores feedback on chat messages and reasoning steps
- `chat_messages`: Stores chat messages
- `reasoning_steps`: Stores reasoning steps
- `chats`: Stores chat sessions

See the [database schema documentation](../supabase/README.md) for more details.

## Workflow

The RLHF workflow consists of the following steps:

1. **Collect Feedback**: Users provide feedback on agent responses
2. **Train Reward Model**: Train a model to predict user satisfaction
3. **Optimize Policy**: Fine-tune the language model using PPO
4. **Deploy Improved Model**: Deploy the improved model for users

This process is repeated continuously to improve the agents over time.

## Agent-Specific Models

The RLHF implementation supports agent-specific models:

- Each agent type (climate_education, job_matching, policy_analysis, etc.) has its own reward model
- The reward models are trained on feedback specific to each agent type
- The policy models are fine-tuned separately for each agent type

This allows each agent to specialize in its domain while still benefiting from the overall feedback.

## Human-in-the-Loop

The RLHF implementation includes human-in-the-loop capabilities:

- Agents can request human review of their responses
- Humans can provide feedback on agent responses
- The feedback is used to improve the agents over time

This ensures that the agents continue to improve and align with human values.

## Metrics and Evaluation

The RLHF implementation includes metrics and evaluation:

- **Reward Model Accuracy**: How well the reward model predicts user satisfaction
- **Policy Improvement**: How much the policy improves over time
- **User Satisfaction**: Direct measures of user satisfaction

These metrics are tracked over time to ensure that the agents are improving.

## Configuration

The RLHF implementation is configured using a JSON file:

```json
{
  "agent_types": ["climate_education", "job_matching", "policy_analysis"],
  "policy_model_name": "gpt2",
  "reward_model_name": "distilroberta-base",
  "ppo_learning_rate": 1e-5,
  "min_feedback_threshold": 50,
  "improvement_interval_days": 7
}
```

See the [configuration file](../config/rlhf_config.json) for more details.

## Command-Line Interface

The RLHF implementation includes a command-line interface:

```bash
# Train a specific agent
python tools/run_rlhf.py --agent-type climate_education

# Train all agents
python tools/run_rlhf.py --all-agents

# Evaluate agents
python tools/run_rlhf.py --evaluate
```

## Integration with LangGraph

The RLHF implementation integrates with LangGraph:

- The `agent_workflow.py` file uses LangGraph's Functional API
- The workflow includes human-in-the-loop capabilities
- The feedback is collected and used for RLHF

This integration ensures that the agents can be improved over time while maintaining the benefits of LangGraph.

## Future Improvements

Future improvements to the RLHF implementation include:

- **Advanced Reward Modeling**: More sophisticated reward models
- **Multi-Objective Optimization**: Optimizing for multiple objectives
- **Distributed Training**: Training across multiple machines
- **Active Learning**: Actively soliciting feedback on uncertain responses

These improvements will further enhance the RLHF capabilities of the Climate Economy Ecosystem.
