# Climate Economy Ecosystem Platform Documentation

## Overview

The Climate Economy Ecosystem platform is a comprehensive web application designed to connect Massachusetts residents with clean energy career opportunities, training programs, and resources. The platform serves as a central hub for job seekers, employers, training providers, and community organizations in the Massachusetts clean energy economy.

## Core Components

The platform consists of several key components, each serving a specific purpose in the user journey:

### 1. SectorExplorer

**Purpose**: Allows users to explore different sectors of the clean energy economy in Massachusetts.

**Features**:
- Interactive sector cards with key metrics
- Detailed sector information including job counts, growth rates, and average salaries
- Job listings specific to each sector
- Skills required for success in each sector
- Training programs related to each sector

**Implementation**: `components/SectorExplorer/index.jsx`

**Data Requirements**:
- Sector metadata (name, description, growth rate, etc.)
- Job listings by sector
- Skills data by sector
- Training program data by sector

### 2. SkillsAnalysis

**Purpose**: Helps users identify in-demand skills in the clean energy economy and assess their personal skill gaps.

**Features**:
- Visualization of high-demand skills with growth metrics
- Personalized skill gap analysis based on user profile
- Recommendations for skill development
- Training program suggestions to address skill gaps
- Job opportunities that match existing skills

**Implementation**: `components/SkillsAnalysis/index.jsx`

**Data Requirements**:
- Skills metadata (demand score, growth rate, salary impact)
- User skills profile
- Training programs by skill
- Job listings by required skills

### 3. Profile

**Purpose**: Manages user profile information and provides personalized career insights.

**Features**:
- Personal information management
- Work experience, education, and certification tracking
- Skills assessment and verification
- Job match scoring
- Career pathway visualization
- Profile export and sharing

**Implementation**: `components/Profile/index.jsx`

**Data Requirements**:
- User personal information
- Work history and education
- Skills and certifications
- Job match algorithm results
- Career pathway data

### 4. EJCommunitySupport

**Purpose**: Provides specialized resources and support for residents of Environmental Justice communities in Massachusetts.

**Features**:
- EJ community finder
- Community-specific programs and resources
- Local employer information
- Support services (transportation, childcare, financial)
- Success stories from EJ community members

**Implementation**: `components/EJCommunitySupport/index.jsx`

**Data Requirements**:
- EJ community definitions and boundaries
- Community-specific programs and resources
- Local employer data
- Support service information
- Success story testimonials

### 5. Dashboard

**Purpose**: Serves as the central hub for users to access personalized information and recommendations.

**Features**:
- Profile completion tracking
- Job match recommendations
- Upcoming events and programs
- Notification system
- Industry metrics and trends
- Quick access to key platform features

**Implementation**: `components/Dashboard/index.jsx`

**Data Requirements**:
- User profile data
- Job match results
- Event and program calendar
- Notification system
- Industry metrics and trends

### 6. Chat Interface

**Purpose**: Provides an AI-powered assistant to help users navigate the platform and find relevant information.

**Features**:
- Natural language interaction
- File upload for resume analysis
- Streaming responses for better user experience
- Source citations for information provided
- Feedback mechanism for response quality

**Implementation**:
- `components/Chat/EnhancedChatInterface.jsx`
- `components/Chat/StreamingResponse.jsx`
- `app/chat/page.jsx`
- `app/api/chat/stream/route.js`
- `app/api/resume/upload/route.js`
- `app/api/chat/history/route.js`
- `app/api/chat/feedback/route.js`

**Data Requirements**:
- OpenAI API integration
- Vector database for relevant context retrieval
- User conversation history
- Document processing capabilities
- Feedback storage and analysis

## Technical Architecture

### Frontend

The frontend is built using Next.js 13+ with the App Router, providing a modern, server-component-based architecture with client-side interactivity where needed.

