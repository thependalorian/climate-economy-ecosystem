# Massachusetts Clean Tech Ecosystem Assistant

## Overview
This platform connects job seekers with clean tech opportunities in Massachusetts, with a focus on Environmental Justice communities and Gateway Cities. It uses AI-powered resume analysis to provide personalized career pathways, education recommendations, and job matches.

## Strategic Context
The Climate Ecosystem Assistant is designed to create a just, rapid, and equitable climate transition by connecting underrepresented communities with training and career opportunities in renewable energy, clean transportation, and decarbonizing buildings.

## Target Populations
- Residents of Environmental Justice neighborhoods 
- Individuals from low-income backgrounds
- Minority and Women-owned Business Enterprises
- Veterans transitioning to civilian careers
- International professionals with overseas credentials
- Workforce reentry candidates

## Target Locations
Brockton, Boston, Fall River/New Bedford, Lawrence/Lowell, Springfield, Worcester, and other Massachusetts Gateway Cities.

## Core Features
- Resume parsing and analysis with climate tech relevance scoring
- Skill gap identification and recommendation engine
- Career pathway generation for clean tech sectors
- Education and training program matching
- Military skills translator and credential evaluator
- Real-time processing with streaming updates

## Project Structure
- `app/`: Next.js application pages and API routes
- `components/`: Reusable UI components with DaisyUI
- `lib/`: Shared libraries and utilities
- `public/`: Static files
- `styles/`: CSS and styling based on ACT brand guidelines
- `utils/`: Utility functions
- `models/`: Data models
- `hooks/`: Custom React hooks
- `graph/`: LangGraph agent definitions
- `state/`: State management
- `tools/`: Tool definitions for agents
- `prompts/`: System prompts for agents
- `tests/`: Test files

## Technologies
- Next.js 14 with App Router
- DaisyUI for styling (following ACT brand guidelines)
- LangGraph for agent orchestration
- LangChain for LLM integration
- Supabase for data persistence
- Socket.IO for real-time updates

## Implementation Strategy

### Core Architecture
We'll implement a Python-based solution using mem0, Pydantic, and LangGraph that integrates seamlessly with the Next.js frontend:

```python
# Memory System Implementation Overview
from mem0 import Memory
from pydantic import BaseModel, Field
```

### User Authentication & Session Management
The system uses Supabase Auth to handle user authentication, supporting:
- Email/password authentication
- Google OAuth integration
- Session persistence with refresh tokens
- Role-based access control
- User profile management

This enables personalized experiences while tracking user preferences and history across sessions.

### Military Skills Translation System
A specialized module for veterans:
- Translates Military Occupational Specialty (MOS) codes to civilian equivalents
- Maps military leadership experience to management opportunities
- Identifies technical skills transferable to clean energy sectors
- Considers military-specific certifications and training
- Provides transition resources specifically for MA-based veterans

The system handles specialized military backgrounds with precision:
- Technical MOSs (e.g., 12P - Prime Power Production Specialist) → Civilian solar/grid technician roles
- Logistics specialists (e.g., 88M, 92F) → Clean transportation and supply chain management
- Infantry and combat roles → Safety management, team leadership, and quality control
- Military engineers → Renewable infrastructure construction and project management
- Communications specialists → Smart grid and IoT system management

Example Military Translation Pipeline:
1. Extract military background from resume
2. Identify MOS codes and training
3. Map to civilian equivalents using ML models
4. Prioritize clean energy matches
5. Generate personalized career pathways with identified skill gaps

The system integrates with veteran support programs in Massachusetts, including:
- Helmets to Hardhats for construction and renewable installation training
- MA Hire-Vets Medallion Program participants
- Veterans Clean Energy Job Placement Initiative
- VA benefits coordination for training program funding

### International Credential Evaluation
For international professionals, especially from Africa and other regions:
- Analyzes foreign degrees and certifications
- Provides US equivalency information
- Identifies credential gaps requiring additional certification
- Maps international experience to Massachusetts requirements
- Suggests credential validation services where needed

The system includes comprehensive support for African credentials:
- Nigeria: Engineering degrees from universities like University of Lagos or University of Ibadan
- Kenya: Technical certifications from institutions like Kenya Polytechnic University
- South Africa: Energy sector qualifications from University of Cape Town or University of Witwatersrand
- Ghana: Renewable energy programs from Kwame Nkrumah University
- Egypt: Engineering and technical programs from Cairo University and Alexandria University

For each credential type, the system provides:
- US academic equivalency (e.g., Bachelor of Engineering to ABET-accredited BS degree)
- Required supplemental certifications for Massachusetts licensure
- Bridge program recommendations to fill qualification gaps
- Connection to Massachusetts-based professional associations for international graduates
- Mentorship opportunities with professionals from similar backgrounds

The system supports skills recognition for newcomers in Massachusetts Gateway Cities, with special focus on engineering, technical, and scientific credentials relevant to clean energy sectors.

