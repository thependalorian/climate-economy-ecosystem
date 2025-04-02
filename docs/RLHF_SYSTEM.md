# Reinforcement Learning from Human Feedback (RLHF) System

## Overview

The Climate Economy Ecosystem uses RLHF to continually improve the quality of AI responses based on user feedback. This document outlines the technical implementation and integration of the RLHF system.

## Architecture

![RLHF System Architecture](https://mermaid.ink/img/pako:eNqVVE1v2zAM_SuETjtgaZcedhkKLN1WoJcOG3YodigsM7aAyHQoKl2C5L-PlJzEdoJlPcQWqUfy8ZGkbpgxCVnKZipTCmr-LM9-lCzKGxd0xoKRBYsS3S7qJcl0KZ4VaINXMfBCsYnhb9B6BTTxTmtCpRPtclzqLCXhA7T63QNXpAU6lURrQDjHo7Q_kFoZrE61u1EJJeQoToBQ1x-3GMQE5B3Hm8dqcbA5SsGJjYA81ER8EvU9OA8jPr8qlAE-L1mJ1hF-2g-yJo5SX8h-yiGdoWbq8BkJFzs0Dq15aB0t2kXd_lBOKOvAkb0q4KiHYtcuXeRBb-ej-rUy9lBLcuA2MnqHLy5a-NUP3NdCPmJoMpjIK6_ckL9SHgxDXnWGwzvlv8cK7Qs_nK_KlSnDYrg2yqFWOAJ3QeXkVXdpotZXWhIGylr0-0jroXsPDR-QHtg7c_6Ql4pNSYs6V1n0zF8qUDNY3pWgMDFdRnGzZRG2lV6zj5c3f9xK0XaS9bvfq7e8FfB-7bK0q-dPHU9HLbVkx3Vj3X0lkpG2hXdOsz2Wj1tL6k5U8YSKUocH3pvDmEtBK3VmC1OU7GN4_PNl_3n_eD_8DTH8uR-A_wFWJHO3)

The RLHF system consists of the following components:

1. **Feedback Collection UI**
   - Message-level feedback via thumbs up/down
   - Step-level feedback for reasoning steps
   - Numeric ratings (1-5 scale)

2. **Feedback Storage**
   - Supabase database tables for structured feedback
   - User engagement metrics

3. **Metrics Pipeline**
   - Client-side tracking
   - Server-side aggregation
   - Periodic data processing

4. **Model Training**
   - Reward model training
   - PPO fine-tuning
   - Automated retraining workflows

## Database Schema

The following database tables are used for the RLHF system:

```sql
-- Reasoning steps table
CREATE TABLE public.reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES public.chats(id),
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Chat feedback table (extended for RLHF)
ALTER TABLE public.chat_feedback
ADD COLUMN step_id UUID REFERENCES public.reasoning_steps(id),
ADD COLUMN feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5);
```

## Components

### Feedback UI Components

1. **StepFeedback.jsx**
   - Located at: `/components/Chat/StepFeedback.jsx`
   - Purpose: Collects feedback on individual reasoning steps
   - Features: Thumbs up/down, submission handling, UI state management

2. **StreamingResponse.jsx**
   - Located at: `/components/Chat/StreamingResponse.jsx`
   - Enhancements: Added step metadata processing, reasoning step components

### API Endpoints

1. **Feedback API**
   - Located at: `/app/api/assistant/feedback/route.js`
   - Methods: `POST`
   - Purpose: Stores user feedback in database
   - Features: Supports both message and step-level feedback

### Metrics Service

1. **MetricsService.js**
   - Located at: `/lib/monitoring/metrics_service.js`
   - New Methods: `trackChatFeedback`
   - Purpose: Collects and processes feedback metrics

### Machine Learning Components

1. **ClimateRewardModel**
   - Located at: `/lib/ml/reward_model.py`
   - Purpose: Predicts user satisfaction from query-response pairs
   - Features: Training, evaluation, batch processing

2. **FeedbackProcessor**
   - Located at: `/lib/ml/feedback_processor.py`
   - Purpose: Prepares feedback data for model training
   - Features: Data loading, preprocessing, train/test splitting

3. **RLHF Training Pipeline**
   - Located at: `/tools/train_rlhf.py`
   - Purpose: Trains reward model and policy using PPO
   - Features: Command-line interface, hyperparameter tuning

## Training Workflow

The RLHF training workflow is automated using GitHub Actions:

1. **Scheduled Training**
   - Configured in: `/.github/workflows/rlhf_training.yml`
   - Schedule: Weekly on Sundays at 1 AM UTC
   - Steps: Environment setup, dependency installation, model training, artifact storage

2. **Manual Training**
   - Script: `/scripts/train_model.sh`
   - Options: Train reward model, PPO fine-tuning, or both
   - Usage: `./scripts/train_model.sh [reward|ppo|both]`

## Integration Points

The RLHF system integrates with the following components:

1. **Chat Interface**
   - Step-level feedback UI
   - Message-level feedback UI
   - Feedback submission handling

2. **User Engagement Metrics**
   - Satisfaction score calculation
   - Feedback tracking
   - Performance monitoring

3. **Model Deployment**
   - Automatic model updates
   - A/B testing of fine-tuned models

## Best Practices

When working with the RLHF system, consider the following best practices:

1. **Data Quality**
   - Regularly audit feedback data for quality and bias
   - Monitor outliers and abnormal patterns
   - Ensure representative sampling across user demographics

2. **Model Evaluation**
   - Track reward model performance over time
   - Compare fine-tuned models against baselines
   - Measure impact on user satisfaction metrics

3. **Deployment Strategy**
   - Use canary deployments for new models (5-10% of traffic)
   - Monitor performance closely during initial rollout
   - Roll back if negative impacts observed

4. **Privacy Considerations**
   - Anonymize user data used for training
   - Obtain explicit consent for feedback collection
   - Provide options to delete feedback history

## Troubleshooting

Common issues and their solutions:

1. **Missing feedback data**
   - Check client-side metrics tracking
   - Verify API endpoint functionality
   - Inspect database schema and permissions

2. **Training failures**
   - Check for sufficient feedback data volume
   - Verify dependencies and environment setup
   - Inspect training logs for error messages

3. **Model performance regression**
   - Compare reward scores before and after training
   - Analyze feedback distribution for potential bias
   - Consider rolling back to previous model version

## Future Improvements

Planned enhancements to the RLHF system:

1. **Multi-objective optimization**
   - Balance helpfulness, accuracy, and other metrics
   - Incorporate domain-specific reward signals

2. **Enhanced feedback collection**
   - In-line annotation of responses
   - Structured feedback for specific aspects
   - Implicit feedback from user engagement

3. **Advanced training techniques**
   - Exploration of RLHF alternatives (DPO, RRHF)
   - Distillation of fine-tuned models
   - Integration with domain adaptation methods

## References

- [Implementation RFL Documentation](./implementation_rfl.md)
- [OpenAI InstructGPT Paper](https://arxiv.org/abs/2203.02155)
- [HuggingFace TRL Library](https://github.com/huggingface/trl) 