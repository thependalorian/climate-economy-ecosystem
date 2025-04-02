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