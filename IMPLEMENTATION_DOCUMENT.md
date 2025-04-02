# Massachusetts Clean Tech Ecosystem - Implementation Document

This document provides a comprehensive overview of the Climate Economy Ecosystem application implementation, including its architecture, file structure, key components, and configuration.

## Project Structure

The project follows a modern Next.js application structure using the App Router pattern:

```
climate_economy_ecosystem/
├── app/                          # Next.js App Router pages
│   ├── admin/                    # Admin dashboard
│   ├── api/                      # API routes (App Router)
│   │   ├── admin/                # Admin API endpoints
│   │   │   ├── alerts/           # System alerts API
│   │   │   └── metrics/          # Metrics API
│   │   ├── auth/                 # Authentication API
│   │   ├── jobs/                 # Job search API 
│   │   ├── notifications/        # Notifications API
│   │   └── profile/              # User profile API
│   ├── auth/                     # Auth pages
│   ├── dashboard/                # User dashboard
│   ├── login/                    # Login page
│   ├── globals.css               # Global CSS
│   ├── layout.jsx                # Root layout
│   └── page.jsx                  # Homepage
├── components/                   # React components
│   ├── Admin/                    # Admin components
│   ├── Auth/                     # Authentication components
│   ├── Chat/                     # Chat interface components
│   ├── ClimateChat/              # Climate chat specific components
│   ├── Dashboard/                # Dashboard components
│   ├── EJCommunitySupport/       # EJ community support components
│   ├── Feedback/                 # Feedback components
│   ├── Notifications/            # Notification components
│   ├── Profile/                  # User profile components
│   ├── Search/                   # Search components 
│   ├── SectorExplorer/           # Sector exploration components
│   ├── SkillsAnalysis/           # Skills analysis components
│   └── ui/                       # Reusable UI components
│       ├── Feedback/             # Feedback UI components
│       ├── Form/                 # Form UI components
│       ├── Navigation/           # Navigation UI components
│       ├── alert.jsx             # Alert component
│       ├── badge.jsx             # Badge component
│       ├── button.jsx            # Button component
│       ├── card.jsx              # Card component
│       ├── popover.jsx           # Popover component
│       ├── tabs.jsx              # Tabs component
│       └── use-toast.js          # Toast hook
├── database/                     # Database configuration
│   ├── migrations/               # Database migrations
│   ├── seeds/                    # Seed data
│   └── schema.sql                # Database schema
├── docs/                         # Documentation
│   ├── act-brand-implementation.md  # ACT brand guidelines implementation
│   ├── supabase-ssr-integration.md  # Supabase SSR integration
│   └── ui-ux-implementation.md      # UI/UX implementation guide
├── graph/                        # LangGraph agent definitions
├── hooks/                        # Custom React hooks
│   └── useAuth.js                # Authentication hook
├── lib/                          # Shared libraries
│   ├── memory/                   # Memory system for agents
│   ├── monitoring/               # Metrics and monitoring
│   ├── tools/                    # Tools for agents
│   ├── supabase-api.js           # Supabase API client
│   ├── supabase-client.js        # Supabase client-side client
│   ├── supabase-server.js        # Supabase server-side client
│   └── utils.js                  # Utility functions
├── pages/                        # Next.js Pages Router (legacy)
│   └── api/                      # API routes (Pages Router)
├── prompts/                      # Agent prompts
├── public/                       # Static files
├── tools/                        # Tool implementations
├── .env                          # Environment variables
├── jsconfig.json                 # JavaScript configuration
├── middleware.js                 # Next.js middleware
├── next.config.js                # Next.js configuration
├── package.json                  # Project dependencies
├── README.md                     # Project documentation
├── tailwind.config.js            # Tailwind CSS configuration
└── IMPLEMENTATION_STRATEGY.md    # Implementation strategy
```

## Key Components

### UI Components

The application uses a set of reusable UI components built with DaisyUI and following the ACT brand guidelines:

1. **Card Component** (`components/ui/card.jsx`)
   - Reusable card component with header, title, content, and footer sections
   - Follows ACT brand colors (seafoam-blue, spring-green)

2. **Button Component** (`components/ui/button.jsx`)
   - Customizable button with various variants and sizes
   - Includes loading state and icon support

3. **Alert Component** (`components/ui/alert.jsx`)
   - Notification alerts with different severity levels
   - Includes title and description elements

4. **Tabs Component** (`components/ui/tabs.jsx`)
   - Tabbed interface with triggers and content panels
   - Styled according to ACT brand guidelines

5. **Badge Component** (`components/ui/badge.jsx`)
   - Small labels for showing status or categories
   - Various variants and sizes available

