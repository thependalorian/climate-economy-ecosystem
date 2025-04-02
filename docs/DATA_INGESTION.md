# Climate Economy Ecosystem Data Ingestion Guide

This guide explains how to set up and run the data ingestion process for the Climate Economy Ecosystem project. The system uses Supabase for data storage and OpenAI for generating embeddings.

## Prerequisites

1. **Python Dependencies**
```bash
pip install httpx beautifulsoup4 openai python-dotenv
```

2. **Environment Variables**
Create or update `.env` file with:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
OPENAI_API_KEY=your_openai_key
```

## Supabase Setup

1. **Database Schema**
The system requires the following table in Supabase:

```sql
CREATE TABLE climate_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    user_id TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE climate_memories ENABLE ROW LEVEL SECURITY;

-- Create policy for reading
CREATE POLICY "Public climate memories are viewable by everyone."
    ON climate_memories FOR SELECT
    USING (true);

-- Create policy for inserting
CREATE POLICY "System can insert memories."
    ON climate_memories FOR INSERT
    WITH CHECK (user_id = 'system');
```

2. **Vector Extension**
Enable the vector extension in Supabase:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Running the Ingestion

1. **Test Single URL**
```bash
cd climate_economy_ecosystem/scripts
python unified_url_ingestion.py
```
This will test ingestion with a single URL (masscec.com).

2. **Monitor Progress**
```bash
tail -f url_ingestion.log
```

3. **Full Ingestion**
To run full ingestion with all URLs, modify `main()` in `unified_url_ingestion.py`:
```python
async def main():
    try:
        ingester = UnifiedURLIngester()
        
        # Primary URLs (Tier 1)
        primary_urls = [
            "https://www.masscec.com/",
            "https://www.greentownlabs.com/",
            "https://franklincummings.edu/",
            # Add more URLs as needed
        ]
        
        success_count = await ingester.process_url_list(primary_urls, tier=1)
        ingester.print_summary()
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        sys.exit(1)
```

## Features

1. **Smart Content Extraction**
- Preserves document structure (headings, lists, paragraphs)
- Handles both HTML and PDF content
- Intelligent text chunking with overlap

2. **Rate Limiting**
- URL requests: 1 request per 2 seconds
- Supabase API: 2 requests per second
- OpenAI API: Automatic rate limiting

3. **Content Processing**
- Maximum content size: 200KB
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Maximum chunks per document: 20

4. **URL Discovery**
- Tier 1: Primary URLs (explicitly provided)
- Tier 2: URLs discovered from Tier 1
- Tier 3: URLs discovered from Tier 2
- Domain-restricted crawling

## Monitoring and Maintenance

1. **Logging**
- Log file: `url_ingestion.log`
- Log level: INFO
- Includes timestamps and detailed error messages

2. **Progress Tracking**
- Total URLs processed
- Success/failure counts
- Success rate percentage
- URLs discovered and queued

3. **Error Handling**
- Connection timeouts
- Rate limit errors
- Content extraction failures
- Database insertion errors

## Troubleshooting

1. **Common Issues**
- **Environment Variables**: Ensure all required variables are set
- **Database Connection**: Check Supabase URL and key
- **OpenAI API**: Verify API key and quota
- **Rate Limits**: Adjust if encountering 429 errors

2. **Debugging**
```bash
# Check environment variables
env | grep SUPABASE
env | grep OPENAI

# Test database connection
curl -H "apikey: $SUPABASE_SERVICE_KEY" \
     -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
     "$SUPABASE_URL/rest/v1/climate_memories?select=count"

# Monitor real-time logs
tail -f url_ingestion.log
```

## Best Practices

1. **Rate Limiting**
- Don't modify rate limits unless necessary
- Consider target website's policies
- Monitor API usage and costs

2. **Content Processing**
- Review extracted content quality
- Adjust chunk sizes if needed
- Monitor embedding generation

3. **Database Management**
- Regularly check storage usage
- Monitor vector index performance
- Back up data periodically

4. **Testing**
- Start with single URL tests
- Monitor memory usage
- Check content quality
- Verify embeddings 