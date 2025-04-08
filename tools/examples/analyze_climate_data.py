#!/usr/bin/env python3
"""
Example script demonstrating how to use the climate analysis tools programmatically.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to path so we can import the tools
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the analysis tools
from content_analyzer import ContentAnalyzer
from relationship_analyzer import RelationshipAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("example_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("climate_economy_example")

# Load environment variables
load_dotenv()

async def run_content_analysis():
    """Run a content analysis on ingested climate data."""
    logger.info("Starting content analysis...")
    
    # Initialize the content analyzer
    content_analyzer = ContentAnalyzer()
    
    # Fetch memories from Supabase
    memories = await content_analyzer.fetch_memories(limit=1000)
    logger.info(f"Fetched {len(memories)} memories for analysis")
    
    # Organize content by source
    source_data = content_analyzer.organize_by_source(memories)
    logger.info(f"Organized content by {len(source_data)} sources")
    
    # Analyze term frequency
    term_data = content_analyzer.analyze_term_frequency(memories)
    logger.info(f"Analyzed term frequency - found {len(term_data['most_common'])} common terms")
    
    # Generate a word cloud
    wordcloud_path = "example_wordcloud.png"
    content_analyzer.generate_wordcloud(term_data, output_path=wordcloud_path)
    logger.info(f"Generated word cloud at {wordcloud_path}")
    
    # Cluster content
    clusters = content_analyzer.cluster_content(memories, num_clusters=5)
    logger.info(f"Generated {len(clusters)} content clusters")
    
    # Analyze trends by organization
    org_trends = content_analyzer.trends_by_organization(memories)
    logger.info(f"Analyzed trends for {len(org_trends)} organizations")
    
    # Generate a summary with OpenAI
    summary = await content_analyzer.generate_summary_with_openai(
        term_data, 
        clusters, 
        org_trends
    )
    logger.info("Generated AI summary of content analysis")
    
    # Generate a content report
    report_path = "example_content_report.html"
    content_analyzer.generate_content_report(
        term_data,
        clusters,
        org_trends,
        summary,
        wordcloud_path,
        report_path
    )
    logger.info(f"Generated content analysis report at {report_path}")
    
    return report_path

async def run_relationship_analysis():
    """Run a relationship analysis on ingested climate data."""
    logger.info("Starting relationship analysis...")
    
    # Initialize the relationship analyzer
    relationship_analyzer = RelationshipAnalyzer()
    
    # Fetch memories from Supabase
    memories = await relationship_analyzer.fetch_memories(limit=1000)
    logger.info(f"Fetched {len(memories)} memories for analysis")
    
    # Extract organization mentions
    mentions = relationship_analyzer.extract_organization_mentions(memories)
    logger.info(f"Extracted mentions for {len(mentions)} organizations")
    
    # Analyze organization relationships
    relationships = relationship_analyzer.analyze_organization_relationships(mentions)
    logger.info(f"Analyzed relationships between organizations")
    
    # Generate network graph
    graph = relationship_analyzer.generate_network_graph(relationships)
    logger.info(f"Generated network graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    
    # Calculate similarity matrix
    similarity_matrix = relationship_analyzer.calculate_similarity_matrix(mentions)
    logger.info(f"Calculated similarity matrix of size {similarity_matrix.shape}")
    
    # Visualize network
    network_path = "example_network.png"
    relationship_analyzer.visualize_network(graph, output_path=network_path)
    logger.info(f"Generated network visualization at {network_path}")
    
    # Visualize similarity heatmap
    heatmap_path = "example_similarity.png"
    relationship_analyzer.visualize_similarity_heatmap(similarity_matrix, mentions.keys(), output_path=heatmap_path)
    logger.info(f"Generated similarity heatmap at {heatmap_path}")
    
    # Identify key relationships
    key_relationships = relationship_analyzer.identify_key_relationships(relationships, top_n=10)
    logger.info(f"Identified {len(key_relationships)} key relationships")
    
    # Generate insights with OpenAI
    insights = await relationship_analyzer.generate_insights_with_openai(
        relationships,
        graph,
        key_relationships
    )
    logger.info("Generated AI insights on organization relationships")
    
    # Generate relationship report
    report_path = "example_relationship_report.html"
    relationship_analyzer.generate_relationship_report(
        relationships,
        key_relationships,
        insights,
        network_path,
        heatmap_path,
        report_path
    )
    logger.info(f"Generated relationship analysis report at {report_path}")
    
    return report_path

async def main():
    """Run both content and relationship analyses."""
    logger.info("Starting climate economy data analysis example")
    
    # Run content analysis
    content_report = await run_content_analysis()
    
    # Run relationship analysis
    relationship_report = await run_relationship_analysis()
    
    logger.info(f"Completed analyses. Reports available at:")
    logger.info(f"  - Content analysis: {content_report}")
    logger.info(f"  - Relationship analysis: {relationship_report}")
    
if __name__ == "__main__":
    asyncio.run(main()) 