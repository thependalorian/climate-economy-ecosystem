# Climate Economy Ecosystem Metrics System

This document provides an overview of the metrics system implemented in the Climate Economy Ecosystem platform. The metrics system tracks user engagement, profile enrichment, job search activity, and system performance.

## Architecture Overview

The metrics system consists of the following components:

1. **Frontend Tracking**
   - JavaScript metrics service for client-side event tracking
   - React hook for easy integration with components
   - Integration with key user interaction points

2. **Backend Processing**
   - Python metrics service for data processing and aggregation
   - API endpoints for collecting and retrieving metrics data
   - Middleware for API performance tracking

3. **Data Storage**
   - Supabase database tables for persistent storage
   - JSON-based event storage for detailed event data

4. **Admin Dashboard**
   - Visualization interface using Chart.js
   - Filtering and time range selection
   - Exporting capabilities

## Key Metrics

### Profile Enrichment Metrics

- Profile enrichment count
- Skills verification rate
- Skills by category (technical, transferable, soft)
- Average skills per profile
- Modification rate during verification
- Top skills across user profiles

### Job Search Metrics

- Search volume
- Search query patterns
- Result counts
- Recommendation effectiveness
- Profile data usage rate
- Click-through rate

### System Performance Metrics

- API response times
- Error rates
- Endpoint popularity
- User satisfaction scores

## Database Schema

### metrics Table

```sql
CREATE TABLE metrics (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id),
    event_type TEXT NOT NULL, -- profile_enrichment, enhanced_job_search, skill_verification, etc.
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
```

### search_analytics Table

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

## API Endpoints

### Tracking Endpoints

#### Profile Enrichment
```
POST /api/metrics/profile-enrichment
```

Tracks profile enrichment events, including skill extraction and verification.

Request body:
```json
{
  "userId": "uuid",
  "enrichmentData": {
    "status": "completed",
    "skills": {
      "technical": ["solar installation", "electric vehicle charging"],
      "transferable": ["project management", "data analysis"],
      "soft": ["communication", "teamwork"]
    },
    "data_sources": [
      { "type": "resume", "query": null },
      { "type": "web", "query": "John Smith solar installation" }
    ],
    "is_verified": false
  }
}
```

#### Enhanced Job Search
```
POST /api/metrics/enhanced-job-search
```

Tracks job search events, including query parameters and results.

Request body:
```json
{
  "userId": "uuid",
  "searchData": {
    "query": "solar installation",
    "results": [...],
    "usedProfileData": true,
    "sectors": ["renewable energy", "construction"],
    "skills": ["solar panel installation", "electrical wiring"],
    "isRecommendation": false,
    "performance": {
      "durationMs": 350
    }
  }
}
```

#### Skill Verification
```
POST /api/metrics/skill-verification
```

Tracks skill verification events, including modifications made by users.

Request body:
```json
{
  "userId": "uuid",
  "verificationData": {
    "verifiedCount": 15,
    "addedCount": 3,
    "removedCount": 2,
    "categories": ["technical", "transferable", "soft"]
  }
}
```

### Admin Data Retrieval

#### Get Metrics
```
GET /api/admin/metrics?timeRange=30d
```

Retrieves aggregated metrics data for the admin dashboard. See [Admin Metrics API](/app/api/admin/metrics/README.md) for detailed documentation.

## JavaScript Metrics Service

The JavaScript metrics service (`lib/monitoring/metrics_service.js`) provides client-side tracking capabilities:

```javascript
// Example usage
import { metricsService } from '../lib/monitoring/metrics_service';

// Track profile enrichment
await metricsService.trackProfileEnrichment({
  status: 'completed',
  skills: { technical: ['solar installation'], ... },
  data_sources: [...],
  is_verified: true
});

// Track job search
await metricsService.trackEnhancedJobSearch({
  query: 'renewable energy jobs',
  results: [...],
  usedProfileData: true,
  sectors: ['solar', 'wind'],
  skills: ['project management']
});

// Track skill verification
await metricsService.trackSkillVerification({
  verifiedCount: 12,
  addedCount: 2,
  removedCount: 1,
  categories: ['technical', 'transferable', 'soft']
});
```

