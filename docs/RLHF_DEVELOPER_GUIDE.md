# RLHF Developer Guide

This guide provides instructions for developers working with the Reinforcement Learning from Human Feedback (RLHF) system in the Climate Economy Ecosystem.

## Setup

### Prerequisites

- Python 3.9+
- NodeJS 18+
- Supabase CLI
- Access to the Climate Economy Ecosystem codebase
- Required Python packages: `torch`, `transformers`, `trl`, `pandas`
- Required Node packages: All project dependencies

### Database Setup

1. Make sure your Supabase instance is running:

```bash
npx supabase start
```

2. Apply the RLHF migration:

```bash
npx supabase db push
```

This will apply the migration file `database/migrations/008_rlhf_schema.sql` which creates the necessary tables and updates the schema.

## Components

### Frontend Components

#### StepFeedback Component

The `StepFeedback` component allows users to provide feedback on individual reasoning steps.

```jsx
// Usage example
import StepFeedback from '@/components/Chat/StepFeedback';

<StepFeedback 
  stepId="step-uuid"
  chatId="chat-uuid"
  onFeedbackSubmit={(feedback) => console.log(feedback)}
/>
```

#### StreamingResponse Component

The enhanced `StreamingResponse` component displays reasoning steps and collects feedback.

```jsx
// Usage example
import StreamingResponse from '@/components/Chat/StreamingResponse';

<StreamingResponse
  query="How do I find green jobs in Massachusetts?"
  showSteps={true}
  collectFeedback={true}
  onComplete={(response) => console.log(response)}
/>
```

### Backend Components

#### Feedback API

The feedback API endpoint handles both message-level and step-level feedback.

```javascript
// Example request
const response = await fetch('/api/assistant/feedback', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messageId: 'message-uuid', // Optional for message-level feedback
    step_id: 'step-uuid',      // Optional for step-level feedback
    chat_id: 'chat-uuid',      // Required
    feedback: 'positive',      // 'positive' or 'negative'
    feedback_type: 'step',     // 'message' or 'step'
    feedback_score: 4          // Optional, 1-5 score
  }),
});
```

#### Metrics Service

The metrics service includes a new method for tracking chat feedback.

```javascript
// Example usage
import { MetricsService } from '@/lib/monitoring/metrics_service';

const metricsService = new MetricsService();
metricsService.trackChatFeedback({
  chatId: 'chat-uuid',
  feedbackType: 'step',
  feedbackScore: 4,
  stepId: 'step-uuid',
  messageId: 'message-uuid'
});
```

## Machine Learning

### Reward Model

The reward model predicts user satisfaction with AI responses.

```python
# Example usage
from lib.ml.reward_model import ClimateRewardModel

model = ClimateRewardModel()

# Compute a reward score for a query-response pair
score = model.compute_reward(
    query="How do I find clean energy jobs?",
    response="You can search on the Massachusetts Clean Energy Center website..."
)
print(f"Reward score: {score}")
```

### Training the Model

#### Using the Script

```bash
# Train the reward model
./scripts/train_model.sh reward

# Train the policy model with PPO
./scripts/train_model.sh ppo

# Train both models
./scripts/train_model.sh both
```

#### Manual Training

```python
# Example training code
from lib.ml.reward_model import ClimateRewardModel
from lib.ml.feedback_processor import FeedbackProcessor

processor = FeedbackProcessor()
train_data, val_data = processor.load_and_prepare_data()

model = ClimateRewardModel()
metrics = model.train(
    train_data=train_data,
    validation_data=val_data,
    epochs=3
)
```

## Testing

### Frontend Testing

1. Run the frontend in development mode:

```bash
npm run dev
```

2. Test the feedback components at `/test/rlhf`
3. Verify that feedback is properly stored in the database

### Backend Testing

1. Run the test suite:

```bash
npm test lib/ml
```

2. Test the API endpoint manually:

```bash
curl -X POST http://localhost:3000/api/assistant/feedback \
  -H "Content-Type: application/json" \
  -d '{"messageId":"test-message","feedback":"positive"}'
```

### Model Testing

1. Run the evaluation script:

```bash
python tools/eval_rlhf.py --model-path data/reward_model
```

## Troubleshooting

### Common Issues

1. **Missing Database Tables**
   - Ensure the migration has been applied: `npx supabase db push`
   - Check if tables exist: `npx supabase db query "SELECT * FROM information_schema.tables WHERE table_name = 'reasoning_steps';"`

2. **Model Training Errors**
   - Verify Python dependencies are installed
   - Check if sufficient feedback data is available
   - Look for error logs in the console output

3. **Feedback Not Showing in Dashboard**
   - Verify the metrics service is properly tracking events
   - Check browser console for API errors
   - Ensure the user has the required permissions

## Resources

- [RLHF System Documentation](./RLHF_SYSTEM.md)
- [Implementation Details](./implementation_rfl.md)
- [OpenAI InstructGPT Paper](https://arxiv.org/abs/2203.02155)
- [HuggingFace TRL Library](https://github.com/huggingface/trl) 