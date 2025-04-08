# Consolidated Services for Climate Economy Ecosystem

This document outlines the consolidated services implemented for the Climate Economy Ecosystem platform, focusing on real-time data processing and proper error handling without mock data fallbacks.

## Table of Contents

1. [Memory Service](#memory-service)
2. [Redis Service](#redis-service)
3. [LangSmith Tracing Service](#langsmith-tracing-service)
4. [Integration with Agents](#integration-with-agents)
5. [Error Handling Strategy](#error-handling-strategy)
6. [Required Resources from Ecosystem Partners](#required-resources-from-ecosystem-partners)

## Memory Service

The Memory Service provides persistent storage for conversations, user profiles, and other data using Mem0.

### Key Features

- Real-time memory storage and retrieval
- User profile management
- Resume analysis storage
- Comprehensive error handling without mock fallbacks
- Support for Environmental Justice communities and international professionals

### Implementation

```python
from lib.memory.memory_service import MemoryService, ClimateMemoryEntry, UserProfile, MemoryServiceError

# Initialize memory service
memory_service = MemoryService()

try:
    # Store a memory
    memory_entry = ClimateMemoryEntry(
        content="Solar installation jobs are growing rapidly in Massachusetts.",
        user_id="user123",
        category="job_market"
    )
    memory_id = await memory_service.add_memory(memory_entry)

    # Retrieve memories
    memories = await memory_service.search_memories(
        query="solar jobs",
        user_id="user123",
        limit=5
    )

    # Get user profile
    profile = await memory_service.get_user_profile("user123")
    
except MemoryServiceError as e:
    # Handle error appropriately
    logger.error(f"Memory service error: {str(e)}")
    # Inform the user or retry with different parameters
```

### Error Handling

The Memory Service uses a robust error handling approach:

1. **Service Unavailability**: When Mem0 is unavailable, the system raises specific exceptions that can be caught and handled appropriately.
2. **Graceful Degradation**: The system informs the user of the issue and suggests alternatives.
3. **Retry Mechanisms**: For transient errors, the system can retry operations with exponential backoff.

## Redis Service

The Redis Service provides caching and pub/sub capabilities for the platform.

### Key Features

- Real-time caching of API responses and search results
- Pub/sub for real-time updates
- Comprehensive error handling without mock fallbacks
- Health check capabilities

### Implementation

```python
from lib.redis.redis_service import RedisService, RedisServiceError

# Initialize Redis service
redis_service = RedisService()

try:
    # Cache data
    await redis_service.set("user:123:recommendations", recommendations, 3600)

    # Get cached data
    cached_recommendations = await redis_service.get("user:123:recommendations")

    # Use cached function pattern
    results = await redis_service.cached(
        key="search:solar:boston",
        func=lambda: search_jobs("solar", "boston"),
        expiry_seconds=1800
    )
    
except RedisServiceError as e:
    # Handle error appropriately
    logger.error(f"Redis service error: {str(e)}")
    # Fall back to direct function call
    results = await search_jobs("solar", "boston")
```

### JavaScript Implementation

```javascript
import { redisCache } from '@/lib/redis/redis-client';

// Cache data with error handling
async function cacheUserRecommendations(userId, recommendations) {
  try {
    await redisCache.set(`user:${userId}:recommendations`, recommendations, 3600);
    return true;
  } catch (error) {
    console.error('Redis caching error:', error);
    // Continue without caching
    return false;
  }
}

// Get cached data with error handling
async function getUserRecommendations(userId) {
  try {
    // Try to get from cache
    const cachedData = await redisCache.get(`user:${userId}:recommendations`);
    if (cachedData) {
      return cachedData;
    }
    
    // If not in cache, fetch from database
    const recommendations = await fetchRecommendationsFromDB(userId);
    
    // Try to cache for next time
    try {
      await redisCache.set(`user:${userId}:recommendations`, recommendations, 3600);
    } catch (cacheError) {
      console.error('Redis caching error:', cacheError);
      // Continue without caching
    }
    
    return recommendations;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
}
```

### Error Handling

The Redis Service uses a robust error handling approach:

1. **Service Unavailability**: When Redis is unavailable, the system raises specific exceptions that can be caught and handled appropriately.
2. **Graceful Degradation**: The system falls back to direct function calls when caching is unavailable.
3. **Automatic Reconnection**: The Redis client automatically attempts to reconnect when the connection is lost.

## LangSmith Tracing Service

The LangSmith Tracing Service provides monitoring and debugging capabilities for LLM calls and chains.

### Key Features

- Detailed tracing of LLM calls and chains
- Performance monitoring and analytics
- Comprehensive error handling without mock fallbacks
- Health check capabilities

### Implementation

```python
from lib.tracing.langsmith_service import TracingService, TracingServiceError

# Initialize tracing service
tracing_service = TracingService()

try:
    # Create a trace
    run_id = tracing_service.create_run_id()
    with tracing_service.trace(
        name="get_job_recommendations",
        run_id=run_id,
        inputs={"user_id": "user123", "query": "solar installer"}
    ) as run:
        # Perform operations
        recommendations = get_job_recommendations("user123", "solar installer")
        
        # End trace with outputs
        run.end(outputs={"recommendations": recommendations})

    # Log an LLM call
    tracing_service.log_llm_call(
        model="gpt-4",
        prompt="Recommend solar jobs in Boston",
        completion="Here are some solar jobs in Boston...",
        run_id=run_id
    )
    
except TracingServiceError as e:
    # Handle error appropriately
    logger.error(f"Tracing service error: {str(e)}")
    # Continue without tracing
```

### JavaScript Implementation

```javascript
import { tracingService } from '@/lib/tracing/langsmith-client';

// Create a trace with error handling
async function getJobRecommendationsWithTracing(userId, query) {
  // Create a unique run ID
  const runId = tracingService.createRunId();
  
  // Create a tracer
  const tracer = tracingService.createTracer(runId, 'get_job_recommendations');
  
  try {
    // Start span
    const span = tracer.startSpan({
      name: 'get_job_recommendations',
      inputs: { userId, query },
      runType: 'chain'
    });
    
    // Perform operations
    const recommendations = await fetchJobRecommendations(userId, query);
    
    // End span with outputs
    span.end({
      outputs: { recommendations }
    });
    
    // End tracer
    tracer.end();
    
    return recommendations;
  } catch (error) {
    console.error('Error getting job recommendations:', error);
    
    // If tracer is available, record the error
    try {
      const errorSpan = tracer.startSpan({
        name: 'error',
        inputs: { error: error.message },
        runType: 'chain'
      });
      
      errorSpan.end();
      tracer.end();
    } catch (tracingError) {
      console.error('Error recording tracing:', tracingError);
    }
    
    throw error;
  }
}
```

### Error Handling

The LangSmith Tracing Service uses a robust error handling approach:

1. **Service Unavailability**: When LangSmith is unavailable, the system continues without tracing.
2. **Graceful Degradation**: Tracing errors don't affect the core functionality of the application.
3. **Error Recording**: When possible, errors are recorded in the tracing system for later analysis.

## Integration with Agents

The consolidated services are integrated with the agent architecture to provide a seamless experience.

### Example: Job Recommendation Agent

```python
from lib.memory.memory_service import MemoryService
from lib.redis.redis_service import RedisService
from lib.tracing.langsmith_service import TracingService
from graph.climate_state import ClimateState
from langgraph.graph import StateGraph

class JobRecommendationAgent:
    """Agent for job recommendations in the clean energy sector"""
    
    def __init__(self):
        """Initialize the agent"""
        self.memory_service = MemoryService()
        self.redis_service = RedisService()
        self.tracing_service = TracingService()
    
    def create_workflow(self) -> StateGraph:
        """Create the job recommendation workflow"""
        # Define the workflow
        workflow = StateGraph(ClimateState)
        
        # Add nodes for each step
        workflow.add_node("search_jobs", self._search_jobs)
        workflow.add_node("analyze_skills_fit", self._analyze_skills_fit)
        workflow.add_node("generate_recommendations_report", self._generate_recommendations_report)
        workflow.add_node("collect_feedback", self._collect_feedback)
        
        # Define edges
        workflow.add_edge("search_jobs", "analyze_skills_fit")
        workflow.add_edge("analyze_skills_fit", "generate_recommendations_report")
        workflow.add_edge("generate_recommendations_report", "collect_feedback")
        
        # Set the entry point
        workflow.set_entry_point("search_jobs")
        
        return workflow
    
    async def run(self, state: ClimateState) -> ClimateState:
        """Run the job recommendation workflow"""
        run_id = self.tracing_service.create_run_id()
        
        try:
            with self.tracing_service.trace(
                name="job_recommendation_agent",
                run_id=run_id,
                inputs={"user_id": state["user_id"], "query": state["user_query"]}
            ) as run:
                # Create the workflow
                graph = self.create_workflow()
                
                # Compile the graph
                app = graph.compile()
                
                # Run the graph
                result = await app.ainvoke(state)
                
                # End trace with outputs
                run.end(outputs={"result": result})
                
                return result
                
        except Exception as e:
            logger.error(f"Error running job recommendation agent: {str(e)}")
            
            # Update state with error
            state["error"] = f"Error running job recommendation agent: {str(e)}"
            
            return state
    
    async def _search_jobs(self, state: ClimateState) -> ClimateState:
        """Search for relevant job opportunities"""
        try:
            # Try to get cached results
            cache_key = f"jobs:search:{state['user_id']}:{state['user_query']}"
            
            # Use cached function pattern
            job_results = await self.redis_service.cached(
                key=cache_key,
                func=lambda: self._perform_job_search(state),
                expiry_seconds=1800
            )
            
            # Update state with results
            state["job_recommendations"] = job_results
            
            return state
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            
            # Try direct search without caching
            try:
                job_results = await self._perform_job_search(state)
                state["job_recommendations"] = job_results
            except Exception as search_error:
                logger.error(f"Error performing direct job search: {str(search_error)}")
                state["error"] = f"Error searching jobs: {str(search_error)}"
                state["job_recommendations"] = []
            
            return state
    
    async def _perform_job_search(self, state: ClimateState) -> List[Dict[str, Any]]:
        """Perform the actual job search"""
        # Implementation details...
        pass
```

## Error Handling Strategy

The consolidated services use a comprehensive error handling strategy:

1. **Specific Error Types**: Each service defines specific error types that provide detailed information about the error.
2. **Graceful Degradation**: When a service is unavailable, the system continues with reduced functionality.
3. **Retry Mechanisms**: For transient errors, the system can retry operations with exponential backoff.
4. **Error Reporting**: Errors are logged and reported for later analysis.
5. **User Feedback**: When appropriate, users are informed of errors and provided with alternatives.

### Example: Error Handling in API Route

```javascript
// app/api/assistant/chat/route.js
import { MemoryService } from '@/lib/memory/memory-service';
import { RedisCache } from '@/lib/redis/redis-client';
import { TracingService } from '@/lib/tracing/langsmith-client';

export async function POST(req) {
  const { query, userId } = await req.json();
  
  // Initialize services
  const memoryService = new MemoryService();
  const redisCache = new RedisCache();
  const tracingService = new TracingService();
  
  // Create a unique run ID for tracing
  const runId = tracingService.createRunId();
  
  try {
    // Try to get cached response
    const cacheKey = `chat:${userId}:${query}`;
    let response;
    
    try {
      response = await redisCache.get(cacheKey);
      if (response) {
        return new Response(JSON.stringify({ response, cached: true }));
      }
    } catch (cacheError) {
      console.error('Cache error:', cacheError);
      // Continue without caching
    }
    
    // Create a trace
    const tracer = tracingService.createTracer(runId, 'chat_response');
    
    try {
      // Get user profile
      let userProfile;
      try {
        userProfile = await memoryService.getUserProfile(userId);
      } catch (profileError) {
        console.error('Error getting user profile:', profileError);
        // Continue without profile
        userProfile = { userId };
      }
      
      // Generate response
      response = await generateChatResponse(query, userProfile, tracer);
      
      // Try to cache response
      try {
        await redisCache.set(cacheKey, response, 3600);
      } catch (cacheError) {
        console.error('Cache error:', cacheError);
        // Continue without caching
      }
      
      // End trace
      tracer.end();
      
      return new Response(JSON.stringify({ response }));
    } catch (error) {
      console.error('Error generating chat response:', error);
      
      // Record error in trace
      try {
        const errorSpan = tracer.startSpan({
          name: 'error',
          inputs: { error: error.message },
          runType: 'chain'
        });
        
        errorSpan.end();
        tracer.end();
      } catch (tracingError) {
        console.error('Error recording tracing:', tracingError);
      }
      
      // Return error response
      return new Response(
        JSON.stringify({
          error: 'Error generating response',
          message: error.message
        }),
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Unhandled error:', error);
    
    // Return error response
    return new Response(
      JSON.stringify({
        error: 'Unhandled error',
        message: error.message
      }),
      { status: 500 }
    );
  }
}
```

## Required Resources from Ecosystem Partners

To fully implement these consolidated services, we need the following resources from our ecosystem partners:

### TPS (The Partnership, Inc.)

1. **Gateway Cities Data**:
   - Comprehensive list of clean energy employers in Gateway Cities
   - Transportation accessibility data for each Gateway City
   - Community-based clean energy projects in Gateway Cities
   - Local workforce development programs with EJ focus

2. **Regulatory Documentation**:
   - Massachusetts-specific licensing requirements for clean energy occupations
   - Step-by-step guides for obtaining licenses in Massachusetts
   - Documentation of regulatory barriers for EJ communities

3. **Workplace Culture Insights**:
   - Massachusetts-specific workplace norms and expectations
   - Industry-specific communication patterns
   - Guidance for navigating workplace dynamics

### AfricanBN

1. **International Credential Mappings**:
   - Country-specific credential equivalencies for clean energy occupations
   - Documentation requirements by country of origin
   - Common credential evaluation challenges by country

2. **Cultural Context Guides**:
   - Country-specific cultural norms relevant to workplace integration
   - Communication style comparisons between origin countries and Massachusetts
   - Cultural adaptation strategies for professional settings

3. **Multilingual Resources**:
   - Clean energy terminology glossaries in multiple languages
   - Cultural nuances in technical terminology translation
   - Language-specific communication patterns for technical discussions

### Headlamp

1. **Interactive Map Components**:
   - Geospatial visualization components for EJ communities
   - Transportation overlay capabilities
   - Clean energy opportunity mapping tools
   - Mobile-responsive map interfaces

2. **Career Pathway Visualizations**:
   - Interactive career progression diagrams
   - Skill mapping visualization components
   - Timeline-based credential pathway tools

3. **Learning Interaction Components**:
   - Multilingual interface components
   - Accessibility-focused UI elements
   - Interactive assessment tools

These resources will be integrated into our consolidated services to provide a comprehensive and personalized experience for users of the Climate Economy Ecosystem platform.