**Key Technologies**:
- **React**: Core UI library
- **Next.js**: Framework for server-side rendering and routing
- **Tailwind CSS**: Utility-first CSS framework for styling
- **shadcn/ui**: Component library built on Radix UI
- **Lucide Icons**: Icon library

### Backend

The backend uses Next.js API routes for serverless functions, with Supabase providing database, authentication, and storage services.

**Key Technologies**:
- **Next.js API Routes**: Serverless function endpoints
- **Supabase**: PostgreSQL database with vector extensions
- **OpenAI API**: For AI assistant capabilities
- **NextAuth.js**: Authentication framework

### Data Storage

**Primary Data Store**:
- **Supabase PostgreSQL**: Relational database for structured data
- **pgvector**: Vector extension for similarity search

**Tables**:
- `users`: User account information
- `profiles`: Extended user profile data
- `skills`: Skill definitions and metadata
- `user_skills`: Junction table for user-skill relationships
- `jobs`: Job listings and metadata
- `climate_memories`: Knowledge base for the AI assistant
- `feedback`: User feedback on AI responses
- `resume_analyses`: Results from resume analysis

### Authentication

Authentication is handled through NextAuth.js with multiple provider options:

- Google OAuth
- Email/Password
- (Optional) LinkedIn OAuth for professional networking

### AI Integration

The platform uses AI for several key features:

- **Chat Assistant**: OpenAI GPT models for natural language interaction
- **Resume Analysis**: AI-powered extraction of skills and experience
- **Job Matching**: AI algorithms to match user profiles with job opportunities
- **Skill Gap Analysis**: AI assessment of user skills versus job requirements

## Deployment Architecture

The application is designed to be deployed on Vercel, with Supabase providing the backend services.

**Environment Configuration**:
- Development: Local environment with Docker containers
- Production: Vercel deployment with Supabase cloud services

**Security Considerations**:
- Environment variables for sensitive credentials
- JWT-based authentication
- Row-level security in Supabase
- Content security policies
- Regular security audits

## User Roles and Permissions

The platform supports multiple user roles with different permissions:

1. **Job Seekers**: Standard users looking for career opportunities
   - Access to all public features
   - Personal profile management
   - Job application capabilities

2. **Employers**: Organizations posting job opportunities
   - Job posting management
   - Applicant tracking
   - Company profile management

3. **Training Providers**: Organizations offering training programs
   - Program listing management
   - Student enrollment tracking
   - Outcome reporting

4. **Administrators**: Platform managers
   - User management
   - Content moderation
   - Analytics and reporting
   - System configuration

## Development Workflow

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Run `npm run generate-keys` to create secure keys
4. Start the development environment with `npm run dev`
5. For full stack development, use `npm run docker:dev:up`

### Testing

- Unit tests: Jest and React Testing Library
- Integration tests: Cypress
- E2E tests: Playwright

### Deployment

1. Push changes to the main branch
2. Vercel automatically deploys the application
3. Database migrations are applied automatically

## Future Enhancements

Planned enhancements for future releases:

1. **Mobile Application**: Native mobile experience for iOS and Android
2. **Advanced Analytics**: Enhanced reporting for administrators and employers
3. **Community Forums**: Peer-to-peer support and networking
4. **Learning Management System**: Integrated course delivery
5. **Employer Dashboard**: Enhanced tools for employers
6. **API for Partners**: Public API for integration with partner systems

## Appendix

### API Documentation

#### Chat API

- `POST /api/chat/stream`: Stream a chat response
- `GET /api/chat/history`: Get user chat history
- `POST /api/chat/feedback`: Submit feedback on a chat response

#### Resume API

- `POST /api/resume/upload`: Upload and analyze a resume

#### User API

- `GET /api/user/profile`: Get user profile
- `PUT /api/user/profile`: Update user profile
- `GET /api/user/skills`: Get user skills
- `PUT /api/user/skills`: Update user skills

#### Jobs API

