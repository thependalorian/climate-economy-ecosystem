# Climate Economy Ecosystem Tools

This directory contains a collection of tools for ingesting, analyzing, and visualizing climate economy data within the ecosystem.

## Available Tools

### Content Analysis

The `content_analyzer.py` tool analyzes ingested content to extract insights, generate visualizations, and create comprehensive reports.

Features:
- Term frequency analysis
- Word cloud generation
- Content clustering
- Organization-specific content analysis
- HTML report generation
- AI-powered summary generation

### Relationship Analysis

The `relationship_analyzer.py` tool analyzes connections and relationships between different climate organizations based on co-mentions in the ingested content.

Features:
- Organization mention extraction
- Relationship strength calculation
- Network graph visualization
- Similarity matrix calculation
- HTML report generation
- AI-powered relationship insights

### URL Ingestion

The `unified_url_ingestion.py` script (in the `scripts` directory) ingests content from URLs into the climate economy ecosystem.

Features:
- Multi-tier URL crawling
- Smart content chunking
- Organization type detection
- Specialized handling for different content types (HTML, PDF, JS-heavy sites)
- Vector embedding generation

### Hybrid Search Testing

The `test_hybrid_search.py` script (in the `scripts` directory) tests and demonstrates hybrid search capabilities that combine text-based search with vector similarity search.

Features:
- Text-based search via Supabase
- Vector similarity search using OpenAI embeddings
- Score combination and result ranking
- Configurable weighting between search methods
- Multiple query testing

### Supabase Testing

The `test_supabase.py` script (in the `scripts` directory) tests the Supabase connection and database setup.

## Utility Modules

### Vector Search Client

The `vector_search.py` utility provides functionality for generating embeddings and performing vector similarity search using OpenAI's embedding models.

Features:
- Embedding generation with OpenAI API
- Cosine similarity calculation
- Bulk embedding generation
- Mock embedding generation for testing
- Similarity ranking and sorting

### Data Processing

The `data_processing.py` utility provides functions for processing and cleaning text data.

Features:
- Text cleaning and normalization
- Lemmatization and stemming
- Climate keyword extraction
- Term frequency calculation
- Organization name extraction

### Supabase Client

The `supabase_client.py` utility provides functions for interacting with Supabase.

Features:
- Connection testing
- Memory and organization fetching
- Text-based search
- Analysis result storage

## Usage

### CLI Tool

The `climate_analyzer_cli.py` provides a unified command-line interface for running all the tools.

```bash
# Install dependencies
pip install -r requirements.txt

# Run content analysis
python climate_analyzer_cli.py content --limit 5000 --days 30

# Run relationship analysis
python climate_analyzer_cli.py relationships --limit 5000

# Run URL ingestion
python climate_analyzer_cli.py ingest --urls urls.txt --tier 1

# Run hybrid search
python climate_analyzer_cli.py search --query "renewable energy" --limit 20

# Test Supabase connection
python climate_analyzer_cli.py test
```

### Command-Line Arguments

#### Content Analysis
- `--limit`: Limit the number of memories to analyze (default: 5000)
- `--days`: Only analyze content from the last N days (default: 30)
- `--output`: Output file path for reports (default: content_analysis_report.html)
- `--wordcloud`: Output file path for word cloud (default: climate_wordcloud.png)
- `--clusters`: Number of content clusters to generate (default: 5)

#### Relationship Analysis
- `--limit`: Limit the number of memories to analyze (default: 5000)
- `--report`: Output file path for relationship report (default: relationship_analysis_report.html)
- `--network`: Output file path for network visualization (default: organization_network.png)
- `--similarity`: Output file path for similarity heatmap (default: organization_similarity.png)

#### URL Ingestion
- `--urls`: File containing URLs to ingest (one per line)
- `--tier`: Starting tier for URL ingestion (1, 2, or 3) (default: 1)
- `--limit`: Limit the number of URLs to process

#### Hybrid Search
- `--query`: Query string to search for
- `--limit`: Limit the number of results to return (default: 10)
- `--text-weight`: Weight for text search results (0-1) (default: 0.6)
- `--vector-weight`: Weight for vector search results (0-1) (default: 0.4)
- `--test`: Run test with multiple predefined queries

## Dependencies

The tools require several Python packages, which can be installed with:

```bash
pip install -r requirements.txt
```

## Output Files

Analysis tools generate several output files:

- **HTML Reports**: Comprehensive analysis reports with visualizations and insights
- **Visualizations**: Word clouds, network graphs, and similarity heatmaps
- **Log Files**: Detailed logs of the analysis process

## Integration with Supabase

All tools integrate with Supabase for data storage and retrieval. Make sure your `.env` file contains the necessary Supabase configuration:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## OpenAI Integration

Some analysis tools use OpenAI for generating insights and embeddings. Make sure your `.env` file contains the necessary OpenAI configuration:

```
OPENAI_API_KEY=your_openai_api_key
``` 