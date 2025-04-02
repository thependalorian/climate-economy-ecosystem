# Climate Economy Ecosystem Implementation Documentation

## Project Overview
The Climate Economy Ecosystem is a Next.js 14 application designed to connect individuals with clean energy career opportunities in Massachusetts. The platform uses Supabase for authentication and data storage, and implements ACT brand guidelines for consistent design.

## Technology Stack
- **Frontend**: Next.js 14 with App Router and SSR
- **Backend**: Supabase
- **Styling**: Tailwind CSS and DaisyUI
- **Authentication**: Supabase Auth
- **Database**: Supabase PostgreSQL
- **Deployment**: Vercel

## Brand Guidelines Implementation
### Colors
- Spring Green: #B2DE26
- Moss Green: #394816
- Midnight Forest: #001818
- Seafoam Blue: #E0FFFF
- Sand Gray: #EBE9E1

### Typography
- Headings: Helvetica
- Body: Inter
- Letter-spacing: -0.02em for headings
- Line-height: 1.2 for headings, 1.5 for body

## Database Schema

### Tables

#### profiles
```sql
CREATE TABLE profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    email TEXT NOT NULL,
    full_name TEXT,
    persona TEXT,
    skills TEXT[],
    interests TEXT[],
    location TEXT,
    background TEXT,
    will_relocate BOOLEAN DEFAULT false,
    in_ej_community BOOLEAN DEFAULT false,
    consent_to_share BOOLEAN DEFAULT false,
    consent_to_email BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

#### jobs
```sql
CREATE TABLE jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    description TEXT,
    requirements TEXT[],
    location TEXT,
    salary_range TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

#### training_programs
```sql
CREATE TABLE training_programs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    provider TEXT NOT NULL,
    description TEXT,
    duration TEXT,
    cost TEXT,
    skills_covered TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

### Row Level Security (RLS) Policies
- Users can only view and update their own profiles
- Jobs and training programs are publicly viewable
- Users can only manage their own saved jobs and training programs

## Authentication Flow
1. User signs up through the landing page
2. Supabase creates a new user record
3. User is redirected to the onboarding flow
4. Onboarding data is saved to the profiles table
5. User is redirected to the dashboard

## Onboarding Flow
The onboarding process consists of 5 steps:

1. **Background Information**
   - User selects their persona (veteran, international, student, EJ community, reentry)
   - Optional background details

2. **Skills Assessment**
   - Selection from predefined skills list
   - Option to add custom skills

3. **Interests**
   - Selection of clean energy sectors
   - Visual cards with sector images

4. **Location Preferences**
   - Massachusetts region selection
   - Relocation preferences
   - EJ community status

5. **Consent and Review**
   - Review of collected information
   - Consent to share data
   - Email preferences

## API Routes

### Onboarding API
```javascript
POST /api/onboarding
```
- Handles submission of onboarding data
- Updates user profile in Supabase
- Requires authenticated session

## Metrics System

The Climate Economy Ecosystem includes a comprehensive metrics system to track user engagement, profile enrichment, and job search activity.

### Metrics Database Tables

#### metrics
```sql
CREATE TABLE metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id),
    event_type TEXT NOT NULL, -- profile_enrichment, enhanced_job_search, skill_verification, etc.
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

#### search_analytics
```sql
CREATE TABLE search_analytics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id),
    search_query TEXT,
    search_type TEXT, -- enhanced, recommendation
    result_count INTEGER,
    search_params JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

### Metrics Components

1. **Frontend Tracking**
   - JavaScript metrics service for client-side tracking
   - Integrated with key components (ProfileEnrichment, EnhancedJobSearch)
   - Tracks user interactions in real-time

2. **Backend Processing**
   - Python metrics service for server-side processing
   - API endpoints for collecting metrics data
   - Data aggregation for dashboard visualizations

3. **Admin Dashboard**
   - Visualizes metrics data with Chart.js
   - Provides insights on user engagement
   - Supports filtering by time range (7d, 30d, 90d)

### Metrics API Routes

```javascript
POST /api/metrics/profile-enrichment
POST /api/metrics/enhanced-job-search
POST /api/metrics/skill-verification
GET /api/admin/metrics
```

### Dashboard Interface

The admin metrics dashboard (`/admin/metrics`) provides:
- Overview statistics (total users, enriched profiles)
- Profile enrichment trends
- Skills distribution analysis
- Job search activity monitoring
- Search term popularity

## Components Structure

### Core Components
- `OnboardingLayout`: Wrapper for onboarding pages
- `StepProgress`: Progress indicator for onboarding steps
- `Question`: Reusable question component
- `SelectableCard`: Visual selection component

### Pages
- `/`: Landing page
- `/onboarding`: Onboarding flow
- `/dashboard`: User dashboard (protected)
- `/counselor`: AI counselor interface

## Environment Variables
Required environment variables in `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