6. **Toast System** (`components/ui/use-toast.js`)
   - Non-intrusive notifications
   - Multiple toast types (success, error, info, warning)

### Authentication

The authentication system is implemented using custom hooks and Supabase Auth:

1. **Auth Hook** (`hooks/useAuth.js`)
   - Manages authentication state
   - Provides login, logout, and user data functions

2. **Supabase Integration**
   - `lib/supabase-client.js` - Client-side Supabase integration
   - `lib/supabase-server.js` - Server-side Supabase integration
   - `lib/supabase-api.js` - API-specific Supabase integration

3. **Auth Pages**
   - `app/login/page.jsx` - Login page
   - `app/auth/signin/page.jsx` - Sign-in page
   - `app/auth/signup/page.jsx` - Sign-up page

### API Routes

The application uses Next.js App Router API routes:

1. **Admin API**
   - `app/api/admin/metrics/route.js` - System metrics API
   - `app/api/admin/alerts/route.js` - System alerts API

2. **Job Search API**
   - `app/api/jobs/search/route.js` - Job search API with filtering

3. **Profile API**
   - `app/api/profile/assessment/route.js` - Profile assessment API

4. **Notifications API**
   - `app/api/notifications/route.js` - Notifications management API

### Dashboard

The main user interface is built around a dashboard:

1. **Dashboard Page** (`app/dashboard/page.jsx`)
   - Client-side rendered dashboard
   - Shows user profile, notifications, and climate news
   - Implements ACT brand styling

2. **Admin Dashboard** (`app/admin/dashboard/page.jsx`)
   - System metrics visualization
   - User analytics
   - Usage statistics

## Database Schema

The database uses Supabase with PostgreSQL:

1. **User Profiles**
   - Stores user information, preferences, location
   - Tracks EJ community and veteran status

2. **Notifications**
   - User notifications system
   - Read/unread status tracking

3. **Job Listings**
   - Clean energy job opportunities
   - Tagged with skills and requirements

4. **Credential Evaluation**
   - International credential mapping
   - Military skill translation

5. **Metrics and Events**
   - System usage tracking
   - Performance monitoring

## Environment Configuration

The application uses environment variables from `.env`:

1. **Supabase Configuration**
   - `SUPABASE_URL` - Supabase instance URL
   - `SUPABASE_ANON_KEY` - Supabase anonymous key
   - `SUPABASE_SERVICE_KEY` - Supabase service key

2. **API Keys**
   - Various API keys for external services

3. **Redis Configuration**
   - Redis cache settings

4. **NextAuth Configuration**
   - Authentication configuration

5. **LangSmith Configuration**
   - Tracing and monitoring for LLM interactions

## Implementation Status

The application follows the implementation strategy outlined in the `IMPLEMENTATION_STRATEGY.md` document:

- **Phase 1 (Core Infrastructure)**: Completed
  - Database schema setup
  - User authentication
  - Basic UI components

- **Phase 2 (Resume Analysis & Job Matching)**: Completed
  - Resume parsing
  - Skill identification
  - Job matching system

- **Phase 3 (Military & International Credentials)**: In progress
  - Military skills translation
  - International credential evaluation

- **Phase 4 (Gateway Cities & EJ Communities)**: In progress
  - Location-based personalization
  - EJ community support

- **Phase 5 (Metrics & Monitoring)**: Completed
  - Metrics service
  - Admin dashboard
  - Event tracking

- **Phase 6 (Hybrid Search & Real-time Features)**: In progress
  - Hybrid search system
  - Real-time streaming
  - Notification system

- **Phase 7 (UI/UX Polish & Performance)**: Planned
  - UI enhancements
  - Performance optimization
  - Final testing

## ACT Brand Implementation

The application follows the ACT (Alliance for Climate Transition) brand guidelines:

1. **Color Palette**
   - Spring Green (#B2DE26) - Primary accent color
   - Midnight Forest (#001818) - Dark text
   - Moss Green (#394816) - Secondary color
   - Seafoam Blue (#E0FFFF) - Light background
   - Sand Gray (#EBE9E1) - Alternative light background

2. **Typography**
   - Helvetica for headings with specific tracking and line height
   - Inter for body text with optimized readability

3. **Component Styling**
   - All UI components follow ACT brand guidelines
   - Consistent spacing, color usage, and typography

## Next Steps

1. **Fixes and Improvements**
   - Add CardDescription export to the card component
   - Configure environment variables properly for production
   - Add ToastProvider wrapper for client components

2. **Completing Phase 6**
   - Finish real-time features
   - Complete notification system
   - Enhance hybrid search

3. **Phase 7 Implementation**
   - UI/UX polish
   - Performance optimization
   - Comprehensive testing 