- `GET /api/jobs`: Get job listings
- `GET /api/jobs/:id`: Get job details
- `POST /api/jobs/apply`: Apply for a job

### Component Reference

Each component follows a consistent structure:

- **Props Interface**: Defined TypeScript interfaces for component props
- **State Management**: Local state using React hooks
- **API Integration**: Data fetching using SWR or React Query
- **Styling**: Tailwind CSS classes with consistent design system
- **Accessibility**: ARIA attributes and keyboard navigation
- **Responsiveness**: Mobile-first design approach

### Security Considerations

The platform implements several security best practices:

- **Authentication**: Secure, JWT-based authentication
- **Authorization**: Role-based access control
- **Data Protection**: Encryption for sensitive data
- **Input Validation**: Server-side validation of all inputs
- **Output Encoding**: Prevention of XSS attacks
- **CSRF Protection**: Token-based protection against CSRF
- **Rate Limiting**: Protection against brute force attacks
- **Audit Logging**: Tracking of security-relevant events

### AI Training and Feedback Loop

#### RLHF Implementation

The platform implements a complete Reinforcement Learning from Human Feedback (RLHF) pipeline for the Massachusetts Climate Assistant. This implementation allows the assistant to continuously improve based on user feedback and domain-specific knowledge.

**Components:**

1. **Massachusetts Climate Retriever** (`lib/retrieval/massachusetts_climate_retriever.py`)
   - Domain-specific retrieval system for Massachusetts climate economy information
   - Uses PDF reports and web content as knowledge sources
   - Implements strict constraints and guardrails to ensure accurate information
   - Provides source citations and confidence levels

2. **Feedback Collection System** (`app/api/climate/feedback/route.js`)
   - Collects various types of feedback (ratings, thumbs up/down, comparisons)
   - Stores feedback in Supabase for later training
   - Calculates aggregated metrics for monitoring

3. **Reward Model Training** (`scripts/train_climate_reward_model.py`)
   - Trains a reward model based on collected user feedback
   - Uses a transformer-based architecture (DistilRoBERTa)
   - Optimizes for alignment with user preferences
   - Supports both rating-based and comparison-based training

4. **Policy Optimization** (`scripts/optimize_climate_policy.py`)
   - Implements Proximal Policy Optimization (PPO) for policy refinement
   - Uses the trained reward model to guide optimization
   - Balances exploration and exploitation
   - Prevents catastrophic forgetting of base capabilities

5. **Evaluation Framework** (`scripts/evaluate_rlhf_improvements.py`)
   - Quantitatively measures improvements from RLHF
   - Compares base and optimized models
   - Generates visualizations of performance metrics
   - Tracks progress over time

#### RLHF Process Flow

The platform uses a continuous improvement approach for AI components:

1. **Initial Training**: Base models fine-tuned on domain-specific Massachusetts climate economy data
2. **User Feedback**: Collection of explicit feedback (ratings, thumbs up/down) and implicit feedback (user engagement)
3. **Reward Modeling**: Training of reward models based on collected feedback
4. **Policy Optimization**: Refinement of AI behavior using PPO guided by the reward model
5. **Evaluation**: Regular assessment of AI performance and alignment with Massachusetts-specific requirements
6. **Iteration**: Continuous improvement based on evaluation results

#### Constraints and Guardrails

The Massachusetts Climate Assistant implements several constraints to ensure high-quality, relevant responses:

- **Geographic Focus**: Ensures responses are specific to Massachusetts
- **Topic Constraints**: Limits responses to clean energy economy topics
- **Source Requirements**: Prioritizes Massachusetts-specific, recent, and authoritative sources
- **Response Requirements**: Enforces citation of sources, acknowledgment of uncertainty, and consideration of environmental justice

This comprehensive RLHF implementation ensures that the AI components of the platform continuously improve based on real user interactions while maintaining strict adherence to Massachusetts-specific information requirements.