### Hybrid Search & Knowledge Retrieval
The system combines multiple information sources:
- Vector database with climate economy information
- Web search capability for recent/missing information
- MA-specific training program database
- ACT member company information
- Clean energy job boards data

Search pipeline:
1. Query mem0 vector database
2. If insufficient results, trigger web search
3. Filter for Massachusetts relevance
4. Rank by relevance to user profile and query
5. Blend results into personalized recommendations

### Tools System for Agents
A structured tools system enables agent capabilities:
- WebSearchTool - Find recent climate economy information
- DBRetrieverTool - Access local knowledge base
- ResumeAnalyzerTool - Parse and evaluate resumes
- SkillMapperTool - Map skills to jobs and training programs
- GatewayCityTool - Location-specific opportunities
- MilitaryTranslatorTool - Veteran skills translation
- CredentialEvaluatorTool - International credential validation
- JobMatcherTool - Connect users to opportunities

Each tool is modular, reusable, and integrated into the LangGraph workflow.

### Metrics & Monitoring
A comprehensive metrics system tracks:
- User interactions and satisfaction
- Query performance and latency
- Recommendation quality and acceptance
- System health and error rates
- Usage patterns by location and demographics

Implemented with:
- Event tracking for all user actions
- Performance monitoring for API endpoints
- Feedback collection on recommendations
- A/B testing for different recommendation approaches
- Dashboard visualizations for stakeholders

### Environmental Justice Integration
For residents of EJ communities:
- Prioritize local opportunities within commuting distance
- Identify training programs with support services
- Focus on programs with stipends or financial assistance
- Connect users with community-based organizations
- Track outcomes for continuous improvement

### Gateway Cities Focus
Location-specific personalization for:
- Brockton - Manufacturing and solar
- Boston - Cleantech innovation and green buildings
- Fall River/New Bedford - Offshore wind focus
- Lawrence/Lowell - Energy efficiency and weatherization
- Springfield - Clean transportation and EVs
- Worcester - Green construction and waste management

Each location has tailored resources and opportunities mapped to local economic development priorities.

### Clean Energy Sector Coverage
Specialized career pathways for key sectors:
- Renewable Energy - Solar, wind, geothermal, hydropower
- Energy Efficiency - Weatherization, green building, HVAC
- Clean Transportation - EVs, charging infrastructure, public transit
- Decarbonizing Buildings - Retrofits, heat pumps, smart systems
- Circular Economy - Waste reduction, recycling, materials innovation

### Real-time Streaming Updates
Socket.IO implementation for responsive UX:
- Token-by-token streaming of AI responses
- Progress indicators for long-running operations
- Real-time notifications for new opportunities
- Collaborative features for career counselors
- Resume analysis visualization during processing

## Technical Implementation

### Memory Service
```python
# climate_economy_ecosystem/lib/memory/mem0_service.py

from mem0 import Memory
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
import os
from datetime import datetime
import openai

class ClimateMemoryEntry(BaseModel):
    """Memory entry model for climate economy assistant"""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    category: str = "report"  # report, job, training, conversation, resume
    source: str = "manual"
    relevance_score: Optional[float] = None

class UserProfile(BaseModel):
    """User profile with resume data and preferences"""
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    is_ej_community: bool = False
    gateway_city: Optional[str] = None
    is_veteran: bool = False
    military_background: Optional[Dict[str, Any]] = None
    international_credentials: Optional[List[Dict[str, Any]]] = None
    resume_data: Optional[Dict[str, Any]] = None
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
```

### Agent Workflow
```python
# climate_economy_ecosystem/graph/climate_state.py

from typing import Dict, List, Optional, Any, TypedDict, Union
from pydantic import BaseModel

# State definition for climate assistant
class ClimateState(TypedDict):
    """State for climate assistant workflow"""
    user_query: str
    user_id: str
    context: List[Dict[str, Any]]
    retrieved_memories: List[Dict[str, Any]]
    report_insights: List[Dict[str, Any]]
    job_recommendations: List[Dict[str, Any]]
    training_paths: List[Dict[str, Any]]
    response: Optional[str]
    error: Optional[str]
    resume_text: Optional[str]
    resume_analysis: Optional[Dict[str, Any]]
    stream_tokens: Optional[bool]
    socket_id: Optional[str]
    is_ej_community: Optional[bool]
    is_veteran: Optional[bool]
    military_data: Optional[Dict[str, Any]]
    metrics: Dict[str, Any]
```

