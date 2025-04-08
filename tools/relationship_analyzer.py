#!/usr/bin/env python3
"""
Relationship Analyzer for Climate Economy Ecosystem

This tool analyzes connections and relationships between different climate organizations
based on co-mentions in the ingested content, creating visualizations of the
organizational network within the climate economy ecosystem.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse

import httpx
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client
import openai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('relationship_analysis.log')
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

# Climate organization dictionary
CLIMATE_ORGANIZATIONS = {
    # Government
    "masscec": {
        "full_name": "Massachusetts Clean Energy Center",
        "type": "government",
        "aliases": ["masscec", "massachusetts clean energy center", "mass clean energy"]
    },
    "masshire": {
        "full_name": "MassHire",
        "type": "government",
        "aliases": ["masshire", "mass hire", "career centers"]
    },
    
    # Education
    "franklincummings": {
        "full_name": "Franklin Cummings Tech",
        "type": "education",
        "aliases": ["franklin cummings", "bfit", "benjamin franklin institute", "franklin cummings tech"]
    },
    
    # Innovation
    "greentownlabs": {
        "full_name": "Greentown Labs",
        "type": "innovation",
        "aliases": ["greentown labs", "greentown", "green town"]
    },
    "joinact": {
        "full_name": "ACT - Action for Climate Tech",
        "type": "innovation",
        "aliases": ["act", "action for climate tech", "joinact"]
    },
    
    # Service
    "tps-energy": {
        "full_name": "TPS Energy",
        "type": "service",
        "aliases": ["tps energy", "tps", "thompson power systems"]
    },
    "ulem": {
        "full_name": "Urban League of Eastern Massachusetts",
        "type": "service",
        "aliases": ["ulem", "urban league", "urban league of eastern massachusetts"]
    },
    "myheadlamp": {
        "full_name": "MyHeadlamp",
        "type": "service",
        "aliases": ["myheadlamp", "headlamp", "my headlamp"]
    },
    "africanbn": {
        "full_name": "African Bridge Network",
        "type": "service",
        "aliases": ["africanbn", "african bridge network", "african bridge"]
    }
}

# Additional climate organizations that might be referenced
ADDITIONAL_ORGANIZATIONS = {
    "doe": {
        "full_name": "Department of Energy",
        "type": "government",
        "aliases": ["doe", "department of energy", "us department of energy", "u.s. department of energy"]
    },
    "epa": {
        "full_name": "Environmental Protection Agency",
        "type": "government",
        "aliases": ["epa", "environmental protection agency", "us epa", "u.s. epa"]
    },
    "mitos": {
        "full_name": "MIT Office of Sustainability",
        "type": "education",
        "aliases": ["mitos", "mit office of sustainability", "mit sustainability"]
    },
    "harvard": {
        "full_name": "Harvard University",
        "type": "education",
        "aliases": ["harvard", "harvard university", "harvard sustainability"]
    }
}

# Combine all organizations
ALL_ORGANIZATIONS = {**CLIMATE_ORGANIZATIONS, **ADDITIONAL_ORGANIZATIONS}

class RelationshipAnalyzer:
    """Analyzes relationships between climate organizations in content."""
    
    def __init__(self):
        """Initialize the relationship analyzer."""
        try:
            # Try to initialize the OpenAI client with the newer approach
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except TypeError:
            # Fall back to older client initialization
            try:
                openai.api_key = os.getenv("OPENAI_API_KEY")
                self.openai_client = openai
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.openai_client = None
        self.climate_memories = []
        self.organization_mentions = defaultdict(int)
        self.relationship_strength = defaultdict(lambda: defaultdict(int))
        self.document_org_mentions = []
        self.org_vectors = {}
        self.network_graph = None
        self.similarity_matrix = None
        
    async def fetch_memories(self, limit: int = 5000) -> List[Dict[str, Any]]:
        """Fetch memories from the Supabase database."""
        try:
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
    
    def extract_organization_mentions(self) -> Dict[str, int]:
        """Extract mentions of organizations from content."""
        # Reset counters
        self.organization_mentions = defaultdict(int)
        
        # Process each memory
        for memory in self.climate_memories:
            content = memory.get('content', '')
            if not content:
                continue
            
            # Convert to lowercase for case-insensitive matching
            content_lower = content.lower()
            
            # Track organizations mentioned in this document
            orgs_in_doc = set()
            
            # Check for organization mentions
            for org_id, org_info in ALL_ORGANIZATIONS.items():
                # Check each alias
                for alias in org_info["aliases"]:
                    if alias.lower() in content_lower:
                        self.organization_mentions[org_id] += 1
                        orgs_in_doc.add(org_id)
                        break
            
            # Store document-organization mentions for co-occurrence analysis
            if orgs_in_doc:
                self.document_org_mentions.append(orgs_in_doc)
        
        return dict(self.organization_mentions)
    
    def analyze_organization_relationships(self) -> Dict[str, Dict[str, int]]:
        """Analyze relationships between organizations based on co-mentions."""
        # Reset relationship strength
        self.relationship_strength = defaultdict(lambda: defaultdict(int))
        
        # Process co-mentions in documents
        for doc_orgs in self.document_org_mentions:
            # If at least 2 organizations are mentioned together
            if len(doc_orgs) >= 2:
                # Create links between all pairs of organizations
                for org1 in doc_orgs:
                    for org2 in doc_orgs:
                        if org1 != org2:
                            self.relationship_strength[org1][org2] += 1
        
        # Convert to regular dict for easier serialization
        result = {}
        for org1, relations in self.relationship_strength.items():
            result[org1] = dict(relations)
        
        return result
    
    def generate_network_graph(self) -> nx.Graph:
        """Generate a network graph of organization relationships."""
        # Create a new graph
        G = nx.Graph()
        
        # Add nodes for all mentioned organizations
        for org_id, count in self.organization_mentions.items():
            org_info = ALL_ORGANIZATIONS.get(org_id, {})
            G.add_node(
                org_id, 
                name=org_info.get('full_name', org_id),
                type=org_info.get('type', 'unknown'),
                mentions=count
            )
        
        # Add edges for relationships
        for org1, relations in self.relationship_strength.items():
            for org2, strength in relations.items():
                if strength > 0:
                    G.add_edge(org1, org2, weight=strength)
        
        self.network_graph = G
        return G
    
    def calculate_similarity_matrix(self) -> np.ndarray:
        """Calculate similarity matrix between organizations based on co-occurrence patterns."""
        orgs = list(self.organization_mentions.keys())
        n_orgs = len(orgs)
        
        # Create org->index mapping
        org_to_idx = {org: i for i, org in enumerate(orgs)}
        
        # Create matrix
        matrix = np.zeros((n_orgs, n_orgs))
        
        # Fill matrix with relationship strengths
        for org1, relations in self.relationship_strength.items():
            if org1 in org_to_idx:
                i = org_to_idx[org1]
                for org2, strength in relations.items():
                    if org2 in org_to_idx:
                        j = org_to_idx[org2]
                        matrix[i, j] = strength
        
        # Create similarity matrix using cosine similarity
        similarity = cosine_similarity(matrix)
        
        self.similarity_matrix = pd.DataFrame(
            similarity,
            index=orgs,
            columns=orgs
        )
        
        return similarity
    
    def visualize_network(self, output_path: str = 'organization_network.png') -> str:
        """Visualize the organization network."""
        if not self.network_graph:
            self.generate_network_graph()
        
        G = self.network_graph
        
        # Set up plot
        plt.figure(figsize=(16, 12))
        
        # Define node colors by organization type
        color_map = {
            'government': 'red',
            'education': 'blue',
            'innovation': 'green',
            'service': 'purple',
            'unknown': 'gray'
        }
        
        node_colors = [color_map.get(G.nodes[node]['type'], 'gray') for node in G.nodes()]
        
        # Node size based on mentions (scaled)
        node_sizes = [100 + (G.nodes[node]['mentions'] * 20) for node in G.nodes()]
        
        # Edge width based on relationship strength
        edge_widths = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]
        
        # Define layout
        pos = nx.spring_layout(G, k=0.5, seed=42)
        
        # Draw network
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                          markerfacecolor=color, markersize=10, label=org_type)
                  for org_type, color in color_map.items()]
        
        plt.legend(handles=legend_elements, title="Organization Types")
        
        # Remove axes
        plt.axis('off')
        
        # Add title
        plt.title('Climate Economy Organization Network', size=20)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Network visualization saved to {output_path}")
        return output_path
    
    def visualize_similarity_heatmap(self, output_path: str = 'organization_similarity.png') -> str:
        """Visualize organization similarity as a heatmap."""
        if self.similarity_matrix is None:
            self.calculate_similarity_matrix()
        
        # Create heatmap
        plt.figure(figsize=(14, 12))
        
        # Replace org IDs with full names
        labels = [ALL_ORGANIZATIONS.get(org, {}).get('full_name', org) for org in self.similarity_matrix.index]
        
        # Create heatmap
        ax = sns.heatmap(
            self.similarity_matrix, 
            annot=True, 
            cmap="YlGnBu", 
            linewidths=.5,
            xticklabels=labels,
            yticklabels=labels,
            vmin=0, 
            vmax=1
        )
        
        # Rotate x labels
        plt.xticks(rotation=45, ha='right')
        
        # Add title
        plt.title('Organization Similarity Matrix (based on co-mentions)', size=16)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Similarity heatmap saved to {output_path}")
        return output_path
    
    def identify_key_relationships(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Identify the strongest relationships between organizations."""
        # Collect all relationships
        all_relationships = []
        
        for org1, relations in self.relationship_strength.items():
            for org2, strength in relations.items():
                if strength > 0:
                    all_relationships.append({
                        'organization1': org1,
                        'organization1_name': ALL_ORGANIZATIONS.get(org1, {}).get('full_name', org1),
                        'organization2': org2,
                        'organization2_name': ALL_ORGANIZATIONS.get(org2, {}).get('full_name', org2),
                        'strength': strength
                    })
        
        # Sort by strength
        sorted_relationships = sorted(all_relationships, key=lambda x: x['strength'], reverse=True)
        
        # Return top N
        return sorted_relationships[:top_n]
    
    def generate_relationship_report(self, output_path: str = 'relationship_analysis_report.html') -> str:
        """Generate a comprehensive HTML report of organization relationships."""
        try:
            # Create basic HTML structure
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Climate Economy Organization Relationship Analysis</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                    h1, h2, h3 {{ color: #2c5282; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .stats-card {{ background: #f9f9f9; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
                    .network-viz {{ text-align: center; margin: 30px 0; }}
                    .network-viz img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #2c5282; color: white; }}
                    tr:hover {{ background-color: #f5f5f5; }}
                    .org-section {{ margin-top: 40px; }}
                    .timestamp {{ color: #888; font-style: italic; margin-top: 40px; }}
                    .org-type-government {{ color: #e53e3e; }}
                    .org-type-education {{ color: #3182ce; }}
                    .org-type-innovation {{ color: #38a169; }}
                    .org-type-service {{ color: #805ad5; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Climate Economy Organization Relationship Analysis</h1>
                    <p class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
            
            # Add organization mentions
            html_content += """
                    <div class="stats-card">
                        <h2>Organization Mentions</h2>
                        <table>
                            <tr>
                                <th>Organization</th>
                                <th>Type</th>
                                <th>Mentions</th>
                            </tr>
            """
            
            # Sort organizations by mention count
            sorted_orgs = sorted(
                [(org, count) for org, count in self.organization_mentions.items()],
                key=lambda x: x[1], 
                reverse=True
            )
            
            for org, count in sorted_orgs:
                org_info = ALL_ORGANIZATIONS.get(org, {})
                org_type = org_info.get('type', 'unknown')
                org_name = org_info.get('full_name', org)
                
                html_content += f"""
                            <tr>
                                <td>{org_name}</td>
                                <td class="org-type-{org_type}">{org_type.capitalize()}</td>
                                <td>{count}</td>
                            </tr>
                """
            
            html_content += """
                        </table>
                    </div>
            """
            
            # Add key relationships
            key_relationships = self.identify_key_relationships(top_n=15)
            
            html_content += """
                    <div class="stats-card">
                        <h2>Key Organization Relationships</h2>
                        <table>
                            <tr>
                                <th>Organization 1</th>
                                <th>Organization 2</th>
                                <th>Relationship Strength</th>
                            </tr>
            """
            
            for rel in key_relationships:
                html_content += f"""
                            <tr>
                                <td>{rel['organization1_name']}</td>
                                <td>{rel['organization2_name']}</td>
                                <td>{rel['strength']}</td>
                            </tr>
                """
            
            html_content += """
                        </table>
                    </div>
            """
            
            # Add network visualization if available
            network_path = 'organization_network.png'
            if os.path.exists(network_path):
                html_content += f"""
                    <div class="network-viz">
                        <h2>Organization Network Visualization</h2>
                        <img src="{network_path}" alt="Climate Economy Organization Network">
                    </div>
                """
            
            # Add similarity heatmap if available
            heatmap_path = 'organization_similarity.png'
            if os.path.exists(heatmap_path):
                html_content += f"""
                    <div class="network-viz">
                        <h2>Organization Similarity Heatmap</h2>
                        <img src="{heatmap_path}" alt="Organization Similarity Heatmap">
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
            
            logger.info(f"Relationship analysis report saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating relationship report: {str(e)}")
            return f"Error generating report: {str(e)}"
    
    async def generate_insights_with_openai(self) -> str:
        """Generate insights about organization relationships using OpenAI."""
        try:
            # Extract key information
            top_orgs = sorted(
                [(org, count) for org, count in self.organization_mentions.items()],
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            key_relationships = self.identify_key_relationships(top_n=10)
            
            analysis_data = {
                'top_organizations': [
                    {
                        'id': org,
                        'name': ALL_ORGANIZATIONS.get(org, {}).get('full_name', org),
                        'type': ALL_ORGANIZATIONS.get(org, {}).get('type', 'unknown'),
                        'mentions': count
                    } 
                    for org, count in top_orgs
                ],
                'key_relationships': key_relationships
            }
            
            # Create prompt
            prompt = f"""
            Please analyze these climate economy organization relationships and provide insights:
            
            {json.dumps(analysis_data, indent=2)}
            
            Focus on:
            1. Key hubs in the climate economy network
            2. Strongest relationships between organizations
            3. Patterns based on organization types (government, education, innovation, service)
            4. Potential collaboration opportunities
            5. Missing relationships that should be developed
            """
            
            # Generate insights with OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a climate economy relationship analyst providing insights on organizational networks."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating insights with OpenAI: {str(e)}")
            return f"Error generating insights: {str(e)}"

    def analyze_user_organization_connections(self, limit: int = 100) -> Dict[str, Any]:
        """
        Analyze connections between users and organizations based on 
        profile enrichment data and content analysis.
        
        Args:
            limit: Maximum number of users to analyze
            
        Returns:
            Dict with user-organization connection analysis
        """
        try:
            # Fetch enriched user profiles
            user_profiles = self._fetch_enriched_profiles(limit)
            
            # Fetch known organizations 
            organizations = self._get_organizations_list()
            
            # Map users to organizations
            user_org_connections = {}
            
            for user_id, profile in user_profiles.items():
                if not profile.get("enrichment"):
                    continue
                    
                # Extract text to scan for organization mentions
                scan_text = self._get_profile_scan_text(profile)
                
                # Find organization mentions
                user_orgs = {}
                for org_name in organizations:
                    # Simple match - could be improved with NLP/entity recognition
                    pattern = r'\b' + re.escape(org_name) + r'\b'
                    matches = re.findall(pattern, scan_text, re.IGNORECASE)
                    
                    if matches:
                        user_orgs[org_name] = len(matches)
                
                if user_orgs:
                    user_org_connections[user_id] = {
                        "user_name": profile.get("full_name", "Unknown User"),
                        "organizations": user_orgs,
                        "skill_count": len(self._extract_all_skills(profile)),
                        "connection_strength": len(user_orgs)
                    }
            
            # Analyze overall network
            network_stats = self._analyze_user_org_network(user_org_connections)
            
            return {
                "user_org_connections": user_org_connections,
                "network_stats": network_stats
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user-organization connections: {str(e)}")
            return {"error": str(e)}

    def _fetch_enriched_profiles(self, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch user profiles with enrichment data.
        
        Args:
            limit: Maximum number of profiles to fetch
            
        Returns:
            Dict of user profiles keyed by user_id
        """
        try:
            # Initialize Supabase client
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                logger.error("Missing Supabase credentials")
                return {}
                
            supabase = create_client(supabase_url, supabase_key)
            
            # Fetch profiles with enrichment data
            response = supabase.table("profiles") \
                .select("id, full_name, enrichment") \
                .not_.is_("enrichment", "null") \
                .limit(limit) \
                .execute()
                
            profiles = {}
            if hasattr(response, 'data'):
                for profile in response.data:
                    profiles[profile.get("id")] = profile
                    
            return profiles
            
        except Exception as e:
            logger.error(f"Error fetching enriched profiles: {str(e)}")
            return {}

    def _get_profile_scan_text(self, profile: Dict[str, Any]) -> str:
        """
        Extract text from profile to scan for organization mentions.
        
        Args:
            profile: User profile data
            
        Returns:
            Text to scan for organization mentions
        """
        text_components = []
        
        # Add basic profile info
        if profile.get("full_name"):
            text_components.append(profile.get("full_name"))
            
        if profile.get("bio"):
            text_components.append(profile.get("bio"))
            
        # Add experience info from enrichment
        if profile.get("enrichment") and profile["enrichment"].get("experience"):
            for exp in profile["enrichment"]["experience"]:
                if exp.get("company"):
                    text_components.append(exp.get("company"))
                if exp.get("description"):
                    text_components.append(exp.get("description"))
                    
        # Add education info from enrichment
        if profile.get("enrichment") and profile["enrichment"].get("education"):
            for edu in profile["enrichment"]["education"]:
                if edu.get("institution"):
                    text_components.append(edu.get("institution"))
                if edu.get("field"):
                    text_components.append(edu.get("field"))
                    
        return " ".join(text_components)

    def _extract_all_skills(self, profile: Dict[str, Any]) -> List[str]:
        """
        Extract all skills from a user profile.
        
        Args:
            profile: User profile data
            
        Returns:
            List of skills
        """
        all_skills = []
        
        if profile.get("enrichment") and profile["enrichment"].get("skills"):
            skills = profile["enrichment"]["skills"]
            
            # Add technical skills
            if skills.get("technical"):
                all_skills.extend(skills["technical"])
                
            # Add transferable skills
            if skills.get("transferable"):
                all_skills.extend(skills["transferable"])
                
            # Add soft skills
            if skills.get("soft"):
                all_skills.extend(skills["soft"])
                
        return all_skills

    def _analyze_user_org_network(self, user_org_connections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the user-organization network.
        
        Args:
            user_org_connections: User-organization connections data
            
        Returns:
            Dict with network statistics
        """
        # Count organizations and users
        all_orgs = set()
        for user_data in user_org_connections.values():
            all_orgs.update(user_data["organizations"].keys())
            
        total_users = len(user_org_connections)
        total_orgs = len(all_orgs)
        
        # Calculate organization popularity
        org_popularity = {}
        for user_data in user_org_connections.values():
            for org_name in user_data["organizations"].keys():
                org_popularity[org_name] = org_popularity.get(org_name, 0) + 1
                
        # Sort by popularity
        top_orgs = sorted(
            org_popularity.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Calculate network density
        max_connections = total_users * total_orgs
        actual_connections = sum(len(user_data["organizations"]) for user_data in user_org_connections.values())
        network_density = actual_connections / max_connections if max_connections > 0 else 0
        
        return {
            "total_users": total_users,
            "total_organizations": total_orgs,
            "top_organizations": top_orgs,
            "total_connections": actual_connections,
            "network_density": network_density
        }

async def main():
    """
    Main function to run the analysis.
    """
    analyzer = RelationshipAnalyzer()
    
    # Fetch memories
    logger.info("Fetching memories...")
    memories = await analyzer.fetch_memories(limit=1000)
    logger.info(f"Retrieved {len(memories)} memories")
    
    # Extract organization mentions
    logger.info("Extracting organization mentions...")
    org_mentions = analyzer.extract_organization_mentions()
    logger.info(f"Found {len(org_mentions)} organization mentions")
    
    # Analyze organization relationships
    logger.info("Analyzing organization relationships...")
    relationships = analyzer.analyze_organization_relationships()
    
    # Generate network graph
    logger.info("Generating network graph...")
    graph = analyzer.generate_network_graph()
    
    # Calculate similarity matrix
    logger.info("Calculating similarity matrix...")
    similarity = analyzer.calculate_similarity_matrix()
    
    # Visualize network
    logger.info("Visualizing network...")
    network_path = analyzer.visualize_network(output_path="example_network.png")
    logger.info(f"Network visualization saved to {network_path}")
    
    # Visualize similarity heatmap
    logger.info("Visualizing similarity heatmap...")
    heatmap_path = analyzer.visualize_similarity_heatmap(output_path="example_similarity.png")
    logger.info(f"Similarity heatmap saved to {heatmap_path}")
    
    # Identify key relationships
    logger.info("Identifying key relationships...")
    key_relationships = analyzer.identify_key_relationships()
    
    # Generate insights
    logger.info("Generating insights...")
    insights = await analyzer.generate_insights_with_openai()
    
    # Generate report
    logger.info("Generating relationship report...")
    report_path = analyzer.generate_relationship_report(output_path="example_relationship_report.html")
    logger.info(f"Relationship report saved to {report_path}")
    
    # Analyze user-organization connections
    logger.info("Analyzing user-organization connections...")
    user_org_analysis = analyzer.analyze_user_organization_connections()
    logger.info(f"Analyzed connections for {user_org_analysis.get('network_stats', {}).get('total_users', 0)} users")
    
    logger.info("Analysis complete")

if __name__ == "__main__":
    asyncio.run(main()) 