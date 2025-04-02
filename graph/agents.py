from typing import Dict, List, Any, Optional, Annotated, TypedDict, Union
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import openai
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .climate_state import ClimateState, JobRecommendationConfig

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class JobRecommendationTools:
    """Tools for the job recommendation workflow"""
    
    @staticmethod
    async def search_jobs(state: ClimateState) -> ClimateState:
        """Search for relevant job opportunities"""
        config = state.get("job_config", {})
        
        # TODO: Implement actual job search using lib/tools/db_retriever.py
        # This is a placeholder implementation
        jobs = [
            {
                "id": "job-1",
                "title": "Solar Installation Technician",
                "company": "BrightSun Energy",
                "location": "Boston, MA",
                "description": "Install and maintain solar panel systems on residential and commercial properties.",
                "sector": "Solar Energy",
                "skills_required": ["Technical", "Physical", "Problem-solving"],
                "veteran_friendly": True,
                "ej_friendly": True,
                "salary_range": "$50,000 - $70,000"
            },
            {
                "id": "job-2",
                "title": "Wind Turbine Technician",
                "company": "Northeast Wind",
                "location": "New Bedford, MA",
                "description": "Maintain and repair wind turbines for offshore wind farms.",
                "sector": "Wind Energy",
                "skills_required": ["Technical", "Physical", "Safety"],
                "veteran_friendly": True,
                "ej_friendly": False,
                "salary_range": "$60,000 - $80,000"
            },
            {
                "id": "job-3",
                "title": "Energy Efficiency Consultant",
                "company": "GreenSave Solutions",
                "location": "Worcester, MA",
                "description": "Perform energy audits and recommend efficiency improvements for homes and businesses.",
                "sector": "Energy Efficiency",
                "skills_required": ["Analytical", "Customer Service", "Technical"],
                "veteran_friendly": False,
                "ej_friendly": True,
                "salary_range": "$55,000 - $75,000"
            }
        ]
        
        # Filter jobs based on configuration
        filtered_jobs = []
        for job in jobs:
            # Location filter
            if config.get("location_preference") and config["location_preference"] not in job["location"]:
                continue
                
            # Veteran friendly filter
            if config.get("is_veteran") and not job["veteran_friendly"]:
                continue
                
            # EJ friendly filter
            if config.get("is_ej_community") and not job["ej_friendly"]:
                continue
                
            # Skills filter
            if config.get("skills"):
                skills_matched = False
                for skill in config["skills"]:
                    if skill in job["skills_required"]:
                        skills_matched = True
                        break
                if not skills_matched:
                    continue
                    
            filtered_jobs.append(job)
        
        # Add jobs to state
        state["job_recommendations"] = filtered_jobs
        return state
    
    @staticmethod
    async def analyze_skills_fit(state: ClimateState) -> ClimateState:
        """Analyze skills fit for recommended jobs"""
        jobs = state.get("job_recommendations", [])
        skills = state.get("job_config", {}).get("skills", [])
        
        if not jobs or not skills:
            return state
            
        # Calculate skills match percentage for each job
        for job in jobs:
            matching_skills = [skill for skill in skills if skill in job["skills_required"]]
            job["skills_match_percentage"] = len(matching_skills) / len(job["skills_required"]) * 100
            job["matching_skills"] = matching_skills
            job["missing_skills"] = [skill for skill in job["skills_required"] if skill not in skills]
            
        # Sort jobs by skills match
        jobs.sort(key=lambda x: x["skills_match_percentage"], reverse=True)
        
        # Update state
        state["job_recommendations"] = jobs
        return state
    
    @staticmethod
    async def generate_recommendations_report(state: ClimateState) -> ClimateState:
        """Generate a report based on job recommendations"""
        jobs = state.get("job_recommendations", [])
        resume_analysis = state.get("resume_analysis", {})
        
        if not jobs:
            state["report_insights"] = [{
                "type": "no_jobs",
                "message": "No matching jobs found. Try broadening your search criteria."
            }]
            return state
            
        # Generate insights based on job matches
        insights = []
        
        # Best match insight
        if jobs:
            best_match = jobs[0]
            insights.append({
                "type": "best_match",
                "job_id": best_match["id"],
                "title": best_match["title"],
                "company": best_match["company"],
                "match_percentage": best_match.get("skills_match_percentage", 0),
                "message": f"Your best match is {best_match['title']} at {best_match['company']}."
            })
        
        # Skills gaps insight
        missing_skills = {}
        for job in jobs[:3]:  # Top 3 jobs
            for skill in job.get("missing_skills", []):
                if skill in missing_skills:
                    missing_skills[skill] += 1
                else:
                    missing_skills[skill] = 1
                    
        if missing_skills:
            insights.append({
                "type": "skills_gaps",
                "skills": sorted(missing_skills.items(), key=lambda x: x[1], reverse=True),
                "message": f"Consider developing these skills: {', '.join(list(missing_skills.keys())[:3])}"
            })
            
        # Location insight
        locations = {}
        for job in jobs:
            location = job["location"].split(",")[0].strip()
            if location in locations:
                locations[location] += 1
            else:
                locations[location] = 1
                
        if locations:
            top_location = max(locations.items(), key=lambda x: x[1])[0]
            insights.append({
                "type": "location",
                "locations": sorted(locations.items(), key=lambda x: x[1], reverse=True),
                "message": f"Most opportunities are in {top_location}."
            })
            
        # Update state
        state["report_insights"] = insights
        return state

def initialize_job_recommendation_graph() -> StateGraph:
    """Initialize the job recommendation workflow graph"""
    
    # Define the workflow
    workflow = StateGraph(ClimateState)
    
    # Add nodes for each step
    workflow.add_node("search_jobs", JobRecommendationTools.search_jobs)
    workflow.add_node("analyze_skills_fit", JobRecommendationTools.analyze_skills_fit)
    workflow.add_node("generate_recommendations_report", JobRecommendationTools.generate_recommendations_report)
    
    # Define edges
    workflow.add_edge("search_jobs", "analyze_skills_fit")
    workflow.add_edge("analyze_skills_fit", "generate_recommendations_report")
    workflow.add_edge("generate_recommendations_report", END)
    
    # Set the entry point
    workflow.set_entry_point("search_jobs")
    
    return workflow

async def run_job_recommendation(config: JobRecommendationConfig) -> Dict[str, Any]:
    """Run the job recommendation workflow with the given configuration"""
    # Initialize the graph
    graph = initialize_job_recommendation_graph()
    
    # Compile the graph
    app = graph.compile()
    
    # Initialize state
    initial_state: ClimateState = {
        "user_id": config.user_id,
        "job_config": config.dict(),
        "user_query": "Find me job recommendations",
        "context": [],
        "retrieved_memories": [],
        "report_insights": [],
        "job_recommendations": [],
        "training_paths": [],
        "response": None,
        "error": None,
        "resume_text": None,
        "resume_analysis": None,
        "stream_tokens": False,
        "socket_id": None,
        "is_ej_community": config.is_ej_community,
        "is_veteran": config.is_veteran,
        "military_data": None,
        "metrics": {}
    }
    
    # Run the graph
    result = await app.ainvoke(initial_state)
    
    # Extract relevant information from result
    return {
        "job_recommendations": result.get("job_recommendations", []),
        "insights": result.get("report_insights", [])
    }
