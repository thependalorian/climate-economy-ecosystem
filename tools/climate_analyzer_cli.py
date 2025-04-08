#!/usr/bin/env python3
"""
Climate Economy Ecosystem Analyzer CLI

A unified command-line interface for running various climate economy analysis tools.
"""

import os
import sys
import argparse
import asyncio
import logging
from typing import Dict, List, Any, Optional
import importlib.util
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('climate_analyzer.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Available tools definitions
AVAILABLE_TOOLS = {
    "content": {
        "module": "content_analyzer",
        "class": "ContentAnalyzer",
        "description": "Analyzes ingested content to extract insights and generate reports",
        "params": {
            "--limit": {
                "help": "Limit the number of memories to analyze",
                "type": int,
                "default": 5000
            },
            "--days": {
                "help": "Only analyze content from the last N days",
                "type": int,
                "default": 30
            },
            "--output": {
                "help": "Output file path for reports",
                "type": str,
                "default": "content_analysis_report.html"
            },
            "--wordcloud": {
                "help": "Output file path for word cloud",
                "type": str,
                "default": "climate_wordcloud.png"
            },
            "--clusters": {
                "help": "Number of content clusters to generate",
                "type": int,
                "default": 5
            }
        }
    },
    "relationships": {
        "module": "relationship_analyzer",
        "class": "RelationshipAnalyzer",
        "description": "Analyzes connections between climate organizations",
        "params": {
            "--limit": {
                "help": "Limit the number of memories to analyze",
                "type": int,
                "default": 5000
            },
            "--report": {
                "help": "Output file path for relationship report",
                "type": str,
                "default": "relationship_analysis_report.html"
            },
            "--network": {
                "help": "Output file path for network visualization",
                "type": str,
                "default": "organization_network.png"
            },
            "--similarity": {
                "help": "Output file path for similarity heatmap",
                "type": str,
                "default": "organization_similarity.png"
            }
        }
    },
    "ingest": {
        "module": "unified_url_ingestion",
        "description": "Ingests content from URLs into the climate economy ecosystem",
        "is_script": True,
        "params": {
            "--urls": {
                "help": "File containing URLs to ingest (one per line)",
                "type": str
            },
            "--tier": {
                "help": "Starting tier for URL ingestion (1, 2, or 3)",
                "type": int,
                "default": 1
            },
            "--limit": {
                "help": "Limit the number of URLs to process",
                "type": int
            }
        }
    },
    "search": {
        "module": "test_hybrid_search",
        "description": "Performs hybrid search on climate economy data using text and vector similarity",
        "is_script": True,
        "params": {
            "--query": {
                "help": "Query string to search for",
                "type": str
            },
            "--limit": {
                "help": "Limit the number of results to return",
                "type": int,
                "default": 10
            },
            "--text-weight": {
                "help": "Weight for text search results (0-1)",
                "type": float,
                "default": 0.6
            },
            "--vector-weight": {
                "help": "Weight for vector search results (0-1)",
                "type": float,
                "default": 0.4
            }
        }
    },
    "profile-enrich": {
        "module": "profile_enrichment",
        "description": "Enriches user profiles with extracted skills and information",
        "is_script": True,
        "params": {
            "--user-id": {
                "help": "User ID to enrich profile for",
                "type": str,
                "required": True
            },
            "--verify": {
                "help": "Whether to verify data before saving",
                "action": "store_true"
            },
            "--member-companies-only": {
                "help": "Only search for information from member companies",
                "action": "store_true"
            },
            "--output": {
                "help": "Output file path for enriched profile JSON",
                "type": str
            }
        }
    },
    "job-search": {
        "module": "enhanced_job_search",
        "description": "Performs enhanced job search using profile enrichment data",
        "is_script": True,
        "params": {
            "--user-id": {
                "help": "User ID to search jobs for",
                "type": str,
                "required": True
            },
            "--query": {
                "help": "Search query text",
                "type": str
            },
            "--location": {
                "help": "Comma-separated locations to search in",
                "type": str
            },
            "--skills": {
                "help": "Comma-separated skills to search for",
                "type": str
            },
            "--recommend": {
                "help": "Get job recommendations instead of search",
                "action": "store_true"
            },
            "--limit": {
                "help": "Limit the number of results",
                "type": int,
                "default": 10
            },
            "--output": {
                "help": "Output file path for results JSON",
                "type": str
            }
        }
    },
    "military-translate": {
        "module": "military_skill_translator",
        "description": "Translates military experience into civilian skills",
        "is_script": True,
        "params": {
            "--mos": {
                "help": "Military Occupational Specialty code or description",
                "type": str,
                "required": True
            },
            "--output": {
                "help": "Output file path for results JSON",
                "type": str
            }
        }
    },
    "credential-evaluate": {
        "module": "credential_evaluator",
        "description": "Evaluates international credentials for the US job market",
        "is_script": True,
        "params": {
            "--country": {
                "help": "Country where credential was obtained",
                "type": str,
                "required": True
            },
            "--credential": {
                "help": "Credential or degree title",
                "type": str,
                "required": True
            },
            "--field": {
                "help": "Field of study",
                "type": str
            },
            "--output": {
                "help": "Output file path for results JSON",
                "type": str
            }
        }
    },
    "resume-process": {
        "module": "resume_processor",
        "description": "Processes resume text to extract skills and experience",
        "is_script": True,
        "params": {
            "--file": {
                "help": "Resume file path",
                "type": str,
                "required": True
            },
            "--output": {
                "help": "Output file path for results JSON",
                "type": str
            }
        }
    },
    "gateway-analyze": {
        "module": "gateway_city_analyzer",
        "description": "Analyzes opportunities in Massachusetts Gateway Cities",
        "is_script": True,
        "params": {
            "--city": {
                "help": "Gateway City name",
                "type": str,
                "required": True
            },
            "--sector": {
                "help": "Clean energy sector to focus on",
                "type": str
            },
            "--output": {
                "help": "Output file path for results JSON",
                "type": str
            }
        }
    },
    "ej-support": {
        "module": "ej_support",
        "description": "Finds support programs for environmental justice communities",
        "is_script": True,
        "params": {
            "--location": {
                "help": "Location to check for EJ status",
                "type": str,
                "required": True
            },
            "--sector": {
                "help": "Clean energy sector to focus on",
                "type": str
            },
            "--output": {
                "help": "Output file path for results JSON",
                "type": str
            }
        }
    },
    "test": {
        "module": "test_supabase",
        "description": "Tests the Supabase connection and database setup",
        "is_script": True,
        "params": {}
    }
}

def get_tool_module_path(tool_name: str) -> Optional[str]:
    """Get the path to a tool module."""
    tool_info = AVAILABLE_TOOLS.get(tool_name)
    if not tool_info:
        return None
    
    # Check script directory
    script_dir = Path(__file__).parent
    module_name = tool_info["module"]
    
    # Check in the tools directory
    tool_path = script_dir / f"{module_name}.py"
    if tool_path.exists():
        return str(tool_path)
    
    # Check in parent script directory
    parent_script_dir = script_dir.parent / "scripts"
    if parent_script_dir.exists():
        tool_path = parent_script_dir / f"{module_name}.py"
        if tool_path.exists():
            return str(tool_path)
    
    # Check in scripts subdirectory
    scripts_dir = script_dir / "scripts"
    if scripts_dir.exists():
        tool_path = scripts_dir / f"{module_name}.py"
        if tool_path.exists():
            return str(tool_path)
    
    # Check in other common locations
    workspace_dir = Path(os.environ.get("WORKSPACE_DIR", "."))
    tool_path = workspace_dir / f"{module_name}.py"
    if tool_path.exists():
        return str(tool_path)
    
    return None

async def run_analysis_tool(tool_name: str, args: Dict[str, Any]) -> int:
    """Run the specified analysis tool."""
    tool_info = AVAILABLE_TOOLS.get(tool_name)
    if not tool_info:
        logger.error(f"Unknown tool: {tool_name}")
        return 1
    
    module_path = get_tool_module_path(tool_name)
    if not module_path:
        logger.error(f"Tool module not found: {tool_info['module']}")
        return 1
    
    try:
        logger.info(f"Loading module: {module_path}")
        
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(tool_info["module"], module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if tool_info.get("is_script", False):
            # For script-based tools, modify sys.argv and call the main function
            original_argv = sys.argv.copy()
            
            # Reconstruct command line arguments
            sys.argv = [module_path]
            for key, value in args.items():
                if value is not None:
                    # Skip None values (for optional arguments)
                    if isinstance(value, bool):
                        if value:
                            sys.argv.append(f"--{key}")
                    else:
                        sys.argv.append(f"--{key}")
                        sys.argv.append(str(value))
            
            # Call the main function
            if hasattr(module, "main"):
                if asyncio.iscoroutinefunction(module.main):
                    await module.main()
                else:
                    module.main()
            else:
                logger.error(f"Module {tool_info['module']} has no main function")
                return 1
            
            # Restore original argv
            sys.argv = original_argv
        else:
            # For class-based tools, instantiate the class and call methods
            class_name = tool_info["class"]
            if hasattr(module, class_name):
                # Instantiate the analyzer class
                analyzer_class = getattr(module, class_name)
                analyzer = analyzer_class()
                
                # Call fetch_memories with limit parameter if available
                if hasattr(analyzer, "fetch_memories"):
                    limit = args.get("limit", 5000)
                    days = args.get("days", 30)
                    
                    logger.info(f"Fetching memories (limit={limit}, days={days})...")
                    await analyzer.fetch_memories(limit=limit, days_back=days)
                
                # For content analyzer
                if tool_name == "content":
                    # Organize content and analyze
                    if hasattr(analyzer, "organize_by_source"):
                        logger.info("Organizing content by source...")
                        analyzer.organize_by_source()
                    
                    if hasattr(analyzer, "analyze_term_frequency"):
                        logger.info("Analyzing term frequency...")
                        analyzer.analyze_term_frequency()
                    
                    # Generate visualization
                    if hasattr(analyzer, "generate_wordcloud"):
                        wordcloud_path = args.get("wordcloud", "climate_wordcloud.png")
                        logger.info(f"Generating word cloud visualization at {wordcloud_path}...")
                        analyzer.generate_wordcloud(output_path=wordcloud_path)
                    
                    # Cluster content
                    if hasattr(analyzer, "cluster_content"):
                        clusters = args.get("clusters", 5)
                        logger.info(f"Clustering content into {clusters} groups...")
                        analyzer.cluster_content(n_clusters=clusters)
                    
                    # Generate report
                    if hasattr(analyzer, "generate_content_report"):
                        output_path = args.get("output", "content_analysis_report.html")
                        logger.info(f"Generating analysis report at {output_path}...")
                        analyzer.generate_content_report(output_path=output_path)
                    
                    # Generate insights with OpenAI
                    if hasattr(analyzer, "generate_summary_with_openai"):
                        logger.info("Generating insights with OpenAI...")
                        summary = await analyzer.generate_summary_with_openai()
                        
                        # Print summary
                        print("\n" + "="*80)
                        print("CLIMATE CONTENT ANALYSIS SUMMARY")
                        print("="*80)
                        print(summary)
                        print("="*80 + "\n")
                
                # For relationship analyzer
                elif tool_name == "relationships":
                    # Extract and analyze relationships
                    if hasattr(analyzer, "extract_organization_mentions"):
                        logger.info("Extracting organization mentions...")
                        analyzer.extract_organization_mentions()
                    
                    if hasattr(analyzer, "analyze_organization_relationships"):
                        logger.info("Analyzing organization relationships...")
                        analyzer.analyze_organization_relationships()
                    
                    if hasattr(analyzer, "generate_network_graph"):
                        logger.info("Generating network graph...")
                        analyzer.generate_network_graph()
                    
                    if hasattr(analyzer, "calculate_similarity_matrix"):
                        logger.info("Calculating organization similarity matrix...")
                        analyzer.calculate_similarity_matrix()
                    
                    # Generate visualizations and report
                    if hasattr(analyzer, "visualize_network"):
                        network_path = args.get("network", "organization_network.png")
                        logger.info(f"Visualizing organization network at {network_path}...")
                        analyzer.visualize_network(output_path=network_path)
                    
                    if hasattr(analyzer, "visualize_similarity_heatmap"):
                        similarity_path = args.get("similarity", "organization_similarity.png")
                        logger.info(f"Visualizing similarity heatmap at {similarity_path}...")
                        analyzer.visualize_similarity_heatmap(output_path=similarity_path)
                    
                    if hasattr(analyzer, "generate_relationship_report"):
                        report_path = args.get("report", "relationship_analysis_report.html")
                        logger.info(f"Generating relationship report at {report_path}...")
                        analyzer.generate_relationship_report(output_path=report_path)
                    
                    # Generate insights with OpenAI
                    if hasattr(analyzer, "generate_insights_with_openai"):
                        logger.info("Generating relationship insights with OpenAI...")
                        insights = await analyzer.generate_insights_with_openai()
                        
                        # Print insights
                        print("\n" + "="*80)
                        print("CLIMATE ORGANIZATION RELATIONSHIP INSIGHTS")
                        print("="*80)
                        print(insights)
                        print("="*80 + "\n")
            else:
                logger.error(f"Module {tool_info['module']} has no class {class_name}")
                return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"Error running tool {tool_name}: {str(e)}", exc_info=True)
        return 1

def setup_parser() -> argparse.ArgumentParser:
    """Set up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Climate Economy Ecosystem Analyzer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available tools:
  content       - Analyze ingested content to extract insights
  relationships - Analyze connections between climate organizations
  ingest        - Ingest content from URLs into the ecosystem
  search        - Perform hybrid search on climate economy data
  test          - Test the Supabase connection and database setup
        """
    )
    
    parser.add_argument(
        "tool",
        choices=AVAILABLE_TOOLS.keys(),
        help="The analysis tool to run"
    )
    
    # Add tool-specific arguments
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        for param_name, param_info in tool_info.get("params", {}).items():
            # Strip leading '--' for argument name
            arg_name = param_name.lstrip("-")
            parser.add_argument(
                param_name,
                dest=arg_name,
                help=param_info.get("help", ""),
                type=param_info.get("type", str),
                default=param_info.get("default", None)
            )
    
    return parser

async def main():
    """Main entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Convert args to dict
    args_dict = vars(args)
    tool_name = args_dict.pop("tool")
    
    # Run the selected tool
    try:
        exit_code = await run_analysis_tool(tool_name, args_dict)
        return exit_code
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 