### Database Schema
```sql
-- Key database tables structure
CREATE TABLE climate_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    user_id TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles with military and international background
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,
    name TEXT,
    email TEXT,
    location TEXT,
    is_ej_community BOOLEAN DEFAULT FALSE,
    gateway_city TEXT,
    is_veteran BOOLEAN DEFAULT FALSE,
    military_background JSONB,
    international_credentials JSONB,
    preferences JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Events table for metrics tracking
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    properties JSONB DEFAULT '{}'::JSONB,
    session_id TEXT
);

-- Companies and job opportunities
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    career_page TEXT,
    location TEXT,
    sector TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE job_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT,
    salary_range TEXT,
    requirements JSONB,
    is_ej_friendly BOOLEAN DEFAULT FALSE,
    is_veteran_friendly BOOLEAN DEFAULT FALSE,
    is_international_friendly BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## System Architecture

```
┌───────────────┐      ┌─────────────────┐     ┌───────────────┐
│   Next.js UI  │      │  FastAPI Server  │     │  Supabase DB  │
│  (React app)  │◄────►│ (Python backend) │◄───►│ (PostgreSQL)  │
└───────┬───────┘      └────────┬─────────┘     └───────────────┘
        │                       │                       ▲
        │                       │                       │
        │                       ▼                       │
┌───────▼───────┐      ┌─────────────────┐     ┌───────▼───────┐
│   User Chat   │      │   LangGraph     │     │     mem0      │
│  Interface    │─────►│   Workflow      │◄────►│ Memory System │
└───────────────┘      └────────┬─────────┘     └───────────────┘
                                │                       ▲
                                │                       │
                                ▼                       │
                       ┌─────────────────┐     ┌───────▼───────┐
                       │  Agent Tools    │     │  Redis Cache  │
                       │ - DB Retriever  │◄────►│               │
                       │ - Web Search    │     └───────────────┘
                       │ - Resume Analyzer│            ▲
                       └───────┬─────────┘            │
                               │                      │
                               ▼                      │
                       ┌─────────────────┐    ┌───────▼───────┐
                       │  Metrics        │    │  Web Services │
                       │  Monitoring     │────►  (External)   │
                       └─────────────────┘    └───────────────┘
```

## Integration Points
- Next.js frontend with DaisyUI components
- Python backend with FastAPI
- LangGraph for agent orchestration
- Supabase for data and authentication
- Redis for caching and rate limiting
- Socket.IO for real-time updates

## Getting Started
To start developing:

1. Clone the repository
2. Install dependencies with `npm install` and `pip install -r requirements.txt`
3. Set up environment variables
4. Initialize Supabase tables
5. Run database migrations
6. Start the development server with `npm run dev`

## Deployment
The application is designed for deployment on Vercel with API functions connecting to Supabase.

## Implementation Plan
- **Phase 1**: Core memory system and user authentication
- **Phase 2**: Resume analysis and job matching
- **Phase 3**: Military skills translation and international credential evaluation
- **Phase 4**: Gateway Cities personalization and EJ communities integration
- **Phase 5**: Metrics tracking and system monitoring
- **Phase 6**: Polish UI/UX and performance optimization

The implementation provides a robust solution for veterans transitioning to civilian careers, international professionals with overseas credentials, and residents of Environmental Justice communities, all within the context of Massachusetts' clean energy economy.

## Recent Updates

### Phase 6: Hybrid Search & Real-time Features

We've recently enhanced the platform with improved search capabilities and real-time features:

#### Hybrid Search System
- Advanced search UI with filtering, history, and feedback mechanisms
- Combined search pipeline that merges database and web results
- Sophisticated ranking algorithms that balance relevance and recency
- Source attribution and category detection for better results

#### Real-time Streaming
- Token-by-token streaming responses for a more interactive experience
- Markdown support for formatted responses
- Source attribution for transparency
- Ability to cancel streaming mid-response

#### Performance Monitoring with LangSmith
- Integrated LangSmith tracing throughout the application
- Detailed step-by-step tracing of search and chat operations
- Performance analytics for API endpoints
- Error tracking and debugging capabilities

## Prerequisites

- Node.js 18+
- Python 3.9+
- Supabase account
- Astra DB account
- OpenAI API key
- LangSmith API key (for tracing)

## Environment Variables

Configure the following environment variables in your `.env` file:

```
# LLM Configuration
OPENAI_API_KEY=your-openai-api-key

# Database Configuration
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# LangSmith Tracing Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=your-project-name
LANGCHAIN_API_KEY=your-langsmith-api-key
```

## Installation

1. Clone the repository
   ```
   git clone https://github.com/your-username/climate-economy-ecosystem.git
   cd climate-economy-ecosystem
   ```

2. Install dependencies
   ```
   npm install
   pip install -r requirements.txt
   ```

3. Run the development server
   ```
   npm run dev
   ```

## Using the Hybrid Search

The hybrid search component provides a more powerful search experience:

```jsx
import HybridSearch from '@/components/Search/HybridSearch';

export default function SearchPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-4">
        Search Clean Energy Resources
      </h1>
      <HybridSearch />
    </div>
  );
}
```

## Using Streaming Responses

For chat interfaces that need real-time streaming:

```jsx
import StreamingResponse from '@/components/Chat/StreamingResponse';

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  
  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />
      
      <StreamingResponse
        query={query}
        showSources={true}
        onComplete={(response, sources) => {
          console.log('Chat completed:', response);
        }}
      />
    </div>
  );
}
```

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.