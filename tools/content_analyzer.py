#!/usr/bin/env python3
"""
Content Analyzer for Climate Economy Ecosystem

This tool analyzes the stored climate economy content in Supabase,
identifying patterns, extracting key insights, and generating reports
on the ingested data.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import math
from urllib.parse import urlparse

import httpx
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('content_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are required")
    sys.exit(1)

# Initialize base headers
SUPABASE_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Initialize NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class ContentAnalyzer:
    """Analyzes ingested climate economy content in Supabase."""
    
    def __init__(self):
        """Initialize the content analyzer."""
        self.openai_client = OpenAI()
        self.stop_words = set(stopwords.words('english'))
        self.english_vocab = set(nltk.corpus.words.words())
        self.climate_memories = []
        self.organization_data = defaultdict(list)
        self.domain_data = defaultdict(list)
        self.term_frequencies = Counter()
        self.tfidf_matrix = None
        self.tfidf_features = None
        self.clusters = None
        
    async def fetch_memories(self, limit: int = 5000, days_back: int = 30) -> List[Dict[str, Any]]:
        """Fetch memories from the Supabase database."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{SUPABASE_URL}/rest/v1/climate_memories?select=*&limit={limit}&order=created_at.desc",
                    headers=SUPABASE_HEADERS
                )
                
                if response.status_code == 200:
                    memories = response.json()
                    logger.info(f"Successfully fetched {len(memories)} memories")
                    self.climate_memories = memories
                    return memories
                else:
                    logger.error(f"Failed to fetch memories: {response.status_code}")
                    return []
        
        except Exception as e:
            logger.error(f"Error fetching memories: {str(e)}")
            return []
    
    def organize_by_source(self) -> Dict[str, List[Dict[str, Any]]]:
        """Organize memories by source organization."""
        for memory in self.climate_memories:
            if 'metadata' in memory and 'url' in memory['metadata']:
                url = memory['metadata']['url']
                domain = urlparse(url).netloc
                
                # Categorize by domain
                self.domain_data[domain].append(memory)
                
                # Categorize by organization type
                org_type = self.identify_organization_type(domain)
                self.organization_data[org_type].append(memory)
        
        return {
            'by_domain': dict(self.domain_data),
            'by_organization': dict(self.organization_data)
        }
    
    def identify_organization_type(self, domain: str) -> str:
        """Identify organization type based on domain."""
        domain_lower = domain.lower()
        
        # Map common climate economy organization types
        if any(gov in domain_lower for gov in ['gov', 'masscec', 'masshire']):
            return 'government'
        elif any(edu in domain_lower for edu in ['edu', 'franklincummings']):
            return 'education'
        elif any(inno in domain_lower for inno in ['greentownlabs', 'joinact']):
            return 'innovation'
        elif any(serv in domain_lower for serv in ['tps-energy', 'ulem', 'myheadlamp', 'africanbn']):
            return 'service'
        else:
            return 'other'
    
    def analyze_term_frequency(self) -> Dict[str, Any]:
        """Analyze term frequency in content."""
        # Extract text from all memories
        all_text = " ".join([memory.get('content', '') for memory in self.climate_memories if memory.get('content')])
        
        # Tokenize and process text
        tokens = word_tokenize(all_text.lower())
        
        # Filter tokens
        filtered_tokens = [
            token for token in tokens 
            if token.isalpha() and 
            token not in self.stop_words and 
            len(token) > 2 and
            token in self.english_vocab
        ]
        
        # Calculate frequency distribution
        freq_dist = FreqDist(filtered_tokens)
        self.term_frequencies = freq_dist
        
        # Find most common climate-related terms
        climate_terms = [
            'climate', 'energy', 'renewable', 'solar', 'wind', 'carbon', 
            'emission', 'green', 'sustainable', 'efficiency', 'electric',
            'battery', 'recycling', 'conservation', 'clean', 'environment'
        ]
        
        climate_term_counts = {term: freq_dist[term] for term in climate_terms if term in freq_dist}
        
        return {
            'most_common_terms': dict(freq_dist.most_common(50)),
            'climate_term_counts': climate_term_counts,
            'total_unique_terms': len(freq_dist),
            'total_terms': sum(freq_dist.values())
        }
    
    def generate_wordcloud(self, output_path: str = 'climate_wordcloud.png') -> str:
        """Generate word cloud visualization of content."""
        if not self.term_frequencies:
            self.analyze_term_frequency()
        
        # Create wordcloud
        wordcloud = WordCloud(
            width=1200, 
            height=800, 
            background_color='white',
            max_words=200,
            colormap='viridis',
            contour_width=1
        ).generate_from_frequencies(self.term_frequencies)
        
        # Save to file
        plt.figure(figsize=(16, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(output_path, format='png', dpi=300)
        plt.close()
        
        logger.info(f"Word cloud saved to {output_path}")
        return output_path
    
    def cluster_content(self, n_clusters: int = 5) -> Dict[str, Any]:
        """Cluster content based on TF-IDF vectors."""
        # Create document corpus
        documents = [memory.get('content', '') for memory in self.climate_memories if memory.get('content')]
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.85,
            stop_words='english'
        )
        
        tfidf_matrix = vectorizer.fit_transform(documents)
        self.tfidf_matrix = tfidf_matrix
        self.tfidf_features = vectorizer.get_feature_names_out()
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(tfidf_matrix)
        self.clusters = kmeans.labels_
        
        # Extract top terms per cluster
        cluster_terms = {}
        order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
        
        for cluster in range(n_clusters):
            terms = [self.tfidf_features[ind] for ind in order_centroids[cluster, :10]]
            cluster_terms[f"Cluster {cluster}"] = terms
        
        # Assign clusters to documents
        cluster_docs = defaultdict(list)
        for i, label in enumerate(self.clusters):
            if i < len(self.climate_memories):
                url = self.climate_memories[i].get('metadata', {}).get('url', 'unknown')
                cluster_docs[f"Cluster {label}"].append(url)
        
        return {
            'cluster_terms': cluster_terms,
            'cluster_docs': dict(cluster_docs),
            'num_clusters': n_clusters
        }
    
    def trends_by_organization(self) -> Dict[str, Any]:
        """Analyze content trends by organization type."""
        org_trends = {}
        
        for org_type, memories in self.organization_data.items():
            if not memories:
                continue
                
            # Extract content
            org_content = " ".join([memory.get('content', '') for memory in memories if memory.get('content')])
            
            # Tokenize and process
            tokens = word_tokenize(org_content.lower())
            filtered_tokens = [
                token for token in tokens 
                if token.isalpha() and 
                token not in self.stop_words and 
                len(token) > 2
            ]
            
            # Calculate frequency
            freq_dist = FreqDist(filtered_tokens)
            
            # Extract top terms
            org_trends[org_type] = {
                'top_terms': dict(freq_dist.most_common(20)),
                'document_count': len(memories),
                'average_length': sum(len(m.get('content', '')) for m in memories) / len(memories) if memories else 0
            }
        
        return org_trends
    
    async def generate_summary_with_openai(self) -> str:
        """Generate a summary of the content analysis using OpenAI."""
        try:
            # Prepare the analysis data
            analysis_data = {
                'term_frequency': self.analyze_term_frequency(),
                'organization_trends': self.trends_by_organization(),
                'source_distribution': {
                    'organization_types': {k: len(v) for k, v in self.organization_data.items()},
                    'top_domains': {k: len(v) for k, v in sorted(self.domain_data.items(), key=lambda x: len(x[1]), reverse=True)[:10]}
                }
            }
            
            # Create prompt
            prompt = f"""
            Please analyze this climate economy ecosystem data and provide a concise summary of key insights:
            
            {json.dumps(analysis_data, indent=2)}
            
            Focus on:
            1. Main topics and themes across the content
            2. Differences between organization types
            3. Most significant climate economy topics
            4. Potential gaps or areas needing more content
            5. Recommendations for future content ingestion
            """
            
            # Generate summary with OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a climate economy data analyst providing concise, insightful summaries of content analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            return "Error generating summary. Please check logs for details."
    
    def generate_content_report(self, output_path: str = 'content_analysis_report.html') -> str:
        """Generate a comprehensive HTML report."""
        try:
            # Create basic HTML structure
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Climate Economy Content Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                    h1, h2, h3 {{ color: #2c5282; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .stats-card {{ background: #f9f9f9; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
                    .term-cloud {{ text-align: center; margin: 30px 0; }}
                    .term-cloud img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #2c5282; color: white; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .org-section {{ margin-top: 40px; }}
                    .timestamp {{ color: #888; font-style: italic; margin-top: 40px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Climate Economy Content Analysis Report</h1>
                    <p class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
            
            # Add overall statistics
            term_freq_data = self.analyze_term_frequency()
            source_data = self.organize_by_source()
            
            html_content += f"""
                    <div class="stats-card">
                        <h2>Content Overview</h2>
                        <div class="stats-grid">
                            <div>
                                <h3>Document Statistics</h3>
                                <p>Total Documents: {len(self.climate_memories)}</p>
                                <p>Unique Sources: {len(self.domain_data)}</p>
                                <p>Organization Types: {len(self.organization_data)}</p>
                            </div>
                            <div>
                                <h3>Content Statistics</h3>
                                <p>Unique Terms: {term_freq_data['total_unique_terms']}</p>
                                <p>Total Term Count: {term_freq_data['total_terms']}</p>
                            </div>
                        </div>
                    </div>
            """
            
            # Add term frequency analysis
            html_content += """
                    <div class="stats-card">
                        <h2>Term Frequency Analysis</h2>
                        <table>
                            <tr>
                                <th>Term</th>
                                <th>Frequency</th>
                            </tr>
            """
            
            for term, count in list(term_freq_data['most_common_terms'].items())[:30]:
                html_content += f"""
                            <tr>
                                <td>{term}</td>
                                <td>{count}</td>
                            </tr>
                """
            
            html_content += """
                        </table>
                    </div>
            """
            
            # Add climate terms section
            html_content += """
                    <div class="stats-card">
                        <h2>Climate-Related Terms</h2>
                        <table>
                            <tr>
                                <th>Term</th>
                                <th>Frequency</th>
                            </tr>
            """
            
            for term, count in sorted(term_freq_data['climate_term_counts'].items(), key=lambda x: x[1], reverse=True):
                html_content += f"""
                            <tr>
                                <td>{term}</td>
                                <td>{count}</td>
                            </tr>
                """
            
            html_content += """
                        </table>
                    </div>
            """
            
            # Add organization analysis
            org_trends = self.trends_by_organization()
            
            html_content += """
                    <div class="org-section">
                        <h2>Organization Analysis</h2>
            """
            
            for org_type, data in org_trends.items():
                html_content += f"""
                        <div class="stats-card">
                            <h3>{org_type.capitalize()}</h3>
                            <p>Documents: {data['document_count']}</p>
                            <p>Average Length: {int(data['average_length'])} characters</p>
                            
                            <h4>Top Terms</h4>
                            <table>
                                <tr>
                                    <th>Term</th>
                                    <th>Frequency</th>
                                </tr>
                """
                
                for term, count in list(data['top_terms'].items())[:15]:
                    html_content += f"""
                                <tr>
                                    <td>{term}</td>
                                    <td>{count}</td>
                                </tr>
                    """
                
                html_content += """
                            </table>
                        </div>
                """
            
            html_content += """
                    </div>
            """
            
            # Add source distribution
            html_content += """
                    <div class="stats-card">
                        <h2>Source Distribution</h2>
                        <table>
                            <tr>
                                <th>Domain</th>
                                <th>Documents</th>
                            </tr>
            """
            
            for domain, memories in sorted(self.domain_data.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
                html_content += f"""
                            <tr>
                                <td>{domain}</td>
                                <td>{len(memories)}</td>
                            </tr>
                """
            
            html_content += """
                        </table>
                    </div>
            """
            
            # Add word cloud image if available
            wordcloud_path = 'climate_wordcloud.png'
            if os.path.exists(wordcloud_path):
                html_content += f"""
                    <div class="term-cloud">
                        <h2>Term Visualization</h2>
                        <img src="{wordcloud_path}" alt="Climate Economy Term Cloud">
                    </div>
                """
            
            # Close HTML
            html_content += """
                </div>
            </body>
            </html>
            """
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Content analysis report saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating content report: {str(e)}")
            return "Error generating report. Please check logs for details."

async def main():
    """Main entry point."""
    try:
        analyzer = ContentAnalyzer()
        
        # Fetch memories
        logger.info("Fetching memories from Supabase...")
        memories = await analyzer.fetch_memories()
        
        if not memories:
            logger.error("No memories found in database")
            sys.exit(1)
        
        # Organize by source
        logger.info("Organizing content by source...")
        analyzer.organize_by_source()
        
        # Analyze term frequency
        logger.info("Analyzing term frequency...")
        term_analysis = analyzer.analyze_term_frequency()
        
        # Generate word cloud
        logger.info("Generating word cloud visualization...")
        wordcloud_path = analyzer.generate_wordcloud()
        
        # Cluster content
        logger.info("Clustering content...")
        cluster_results = analyzer.cluster_content()
        
        # Analyze trends by organization
        logger.info("Analyzing trends by organization...")
        org_trends = analyzer.trends_by_organization()
        
        # Generate report
        logger.info("Generating content analysis report...")
        report_path = analyzer.generate_content_report()
        
        # Generate summary with OpenAI
        logger.info("Generating summary with OpenAI...")
        summary = await analyzer.generate_summary_with_openai()
        
        # Print summary to console
        print("\n" + "="*80)
        print("CLIMATE ECONOMY CONTENT ANALYSIS SUMMARY")
        print("="*80)
        print(summary)
        print("\n" + "="*80)
        print(f"Full report available at: {report_path}")
        print(f"Word cloud visualization: {wordcloud_path}")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 