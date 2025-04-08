# Massachusetts Climate Assistant RLHF Implementation

This document provides an overview of the Reinforcement Learning from Human Feedback (RLHF) implementation for the Massachusetts Climate Assistant.

## Overview

The Massachusetts Climate Assistant uses RLHF to continuously improve its responses based on user feedback. The system is specifically designed to provide accurate, relevant information about the Massachusetts clean energy economy, with strict constraints to ensure geographic and topical relevance.

## Components

### 1. Massachusetts Climate Retriever

**File**: `lib/retrieval/massachusetts_climate_retriever.py`

The retriever is a domain-specific system that:
- Accesses Massachusetts climate economy reports stored in Supabase
- Implements strict constraints and guardrails
- Provides source citations and confidence levels
- Ensures responses are specific to Massachusetts

Key features:
- Vector search with contextual compression
- PDF and web content ingestion
- Constraint enforcement
- Source attribution

### 2. Feedback Collection System

**Files**:
- `app/api/climate/feedback/route.js`
- `components/Climate/ClimateAssistant.jsx`

The feedback system collects:
- Rating-based feedback (1-5 stars)
- Binary feedback (thumbs up/down)
- Comparison feedback (preferred vs. rejected responses)
- Aspect-specific feedback (helpfulness, accuracy, etc.)

All feedback is stored in Supabase for later training.

### 3. Reward Model Training

**File**: `scripts/train_climate_reward_model.py`

The reward model:
- Is trained on collected user feedback
- Uses a transformer-based architecture (DistilRoBERTa)
- Optimizes for alignment with user preferences
- Supports both rating-based and comparison-based training

Training process:
1. Fetch feedback data from Supabase
2. Prepare datasets (train/validation split)
3. Fine-tune the model
4. Evaluate performance
5. Save the best model

### 4. Policy Optimization

**File**: `scripts/optimize_climate_policy.py`

The policy optimization:
- Implements Proximal Policy Optimization (PPO)
- Uses the trained reward model to guide optimization
- Balances exploration and exploitation
- Prevents catastrophic forgetting

Optimization process:
1. Fetch training queries
2. Generate responses with current policy
3. Compute rewards using reward model
4. Update policy with PPO
5. Repeat until convergence

### 5. Evaluation Framework

**File**: `scripts/evaluate_rlhf_improvements.py`

The evaluation framework:
- Quantitatively measures improvements from RLHF
- Compares base and optimized models
- Generates visualizations of performance metrics
- Tracks progress over time

Metrics include:
- Mean reward scores
- Reward distribution
- Improvement percentage
- Per-query improvements

## RLHF Process Flow

The complete RLHF process follows these steps:

1. **Initial Setup**:
   - Ingest Massachusetts climate reports into Supabase
   - Set up constraints and guardrails
   - Deploy base assistant

2. **Feedback Collection**:
   - Users interact with the assistant
   - Feedback is collected through UI components
   - Feedback is stored in Supabase

3. **Reward Model Training**:
   - Fetch feedback data
   - Train reward model
   - Evaluate reward model performance
   - Save best model

4. **Policy Optimization**:
   - Use reward model to guide policy updates
   - Implement PPO for optimization
   - Balance exploration and exploitation
   - Save optimized policy

5. **Evaluation**:
   - Compare base and optimized models
   - Generate performance metrics
   - Create visualizations
   - Document improvements

6. **Deployment**:
   - Deploy optimized model
   - Continue collecting feedback
   - Repeat the process

## Constraints and Guardrails

The Massachusetts Climate Assistant implements several constraints:

- **Geographic Focus**: Ensures responses are specific to Massachusetts
- **Topic Constraints**: Limits responses to clean energy economy topics
- **Source Requirements**: Prioritizes Massachusetts-specific, recent, and authoritative sources
- **Response Requirements**: Enforces citation of sources, acknowledgment of uncertainty, and consideration of environmental justice

## Usage

### Setting Up the Retriever

```python
# Initialize the retriever
retriever = MassachusettsClimateRetriever(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    constraints=MassachusettsClimateConstraints(),
    collection_name="climate_memories",
    model_name="gpt-4o"
)

# Ingest reports
await retriever.ingest_required_reports()

# Query the retriever
result = await retriever.query("What are the top clean energy jobs in Massachusetts?")
print(result["answer"])
```

### Training the Reward Model

```bash
# Run the reward model training script
python scripts/train_climate_reward_model.py
```

### Optimizing the Policy

```bash
# Run the policy optimization script
python scripts/optimize_climate_policy.py
```

### Evaluating Improvements

```bash
# Run the evaluation script
python scripts/evaluate_rlhf_improvements.py
```

## Benefits of RLHF Implementation

The RLHF implementation provides several benefits:

1. **Improved Accuracy**: Responses become more accurate over time based on user feedback
2. **Domain Specificity**: Ensures responses are specific to Massachusetts clean energy economy
3. **Source Attribution**: Provides citations to authoritative sources
4. **Constraint Enforcement**: Prevents responses outside the defined scope
5. **Continuous Improvement**: System gets better with more user interactions

## Limitations and Future Work

Current limitations:

1. **Data Dependency**: Performance depends on the quality and quantity of feedback data
2. **Computational Requirements**: Training and optimization require significant computational resources
3. **Cold Start**: Initial performance may be limited until sufficient feedback is collected

Future work:

1. **Multi-objective Optimization**: Optimize for multiple objectives (accuracy, helpfulness, etc.)
2. **Human-in-the-loop Verification**: Add human verification for critical information
3. **Expanded Knowledge Base**: Include more Massachusetts-specific climate economy resources
4. **Personalization**: Adapt responses based on user preferences and history