## Python Metrics Service

The Python metrics service (`lib/monitoring/metrics_service.py`) provides server-side processing and storage:

```python
from metrics_service import metrics_service

# Track profile enrichment
await metrics_service.track_profile_enrichment(
    user_id='user-uuid',
    enrichment_data={
        'status': 'completed',
        'skills': {...},
        'data_sources': [...],
        'is_verified': True
    }
)

# Track job search
await metrics_service.track_enhanced_job_search(
    user_id='user-uuid',
    search_data={
        'query': 'solar jobs',
        'results': [...],
        'used_profile_data': True,
        'sectors': ['renewable energy'],
        'skills': ['installation']
    }
)

# Track skill verification
await metrics_service.track_skill_verification(
    user_id='user-uuid',
    verification_data={
        'verified_count': 15,
        'added_count': 3,
        'removed_count': 2,
        'categories': ['technical', 'transferable', 'soft']
    }
)

# Get metrics summary
summary = await metrics_service.get_metrics_summary(
    metric_type='profile_enrichment',
    days=30
)
```

## React Hook

The `useMetrics` hook (`hooks/useMetrics.js`) simplifies metrics tracking in React components:

```javascript
import useMetrics from '../hooks/useMetrics';

function ProfileComponent() {
  const { trackProfileEnrichment, trackSkillVerification } = useMetrics();
  
  const handleEnrichment = async (data) => {
    // Process enrichment
    // ...
    
    // Track the event
    await trackProfileEnrichment({
      status: 'completed',
      skills: extractedSkills,
      data_sources: sources,
      is_verified: false
    });
  };
  
  return (
    // Component JSX
  );
}
```

## Admin Dashboard

The admin metrics dashboard (`components/AdminMetricsDashboard.jsx`) provides visualization of the collected metrics. It includes:

- Time range selection (7 days, 30 days, 90 days)
- Tab-based navigation (Overview, Profile Enrichment, Job Search)
- Chart visualizations (Line, Bar, Pie charts)
- Tabular data display
- Key statistics and metrics

## Performance Tracking

The metrics system also includes API performance tracking via middleware:

```javascript
// middleware.js
// Track API performance for metrics endpoints
if (pathname.startsWith('/api/')) {
  const startTime = Date.now();
  
  // After response processing
  const duration = Date.now() - startTime;
  metrics_service.track_api_performance(
    pathname,
    duration,
    statusCode,
    userId,
    queryParams
  );
}
```

## Implementation Guidelines

When adding new features to the platform, follow these guidelines to ensure proper metrics tracking:

1. **Define Event Types**: Clearly define what events should be tracked and what data should be captured.

2. **Use Appropriate Service Methods**: Use the existing metrics service methods when possible, or add new methods for unique tracking needs.

3. **Error Handling**: Always wrap metrics tracking in try/catch blocks to prevent tracking failures from affecting core functionality.

4. **User Privacy**: Only track necessary data and ensure user consent for tracking.

5. **Performance Impact**: Minimize the performance impact of metrics tracking by using asynchronous calls and efficient data structures.

6. **Documentation**: Document any new metrics tracking points added to the system.

## Troubleshooting

### Missing Metrics Data

If metrics are not appearing in the admin dashboard:

1. Check browser console for JavaScript errors
2. Verify that tracking calls are being made
3. Check server logs for Python service errors
4. Verify database connectivity and table structure

### Performance Issues

If metrics tracking is causing performance issues:

1. Optimize data payloads to reduce size
2. Consider batching multiple events together
3. Move more processing to asynchronous background tasks
4. Implement rate limiting for high-volume events

## Future Enhancements

Planned enhancements for the metrics system:

1. **Real-time Dashboard**: Add WebSocket support for real-time metrics updates
2. **Advanced Filtering**: Add more filtering options for metrics data
3. **Export Functionality**: Add ability to export metrics data as CSV/JSON
4. **Custom Alerts**: Configure alerts based on metric thresholds
5. **User-specific Metrics**: Allow users to view their own engagement metrics 