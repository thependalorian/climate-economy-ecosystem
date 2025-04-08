# Admin Metrics API

This API provides access to aggregated metrics data for the Climate Economy Ecosystem platform. It retrieves and processes metrics related to user profiles, profile enrichment, job searches, and skill verifications.

## Endpoint

```
GET /api/admin/metrics
```

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timeRange | string | No | Time range for metrics data. Valid values: `7d` (default), `30d`, `90d` |

## Response Format

```json
{
  "overview": {
    "totalUsers": 123,
    "enrichedProfiles": 85,
    "recentEnrichments": 12,
    "recentSearches": 47
  },
  "profileEnrichment": {
    "dates": ["4/1", "4/2", "4/3", "..."],
    "counts": [5, 7, 3, "..."],
    "verificationCounts": [4, 6, 2, "..."]
  },
  "jobSearch": {
    "dates": ["4/1", "4/2", "4/3", "..."],
    "searchCounts": [15, 22, 18, "..."],
    "recommendationCounts": [8, 12, 10, "..."]
  },
  "skillsDistribution": {
    "technical": 234,
    "transferable": 156,
    "soft": 89,
    "topSkills": [
      { "name": "Solar Panel Installation", "count": 45, "category": "technical" },
      { "name": "Project Management", "count": 38, "category": "transferable" },
      "..."
    ]
  },
  "topSearchTerms": [
    { "term": "solar", "count": 78 },
    { "term": "wind engineer", "count": 45 },
    "..."
  ],
  "profileStats": {
    "avgSkillsPerProfile": 12.3,
    "verificationRate": 87.5,
    "modificationRate": 34.2
  },
  "searchStats": {
    "avgResultsPerSearch": 8.7,
    "profileDataUsageRate": 73.2,
    "recommendationClickRate": 28.6
  }
}
```

## Data Definitions

### Overview

- `totalUsers`: Total number of users registered in the system
- `enrichedProfiles`: Number of users with completed profile enrichment
- `recentEnrichments`: Number of profile enrichments within the selected time range
- `recentSearches`: Number of job searches within the selected time range

### Profile Enrichment

- `dates`: Array of date labels formatted as MM/DD
- `counts`: Array of daily profile enrichment counts
- `verificationCounts`: Array of daily skill verification counts

### Job Search

- `dates`: Array of date labels formatted as MM/DD
- `searchCounts`: Array of daily job search counts
- `recommendationCounts`: Array of daily recommendation interaction counts

### Skills Distribution

- `technical`: Total count of technical skills across all users
- `transferable`: Total count of transferable skills across all users
- `soft`: Total count of soft skills across all users
- `topSkills`: Array of most frequently occurring skills with counts and categories

### Top Search Terms

- Array of search terms sorted by frequency

### Profile Stats

- `avgSkillsPerProfile`: Average number of skills per enriched profile
- `verificationRate`: Percentage of enrichment processes followed by verification
- `modificationRate`: Percentage of verifications that resulted in skill modifications

### Search Stats

- `avgResultsPerSearch`: Average number of results returned per search
- `profileDataUsageRate`: Percentage of searches that leveraged profile data
- `recommendationClickRate`: Percentage of displayed recommendations that were clicked

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 500 | Internal server error or database query failure |

## Example Usage

```javascript
// Example fetch request
const response = await fetch('/api/admin/metrics?timeRange=30d');
const metricsData = await response.json();

// Process and display the metrics data
console.log('Total users:', metricsData.overview.totalUsers);
console.log('Recent job searches:', metricsData.overview.recentSearches);
```

## Access Control

This API is restricted to users with admin role permissions. Unauthorized requests will be redirected to the login page or home page, depending on authentication status.

## Related Components

- `AdminMetricsDashboard.jsx`: Frontend component that consumes this API
- `admin/metrics/page.jsx`: Admin dashboard page that renders the metrics dashboard 