## Known Issues
1. Image optimization warnings for Next.js Image component
   - Need to update legacy props (layout, objectFit) to new format
   - Missing image assets in public directory

2. Authentication warnings
   - NextAuth.js debug mode enabled
   - Need to configure proper debug settings

## Next Steps
1. Add missing image assets to public directory
2. Update Next.js Image components to use new format
3. Implement job matching algorithm
4. Add training program recommendations
5. Set up email notifications
6. Implement admin dashboard
7. Add analytics tracking
8. Set up automated testing

## Development Guidelines
1. Follow ACT brand guidelines for all UI components
2. Use DaisyUI components for consistent styling
3. Implement proper error handling and loading states
4. Ensure all forms have proper validation
5. Maintain responsive design across all breakpoints
6. Follow TypeScript best practices
7. Write comprehensive documentation for new features 

## Reinforcement Learning from Human Feedback (RLHF)

The Climate Economy Ecosystem implements a comprehensive RLHF system to continuously improve AI responses based on user feedback.

### RLHF Database Schema

#### reasoning_steps
```sql
CREATE TABLE reasoning_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    step_content TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### chat_feedback (extensions)
```sql
ALTER TABLE chat_feedback
ADD COLUMN step_id UUID REFERENCES reasoning_steps(id) ON DELETE CASCADE,
ADD COLUMN feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
ADD COLUMN feedback_type TEXT DEFAULT 'message';
```

### Feedback Collection Components

1. **StepFeedback.jsx**
   - Located at: `/components/Chat/StepFeedback.jsx`
   - Collects feedback on individual reasoning steps
   - Provides thumbs up/down and optional star rating

2. **StreamingResponse.jsx**
   - Located at: `/components/Chat/StreamingResponse.jsx`
   - Enhanced to display reasoning steps
   - Integrates step-level feedback UI components

### RLHF API Endpoints

```javascript
POST /api/assistant/feedback
```
- Handles submission of both message-level and step-level feedback
- Stores feedback in the chat_feedback table
- Updates user satisfaction scores
- Forwards feedback to the metrics service

### Machine Learning Components

1. **Reward Model**
   - Located at: `/lib/ml/reward_model.py`
   - Predicts user satisfaction from query-response pairs
   - Trained on historical user feedback data

2. **Feedback Processor**
   - Located at: `/lib/ml/feedback_processor.py`
   - Prepares feedback data for model training
   - Converts raw feedback into training examples

3. **RLHF Training Script**
   - Located at: `/tools/train_rlhf.py`
   - Trains the reward model based on feedback data
   - Implements PPO (Proximal Policy Optimization) for policy model training

### Training Automation

1. **GitHub Workflow**
   - Located at: `/.github/workflows/rlhf_training.yml`
   - Triggers weekly training runs
   - Stores model artifacts for deployment

2. **Shell Script**
   - Located at: `/scripts/train_model.sh`
   - Options for training reward model, PPO fine-tuning, or both
   - Handles dependency checking and environment setup

### Metrics Integration

The RLHF system integrates with the existing metrics pipeline:

1. **MetricsService.js**
   - New method: `trackChatFeedback`
   - Tracks feedback events for analytics

2. **Metrics Dashboard**
   - New section for RLHF metrics
   - Visualizes feedback distribution and model performance

### Future Improvements

Planned enhancements to the RLHF system:
- Multi-objective optimization (balancing helpfulness, accuracy, factuality)
- Enhanced feedback collection with in-line annotations
- Advanced training techniques (DPO, RRHF) 