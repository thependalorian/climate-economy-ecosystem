import streamlit as st

# Page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="MA Clean Tech Ecosystem Assistant",
    page_icon="🌱",
    layout="wide"
)

import os
import sys
from datetime import datetime
import uuid
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
import asyncio
import json

# Add current directory to path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add tools directory to path
tools_dir = os.path.join(current_dir, 'tools')
if os.path.exists(tools_dir) and tools_dir not in sys.path:
    sys.path.append(tools_dir)

# Import utility functions - using fallback mechanisms if needed
try:
    from utils import (
        store_chat_message,
        get_user_metrics,
        get_user_distribution,
        get_recent_activity,
        process_resume,
        store_user_profile,
        get_job_matches,
        store_feedback
    )
except ImportError:
    # Fallback to utils from current directory
    try:
        sys.path.insert(0, current_dir)  # Prioritize current directory
        from utils import (
            store_chat_message,
            get_user_metrics,
            get_user_distribution,
            get_recent_activity,
            process_resume,
            store_user_profile,
            get_job_matches,
            store_feedback
        )
    except ImportError as e:
        st.error(f"Failed to import utility functions: {e}")
        raise

# Import tools modules - wrap in try/except to handle potential import errors
try:
    from tools.credential_evaluator import evaluate_credentials
    from tools.ej_support import analyze_ej_opportunities, is_ej_community
    from tools.job_search import search_jobs_for_user, get_company_job_listings
    from tools.gateway_city_analyzer import analyze_opportunities, is_gateway_city
    from tools.military_skill_translator import translate_military_to_civilian_skills
    from tools.resume_processor import process_resume as process_resume_file
    from tools.profile_enrichment import ProfileEnricher
except ImportError as e:
    st.warning(f"Some tools modules could not be imported: {e}")

# Import graph-based agents if LangGraph is available
try:
    from graph.agents import run_job_recommendation, JobRecommendationConfig
    from graph.climate_state import ClimateState
    langraph_available = True
except ImportError:
    langraph_available = False

# Add a simple mock for memory service
class MockMemoryService:
    """Mock memory service when mem0 is not available"""
    async def search_memories(self, query, user_id, limit=5, categories=None):
        return []
    
    async def add_memory(self, entry):
        return f"mock_memory_{hash(entry.content) % 10000}"
    
    async def get_memory_by_id(self, memory_id):
        return None
    
    async def delete_memory(self, memory_id):
        return True
    
    async def store_resume_analysis(self, user_id, resume_text, analysis):
        return f"mock_resume_{hash(resume_text) % 10000}"
    
    async def bulk_import_memories(self, entries):
        return [f"mock_memory_{i}" for i in range(len(entries))]
    
    async def get_user_profile(self, user_id):
        return None

# Import database and memory tools
try:
    # Since mem0 is not available, we'll skip the memory service
    memory_service = MockMemoryService()
    print("Using mock memory service - mem0 library not available")
except ImportError:
    memory_service = None

# Import ML-related tools
try:
    from lib.ml.feedback_processor import FeedbackProcessor
    from lib.ml.reward_model import ClimateRewardModel
    ml_tools_available = True
except ImportError:
    ml_tools_available = False

# Import prompts
try:
    from prompts.international_prompts import (
        CREDENTIAL_EVALUATION_SYSTEM_PROMPT,
        get_credential_equivalency_prompt
    )
    from prompts.military_prompts import (
        MILITARY_TRANSITION_SYSTEM_PROMPT,
        get_skill_translation_prompt
    )
except ImportError:
    st.warning("Could not import prompt modules")

# Import web search and DB tools
try:
    from lib.tools.web_search import WebSearchTool
    from lib.tools.db_retriever import DBRetrieverTool
    db_tools_available = True
except ImportError:
    db_tools_available = False

# Initialize profile enricher
try:
    profile_enricher = ProfileEnricher()
except NameError:
    profile_enricher = None

# Load environment variables
load_dotenv()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False
if "military_data" not in st.session_state:
    st.session_state.military_data = None
if "is_ej_community" not in st.session_state:
    st.session_state.is_ej_community = False
if "gateway_city" not in st.session_state:
    st.session_state.gateway_city = None
    
# Initialize async support
async def run_async(coroutine):
    """Run asynchronous function in Streamlit"""
    return await coroutine

# Helper to run async functions
def run_async_helper(coroutine):
    """Helper to run async functions in Streamlit"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coroutine)
    loop.close()
    return result

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["User Assessment", "Chat Assistant", "Job Search", "Training Programs", "Dashboard"])

def user_assessment_page():
    st.title("User Assessment")
    
    if not st.session_state.user_type:
        st.write("Welcome! Let's start by understanding your background.")
        user_type = st.selectbox(
            "What best describes you?",
            ["", "Veteran", "International Professional", "Career Transitioner", "Recent Graduate", "Environmental Justice Community Member", "Other"]
        )
        
        if user_type and user_type != "":
            st.session_state.user_type = user_type
            st.success(f"Profile type set to: {user_type}")
            st.rerun()
    
    if st.session_state.user_type and not st.session_state.profile_complete:
        st.write(f"Great! You've identified as a {st.session_state.user_type}.")
        
        # Additional questions based on user type
        if st.session_state.user_type == "Veteran":
            st.subheader("Military Experience")
            mos_code = st.text_input("What was your Military Occupational Specialty (MOS) code or title?")
            years_service = st.slider("Years of Service", min_value=1, max_value=30, value=4)
            branch = st.selectbox("Branch of Service", ["Army", "Navy", "Air Force", "Marines", "Coast Guard", "Space Force"])
            
            if mos_code and st.button("Translate Military Skills"):
                with st.spinner("Analyzing military skills..."):
                    # Use the military skill translator
                    military_data = translate_military_to_civilian_skills(mos_code)
                    st.session_state.military_data = military_data
                    
                    if military_data and "skills" in military_data:
                        st.subheader("Transferable Skills")
                        for skill in military_data["skills"]:
                            st.write(f"- {skill}")
                            
                        st.subheader("Potential Clean Energy Roles")
                        for role in military_data.get("clean_energy_roles", []):
                            st.write(f"- {role}")
                        
                        # Show additional guidance using military_prompts
                        st.subheader("Career Transition Guidance")
                        # Generate transition guidance using prompt
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                            
                            # Get prompt for military transition
                            prompt = get_skill_translation_prompt(
                                mos=mos_code,
                                branch=branch,
                                years_experience=years_service
                            )
                            
                            # Use OpenAI to generate guidance
                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": MILITARY_TRANSITION_SYSTEM_PROMPT},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.7,
                                max_tokens=500
                            )
                            
                            # Display the guidance
                            guidance = response.choices[0].message.content
                            st.write(guidance)
                            
                            # Store in session state for profile
                            if "military_guidance" not in st.session_state.military_data:
                                st.session_state.military_data["military_guidance"] = guidance
                        except Exception as e:
                            st.warning(f"Could not generate additional guidance: {str(e)}")
            
        elif st.session_state.user_type == "International Professional":
            st.subheader("International Credentials")
            country = st.text_input("Country where you obtained your credentials")
            credential = st.text_input("Degree/certification title")
            field = st.text_input("Field of study/expertise")
            
            if country and credential and field and st.button("Evaluate Credentials"):
                with st.spinner("Evaluating credentials..."):
                    # Use the credential evaluator
                    credential_data = evaluate_credentials(country, credential, field)
                    
                    if credential_data:
                        st.subheader("Credential Evaluation")
                        st.write(f"**US Equivalent:** {credential_data.get('us_equivalent', 'Unknown')}")
                        st.write(f"**Evaluation Notes:** {credential_data.get('evaluation_notes', '')}")
                        
                        st.subheader("Recommended Actions")
                        for action in credential_data.get("recommended_actions", []):
                            st.write(f"- {action}")
                            
                        st.subheader("Additional Training Needed")
                        for training in credential_data.get("additional_training_needed", []):
                            st.write(f"- {training}")
        
        elif st.session_state.user_type == "Environmental Justice Community Member":
            st.subheader("Environmental Justice Community")
            location = st.text_input("Which community do you live in?")
            
            if location and st.button("Analyze EJ Opportunities"):
                with st.spinner("Analyzing EJ opportunities..."):
                    # Check if it's an EJ community
                    is_ej = is_ej_community(location)
                    st.session_state.is_ej_community = is_ej
                    
                    if is_ej:
                        # Get EJ analysis
                        ej_data = analyze_ej_opportunities(location)
                        
                        st.success(f"{location} is recognized as an Environmental Justice community.")
                        
                        st.subheader("EJ-Specific Insights")
                        for insight in ej_data.get("ej_specific_insights", []):
                            st.write(f"- {insight}")
                            
                        st.subheader("Clean Energy Opportunity Areas")
                        for opportunity in ej_data.get("opportunity_areas", []):
                            st.write(f"- {opportunity}")
                    else:
                        st.warning(f"{location} is not recognized as an Environmental Justice community in our database.")
        
        # Resume upload for all user types
        st.subheader("Resume Analysis")
        uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
        
        if uploaded_file:
            with st.spinner("Analyzing your resume..."):
                file_type = uploaded_file.type.split('/')[-1]
                file_content = uploaded_file.read()
                
                # Process resume
                resume_data = process_resume(file_content, file_type)
                
                if resume_data:
                    st.subheader("Skills Identified")
                    for skill in resume_data.get("skills", [])[:10]:  # Show top 10 skills
                        st.write(f"- {skill}")
                    
                    # Also process using resume_processor for more detailed analysis
                    try:
                        # Save file temporarily to pass to resume_processor
                        temp_file_path = f"temp_resume_{st.session_state.user_id}.{file_type}"
                        with open(temp_file_path, "wb") as f:
                            f.write(file_content)
                        
                        # Get enhanced resume analysis
                        enhanced_resume_data = process_resume_file(temp_file_path)
                        
                        # Remove temp file
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                        
                        # Merge resume data with enhanced data
                        if enhanced_resume_data:
                            # Add summary if available
                            if "summary" in enhanced_resume_data and enhanced_resume_data["summary"]:
                                st.subheader("Professional Summary")
                                st.write(enhanced_resume_data["summary"])
                            
                            # Merge skills
                            if "skills" in enhanced_resume_data:
                                resume_data["skills"] = list(set(resume_data.get("skills", []) + enhanced_resume_data["skills"]))
                    except Exception as e:
                        st.warning(f"Enhanced resume processing unavailable: {str(e)}")
                    
                    # Create profile data with all collected information
                    profile_data = {
                        "user_type": st.session_state.user_type,
                        "resume_data": resume_data,
                        "created_at": datetime.utcnow().isoformat(),
                        "is_ej_community": st.session_state.is_ej_community,
                        "military_data": st.session_state.military_data
                    }
                    
                    # Enrich profile if possible
                    try:
                        if hasattr(profile_enricher, "enrich_user_profile"):
                            enriched_profile = run_async_helper(profile_enricher.enrich_user_profile({
                                "user_id": st.session_state.user_id,
                                **profile_data
                            }))
                            
                            if enriched_profile and "enrichment" in enriched_profile:
                                st.subheader("Additional Skills Identified")
                                
                                for skill_type, skills in enriched_profile["enrichment"]["skills"].items():
                                    if skills:
                                        st.write(f"**{skill_type.title()} Skills:**")
                                        skill_list = ", ".join(skills[:5])  # Show top 5 of each type
                                        st.write(skill_list)
                                
                                profile_data["enrichment"] = enriched_profile["enrichment"]
                    except Exception as e:
                        st.error(f"Error during profile enrichment: {str(e)}")
                    
                    # Store profile
                    if store_user_profile(st.session_state.user_id, profile_data):
                        st.session_state.profile_complete = True
                        st.success("Profile completed successfully! You can now use the Chat Assistant and Job Search features.")
                        
                        # Show a button to continue
                        if st.button("Continue to Chat Assistant"):
                            st.session_state.page = "Chat Assistant"
                            st.rerun()
                    else:
                        st.error("There was an error saving your profile. Please try again.")
                else:
                    st.error("Error processing resume. Please try a different file format.")
    
    if st.session_state.profile_complete:
        st.success("Profile complete! You can now use all features of the platform.")
        st.write("Use the sidebar to navigate to other sections.")
        
        # Show a summary of the profile
        st.subheader("Your Profile Summary")
        
        # Display appropriate information based on user type
        if st.session_state.user_type == "Veteran" and st.session_state.military_data:
            st.write("**Military Experience:**")
            st.write(f"MOS: {st.session_state.military_data.get('mos', 'Not specified')}")
            
            st.write("**Transferable Skills:**")
            skills = st.session_state.military_data.get("skills", [])
            for skill in skills[:5]:  # Show top 5 skills
                st.write(f"- {skill}")
        
        elif st.session_state.user_type == "Environmental Justice Community Member" and st.session_state.is_ej_community:
            st.write("**Environmental Justice Community Member**")
            st.write("You'll receive specialized recommendations for EJ community opportunities.")

def chat_assistant_page():
    st.title("Chat Assistant")
    
    if not st.session_state.profile_complete:
        st.warning("Please complete your profile assessment first.")
        st.write("Go to the User Assessment page to complete your profile.")
        return
    
    # Initialize reward model if available
    reward_model = None
    if ml_tools_available:
        try:
            reward_model = ClimateRewardModel()
        except Exception as e:
            st.sidebar.warning(f"Reward model not available: {str(e)}")
    
    st.write("Ask me anything about clean energy opportunities in Massachusetts!")
    
    # Display chat history
    for idx, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Add feedback buttons for assistant messages
            if message["role"] == "assistant" and "message_id" in message:
                feedback_id = f"feedback_{idx}"
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    if st.button("👍 Helpful", key=f"helpful_{feedback_id}"):
                        store_feedback(
                            st.session_state.user_id, 
                            message["message_id"], 
                            "positive", 
                            5
                        )
                        st.success("Thank you for your feedback!")
                
                with col2:
                    if st.button("👎 Not Helpful", key=f"not_helpful_{feedback_id}"):
                        store_feedback(
                            st.session_state.user_id, 
                            message["message_id"], 
                            "negative", 
                            1
                        )
                        st.info("Thank you for your feedback. We'll work on improving.")
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        user_message = {
            "role": "user", 
            "content": prompt,
            "timestamp": datetime.utcnow().isoformat()
        }
        st.session_state.chat_history.append(user_message)
        
        # Store user message
        stored_message = store_chat_message(st.session_state.user_id, "user", prompt)
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    # Check if we can use memory services
                    context = []
                    if memory_service:
                        # Search for relevant memories
                        memories = run_async_helper(memory_service.search_memories(
                            query=prompt,
                            user_id=st.session_state.user_id,
                            limit=5
                        ))
                        
                        if memories:
                            context = [memory.content for memory in memories]
                    
                    # Use graph-based agent if available
                    if langraph_available and st.session_state.user_type:
                        # Determine if this is a job recommendation query
                        if "job" in prompt.lower() or "career" in prompt.lower() or "work" in prompt.lower():
                            job_config = JobRecommendationConfig(
                                user_id=st.session_state.user_id,
                                is_veteran=(st.session_state.user_type == "Veteran"),
                                is_ej_community=st.session_state.is_ej_community
                            )
                            
                            # Run job recommendation workflow
                            try:
                                results = run_async_helper(run_job_recommendation(job_config))
                                
                                if results and "insights" in results:
                                    # Format the response
                                    response = "Based on your profile, here are some job recommendations:\n\n"
                                    
                                    # Add insights
                                    for insight in results["insights"]:
                                        if insight["type"] == "best_match" and "message" in insight:
                                            response += f"**{insight['message']}**\n\n"
                                        elif "message" in insight:
                                            response += f"{insight['message']}\n\n"
                                    
                                    # Add job details
                                    if "job_recommendations" in results and results["job_recommendations"]:
                                        response += "**Top Matches:**\n\n"
                                        for job in results["job_recommendations"][:3]:  # Top 3 jobs
                                            response += f"- {job['title']} at {job['company']} ({job['location']})\n"
                            except Exception as e:
                                response = f"I encountered an error while processing job recommendations: {str(e)}"
                        else:
                            # Generic response for now
                            response = "I understand you're interested in clean energy opportunities. Let me help you with that! As the Climate Economy Assistant, I can provide information about jobs, training, and resources in Massachusetts."
                    else:
                        # Generic response if graph agent not available
                        response = "I understand you're interested in clean energy opportunities. Let me help you with that! As the Climate Economy Assistant, I can provide information about jobs, training, and resources in Massachusetts."
                    
                    # Calculate expected reward score if model available
                    reward_score = None
                    if reward_model:
                        try:
                            reward_score = reward_model.compute_reward(prompt, response)
                            # Only show high-quality responses
                            if reward_score < 0.4:  # Threshold for acceptable quality
                                response = "I'm not confident I can provide a helpful response to that question. Could you provide more details or rephrase your question?"
                        except Exception as e:
                            st.sidebar.warning(f"Error calculating reward: {str(e)}")
                    
                    # Display the response
                    st.write(response)
                    
                    # Store assistant message
                    message_id = str(uuid.uuid4())
                    stored_message = store_chat_message(st.session_state.user_id, "assistant", response)
                    if stored_message and "id" in stored_message:
                        message_id = stored_message["id"]
                    
                    # Add to chat history
                    assistant_message = {
                        "role": "assistant", 
                        "content": response,
                        "message_id": message_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    st.session_state.chat_history.append(assistant_message)
                    
                    # Add feedback buttons for the new message
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("👍 Helpful"):
                            store_feedback(st.session_state.user_id, message_id, "positive", 5)
                            st.success("Thank you for your feedback!")
                    with col2:
                        if st.button("👎 Not Helpful"):
                            store_feedback(st.session_state.user_id, message_id, "negative", 1)
                            st.info("Thank you for your feedback. We'll work on improving.")
            except Exception as e:
                st.error(f"An error occurred while processing your request: {str(e)}")
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": "I apologize, but I encountered an error. Please try again."
                })

def job_search_page():
    st.title("Job Search")
    
    if not st.session_state.profile_complete:
        st.warning("Please complete your profile assessment first.")
        st.write("Go to the User Assessment page to complete your profile.")
        return
    
    st.write("Find clean energy job opportunities that match your profile.")
    
    # Add tab selection for search methods
    search_tabs = st.tabs(["Standard Search", "Enhanced Search"])
    
    with search_tabs[0]:
        # Filters
        with st.expander("Search Filters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                sector = st.selectbox("Sector", 
                    ["All", "Solar", "Wind", "Energy Efficiency", "Clean Transportation", 
                    "Battery Storage", "Green Building", "Climate Tech"], key="standard_sector")
                    
                location = st.selectbox("Location", 
                    ["All", "Boston", "Worcester", "Springfield", "Cambridge", "Lowell", 
                    "New Bedford", "Fall River", "Lawrence", "Holyoke"], key="standard_location")
            
            with col2:
                job_type = st.selectbox("Job Type", 
                    ["All", "Full-time", "Part-time", "Contract", "Internship", "Apprenticeship"], key="standard_job_type")
                    
                experience_level = st.selectbox("Experience Level",
                    ["All", "Entry Level", "Mid Level", "Senior Level", "Management", "Executive"], key="standard_exp")
        
            # Skills selection
            default_skills = []
            if st.session_state.user_type == "Veteran" and st.session_state.military_data:
                default_skills = st.session_state.military_data.get("skills", [])[:5]  # Top 5 military skills
                
            skills = st.multiselect("Skills", 
                ["Solar Installation", "Electrical", "HVAC", "Energy Auditing", "Project Management",
                "Customer Service", "Sales", "Engineering", "Design", "Technical Support",
                "Data Analysis", "Software Development", "Construction", "Mechanical", "Administrative"],
                default=default_skills, key="standard_skills")
        
        # Standard search button
        if st.button("Search Jobs", key="standard_search_btn"):
            with st.spinner("Searching for jobs..."):
                # Build filters
                filters = {
                    "sector": sector if sector != "All" else None,
                    "location": location if location != "All" else None,
                    "job_type": job_type if job_type != "All" else None,
                    "experience_level": experience_level if experience_level != "All" else None,
                    "skills": skills if skills else None
                }
                
                # Execute standard search
                jobs = get_job_matches(st.session_state.user_id, filters)
                
                # Display results
                display_job_results(jobs)
    
    with search_tabs[1]:
        st.write("Enhanced job search uses AI to find the best matches based on your profile and preferences.")
        
        # Enhanced search filters
        with st.expander("Search Criteria", expanded=True):
            search_text = st.text_input("Job Description or Keywords", key="enhanced_search_text")
            
            col1, col2 = st.columns(2)
            
            with col1:
                enhanced_sector = st.multiselect("Sectors", 
                    ["Solar", "Wind", "Energy Efficiency", "Clean Transportation", 
                    "Battery Storage", "Green Building", "Climate Tech", "Renewable Energy"],
                    key="enhanced_sectors")
                
                enhanced_location = st.multiselect("Locations", 
                    ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell", 
                    "New Bedford", "Fall River", "Lawrence", "Holyoke", "Remote"],
                    key="enhanced_locations")
            
            with col2:
                enhanced_exp = st.selectbox("Experience Level",
                    ["All", "Entry Level", "Mid Level", "Senior Level", "Management", "Executive"],
                    key="enhanced_exp_level")
                
                enhanced_remote = st.selectbox("Remote Work",
                    ["All", "Remote Only", "Hybrid", "On-site"],
                    key="enhanced_remote")
        
        # Options for enhanced search
        use_member_companies = st.checkbox("Search member companies only", value=True)
        
        # Enhanced search button
        if st.button("Enhanced Search", key="enhanced_search_btn"):
            with st.spinner("Performing enhanced job search..."):
                try:
                    # Import enhanced job search module
                    from tools.enhanced_job_search import EnhancedJobSearch
                    
                    # Create user profile
                    user_profile = {
                        "user_id": st.session_state.user_id,
                        "user_type": st.session_state.user_type,
                        "is_veteran": st.session_state.user_type == "Veteran",
                        "is_ej_community": st.session_state.is_ej_community,
                        "skills": skills if skills else []
                    }
                    
                    # Create search parameters
                    search_params = {
                        "search_text": search_text,
                        "sectors": enhanced_sector,
                        "locations": enhanced_location,
                        "experience_level": enhanced_exp if enhanced_exp != "All" else None,
                        "remote_status": enhanced_remote if enhanced_remote != "All" else None
                    }
                    
                    # Create job search instance
                    job_search = EnhancedJobSearch()
                    
                    # Execute enhanced search asynchronously
                    search_results = run_async_helper(
                        job_search.search_jobs_for_user(
                            user_profile=user_profile,
                            search_params=search_params,
                            member_companies_only=use_member_companies
                        )
                    )
                    
                    # Process results
                    if search_results and "jobs" in search_results:
                        enhanced_jobs = search_results["jobs"]
                        
                        # Add match scores if not present
                        for job in enhanced_jobs:
                            if "relevance_score" in job and "match_score" not in job:
                                job["match_score"] = job["relevance_score"] * 100
                        
                        # Display results
                        display_job_results(enhanced_jobs)
                        
                        # Show metrics
                        if "metrics" in search_results:
                            with st.expander("Search Metrics", expanded=False):
                                st.json(search_results["metrics"])
                    else:
                        st.info("No job matches found. Try adjusting your search criteria.")
                except Exception as e:
                    st.error(f"Enhanced job search encountered an error: {str(e)}")
                    st.info("Falling back to standard search...")
                    
                    # Fall back to standard search
                    filters = {
                        "sector": enhanced_sector[0] if enhanced_sector else None,
                        "location": enhanced_location[0] if enhanced_location else None,
                        "experience_level": enhanced_exp if enhanced_exp != "All" else None
                    }
                    
                    jobs = get_job_matches(st.session_state.user_id, filters)
                    display_job_results(jobs)

def display_job_results(jobs):
    """Helper function to display job search results"""
    st.subheader(f"Found {len(jobs)} Job Opportunities")
    
    if jobs:
        for i, job in enumerate(jobs):
            # Calculate match score if not already present
            match_score = job.get('match_score', 75)  # Default score if not present
            
            # Format job card
            with st.expander(f"{job['title']} at {job['company']} - Match Score: {match_score:.0f}%", expanded=(i==0)):
                cols = st.columns([2, 1])
                
                with cols[0]:
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Type:** {job.get('job_type', 'Not specified')}")
                    st.write(f"**Description:**")
                    st.write(job.get('description', 'No description available'))
                    
                    # Show requirements if available
                    if 'requirements' in job and 'skills' in job['requirements']:
                        st.write("**Requirements:**")
                        for skill in job['requirements']['skills']:
                            # Highlight matching skills
                            if 'skills' in locals() and skills and skill in skills:
                                st.markdown(f"- **:green[{skill}]** ✓")
                            else:
                                st.write(f"- {skill}")
                
                with cols[1]:
                    # Show apply button
                    if st.button("Apply Now", key=f"apply_{job.get('id', i)}"):
                        st.success("Application initiated! You would be redirected to the application portal.")
                    
                    # Show company info if available
                    if 'company' in job:
                        st.write("**Company:** " + job['company'])
                    
                    # Show additional info like salary if available
                    if 'salary_range' in job:
                        st.write("**Salary:** " + job['salary_range'])
                    
                    # Show badges for special programs
                    if job.get('is_veteran_friendly'):
                        st.markdown("🎖️ **Veteran-friendly**")
                    
                    if job.get('is_ej_friendly'):
                        st.markdown("🌱 **EJ community-friendly**")
    else:
        st.info("No job matches found. Try adjusting your filters.")
        
        # Suggest related searches
        st.subheader("Try these related searches:")
        suggestions = [
            "Energy Efficiency", "Solar Installation", "Wind Technician", 
            "Green Building", "Clean Transportation"
        ]
        
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(cols):
            with suggestion:
                if st.button(suggestions[i]):
                    # This would update the sector and rerun
                    pass

def training_programs_page():
    st.title("Training Programs")
    
    if not st.session_state.profile_complete:
        st.warning("Please complete your profile assessment first.")
        st.write("Go to the User Assessment page to complete your profile.")
        return
    
    st.write("Find training programs to enhance your skills for clean energy careers.")
    
    # Filters
    with st.expander("Search Filters", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sector = st.selectbox("Sector", 
                ["All", "Solar", "Wind", "Energy Efficiency", "Clean Transportation", 
                "Battery Storage", "Green Building", "Climate Tech", "Energy Management"])
                
            location = st.selectbox("Location", 
                ["All", "Boston", "Worcester", "Springfield", "Cambridge", "Lowell", 
                "New Bedford", "Fall River", "Lawrence", "Holyoke", "Online"])
        
        with col2:
            program_type = st.selectbox("Program Type", 
                ["All", "Certificate", "Degree", "Apprenticeship", "Short Course", "Workshop"])
                
            length = st.selectbox("Program Length",
                ["All", "Less than 1 month", "1-3 months", "3-6 months", "6-12 months", "1+ year"])
    
        # Budget constraints
        has_funding = st.checkbox("Programs with financial assistance")
    
    # Special considerations based on user type
    if st.session_state.user_type == "Veteran":
        st.info("As a veteran, you may be eligible for GI Bill benefits or other specialized funding for clean energy training.")
        show_veteran_programs = st.checkbox("Show veteran-specific programs")
    
    if st.session_state.is_ej_community:
        st.info("As a member of an Environmental Justice community, you may qualify for specialized training programs with additional support services.")
        show_ej_programs = st.checkbox("Show EJ community-focused programs")
    
    if st.session_state.user_type == "International Professional":
        st.info("As an international professional, you may benefit from credential-bridging programs.")
        show_international_programs = st.checkbox("Show credential-bridging programs")
    
    # Search button
    if st.button("Find Training Programs"):
        with st.spinner("Searching for training programs..."):
            # Build database retriever if available
            if db_tools_available:
                try:
                    db_retriever = DBRetrieverTool()
                    from lib.tools.db_retriever import TrainingSearchParams
                    
                    # Create search parameters
                    params = TrainingSearchParams(
                        user_id=st.session_state.user_id,
                        location=location if location != "All" else None,
                        sector=sector if sector != "All" else None,
                        is_ej_focused=True if st.session_state.is_ej_community and "show_ej_programs" in locals() and show_ej_programs else None,
                        has_funding=has_funding
                    )
                    
                    # Execute search
                    results = run_async_helper(db_retriever.search_training(params))
                except Exception as e:
                    st.error(f"Error searching training programs: {str(e)}")
                    results = []
            else:
                # Sample data when DB tools not available
                results = [
                    {
                        "id": "training-1",
                        "title": "Solar Installation Certificate",
                        "provider": "Massachusetts Clean Energy Center",
                        "location": "Boston, MA",
                        "description": "Comprehensive solar PV installation training covering design, installation, and maintenance.",
                        "sector": "Solar",
                        "program_type": "Certificate",
                        "length": "3 months",
                        "cost": "$2,500",
                        "funding_options": ["Workforce Training Fund", "Income-based scholarships"],
                        "is_ej_focused": True,
                        "is_veteran_friendly": True
                    },
                    {
                        "id": "training-2",
                        "title": "Energy Auditor Training",
                        "provider": "Energy Services Coalition",
                        "location": "Worcester, MA",
                        "description": "Learn to conduct comprehensive energy audits and prepare reports for residential and commercial buildings.",
                        "sector": "Energy Efficiency",
                        "program_type": "Certificate",
                        "length": "6 weeks",
                        "cost": "$1,800",
                        "funding_options": ["Mass Save sponsor"],
                        "is_ej_focused": False,
                        "is_veteran_friendly": True
                    },
                    {
                        "id": "training-3",
                        "title": "Building Performance Institute Certification",
                        "provider": "Green Jobs Academy",
                        "location": "Online",
                        "description": "Industry-recognized certification for building analysts and energy efficiency professionals.",
                        "sector": "Energy Efficiency",
                        "program_type": "Certificate",
                        "length": "4 weeks",
                        "cost": "$1,200",
                        "funding_options": [],
                        "is_ej_focused": False,
                        "is_veteran_friendly": False
                    }
                ]
            
            # Filter results based on form inputs
            filtered_results = []
            for program in results:
                # Apply filters
                if sector != "All" and program.get("sector") != sector:
                    continue
                    
                if location != "All" and location not in program.get("location", ""):
                    continue
                    
                if program_type != "All" and program.get("program_type") != program_type:
                    continue
                    
                if length != "All":
                    if length == "Less than 1 month" and "month" in program.get("length", "").lower() and int(program.get("length", "0").split()[0]) >= 1:
                        continue
                    elif length == "1-3 months" and ("month" not in program.get("length", "").lower() or int(program.get("length", "0").split()[0]) < 1 or int(program.get("length", "0").split()[0]) > 3):
                        continue
                    elif length == "3-6 months" and ("month" not in program.get("length", "").lower() or int(program.get("length", "0").split()[0]) < 3 or int(program.get("length", "0").split()[0]) > 6):
                        continue
                    elif length == "6-12 months" and ("month" not in program.get("length", "").lower() or int(program.get("length", "0").split()[0]) < 6 or int(program.get("length", "0").split()[0]) > 12):
                        continue
                    elif length == "1+ year" and "year" not in program.get("length", "").lower():
                        continue
                
                if has_funding and not program.get("funding_options"):
                    continue
                    
                if "show_veteran_programs" in locals() and show_veteran_programs and not program.get("is_veteran_friendly"):
                    continue
                    
                if "show_ej_programs" in locals() and show_ej_programs and not program.get("is_ej_focused"):
                    continue
                
                filtered_results.append(program)
            
            # Display results
            st.subheader(f"Found {len(filtered_results)} Training Programs")
            
            if filtered_results:
                for i, program in enumerate(filtered_results):
                    with st.expander(f"{program['title']} - {program['provider']}", expanded=(i==0)):
                        cols = st.columns([2, 1])
                        
                        with cols[0]:
                            st.write(f"**Location:** {program['location']}")
                            st.write(f"**Type:** {program.get('program_type', 'Not specified')}")
                            st.write(f"**Length:** {program.get('length', 'Not specified')}")
                            st.write(f"**Description:**")
                            st.write(program.get('description', 'No description available'))
                        
                        with cols[1]:
                            st.write(f"**Cost:** {program.get('cost', 'Not specified')}")
                            
                            # Show funding options if available
                            if program.get('funding_options'):
                                st.write("**Funding Options:**")
                                for option in program['funding_options']:
                                    st.write(f"- {option}")
                            
                            # Show apply button
                            if st.button("Learn More", key=f"more_{program.get('id', i)}"):
                                st.success("You would be redirected to the program website.")
                            
                            # Show badges for special programs
                            if program.get('is_veteran_friendly'):
                                st.markdown("🎖️ **Veteran-friendly**")
                            
                            if program.get('is_ej_focused'):
                                st.markdown("🌱 **EJ community-focused**")
            else:
                st.info("No training programs match your criteria. Try adjusting your filters.")
                
                # Suggest related searches
                st.subheader("Try these related sectors:")
                suggestions = [
                    "Energy Efficiency", "Solar", "Clean Transportation", 
                    "Green Building", "Energy Management"
                ]
                
                cols = st.columns(len(suggestions))
                for i, suggestion in enumerate(cols):
                    with suggestion:
                        if st.button(suggestions[i]):
                            # This would update the sector and rerun
                            pass

def dashboard_page():
    st.title("Analytics Dashboard")
    
    # Add tab selection
    dashboard_tabs = st.tabs(["Metrics", "Network Analysis", "Feedback Analysis"])
    
    with dashboard_tabs[0]:
        # Get metrics
        metrics = get_user_metrics()
        
        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Users", metrics['active_users'])
        with col2:
            st.metric("Job Matches", metrics['job_matches'])
        with col3:
            st.metric("Training Programs", metrics['training_programs'])
        
        # User distribution chart
        distribution = get_user_distribution()
        if distribution['regions'] and distribution['counts']:
            fig = px.pie(
                values=distribution['counts'],
                names=distribution['regions'],
                title="User Distribution by Region"
            )
            st.plotly_chart(fig)
        
        # Recent activity table
        st.subheader("Recent Activity")
        activity = get_recent_activity(limit=10)
        if activity:
            df = pd.DataFrame(activity)
            df['created_at'] = pd.to_datetime(df['created_at'])
            st.dataframe(
                df[['created_at', 'user_id', 'activity_type', 'status']],
                hide_index=True
            )
    
    with dashboard_tabs[1]:
        # Network insights
        try:
            # Import relationship analyzer
            from tools.relationship_analyzer import RelationshipAnalyzer
            
            # Initialize analyzer
            analyzer = RelationshipAnalyzer()
            
            # Get network insights
            with st.spinner("Analyzing network relationships..."):
                try:
                    # Run relationship analysis asynchronously
                    network_insights = run_async_helper(analyzer.identify_key_relationships(top_n=5))
                    
                    # Display insights
                    if network_insights:
                        st.subheader("Key Organizational Relationships")
                        for relationship in network_insights:
                            st.write(f"**{relationship['org1']} ↔ {relationship['org2']}**")
                            st.write(f"Strength: {relationship['strength']}")
                            st.write(f"Context: {relationship['context']}")
                            st.write("---")
                    
                    # Get user-organization connections
                    user_org_connections = analyzer.analyze_user_organization_connections(limit=20)
                    if user_org_connections and "connections" in user_org_connections:
                        st.subheader("Top User-Organization Connections")
                        for connection in user_org_connections["connections"][:5]:
                            st.write(f"**{connection['user']} → {connection['organization']}**")
                            st.write(f"Connection strength: {connection['strength']}")
                            st.write("---")
                except Exception as e:
                    st.error(f"Error analyzing relationships: {str(e)}")
        except ImportError:
            st.info("Network analysis features are not available.")
    
    with dashboard_tabs[2]:
        # RLHF Feedback Analysis
        try:
            # Import feedback processor
            from tools.train_rlhf import FeedbackProcessor
            
            # Initialize processor
            processor = FeedbackProcessor()
            
            # Get feedback data
            with st.spinner("Processing feedback data..."):
                try:
                    # Fetch feedback data 
                    feedback_data = processor.fetch_feedback_data()
                    
                    if not feedback_data.empty:
                        st.success(f"Loaded {len(feedback_data)} feedback entries")
                        
                        # Show feedback distribution
                        st.subheader("Feedback Score Distribution")
                        
                        # Create histogram of scores
                        fig = px.histogram(
                            feedback_data, 
                            x="score",
                            nbins=5,
                            title="Distribution of User Feedback Scores",
                            labels={"score": "Score (1-5)", "count": "Number of Feedback Entries"}
                        )
                        st.plotly_chart(fig)
                        
                        # Show average score
                        avg_score = feedback_data["score"].mean()
                        st.metric("Average Feedback Score", f"{avg_score:.2f}/5.0")
                        
                        # Option to train reward model
                        if st.button("Train Reward Model"):
                            with st.spinner("Preparing training data..."):
                                # Prepare training data
                                train_data, test_data = processor.prepare_training_data()
                                
                                st.success(f"Prepared {len(train_data)} training samples and {len(test_data)} test samples")
                                st.info("In a production environment, this would now train the reward model. This has been disabled for this demo.")
                                
                    else:
                        st.info("No feedback data available yet.")
                except Exception as e:
                    st.error(f"Error processing feedback: {str(e)}")
        except ImportError:
            st.info("RLHF feedback analysis features are not available.")
            
    # Add a fourth tab for Performance Monitoring
    with st.expander("Performance Monitoring", expanded=False):
        try:
            # Import metrics service
            from lib.monitoring.metrics_service import MetricsService
            
            # Initialize metrics service
            metrics_service = MetricsService()
            
            # Set date range for performance metrics
            from datetime import datetime, timedelta
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            # Get performance metrics
            with st.spinner("Loading performance metrics..."):
                try:
                    # Get API performance metrics
                    api_metrics = run_async_helper(
                        metrics_service.get_api_performance_metrics(start_time, end_time)
                    )
                    
                    if api_metrics and "endpoints" in api_metrics:
                        st.subheader("API Performance")
                        
                        # Create a dataframe for the metrics
                        api_data = []
                        for endpoint, metrics in api_metrics["endpoints"].items():
                            api_data.append({
                                "Endpoint": endpoint,
                                "Avg Response Time (ms)": metrics.get("avg_response_time", 0),
                                "P95 Response Time (ms)": metrics.get("p95_response_time", 0),
                                "Success Rate": f"{metrics.get('success_rate', 0) * 100:.1f}%",
                                "Request Count": metrics.get("request_count", 0)
                            })
                        
                        # Display as a table
                        if api_data:
                            api_df = pd.DataFrame(api_data)
                            st.dataframe(api_df, hide_index=True)
                        else:
                            st.info("No API performance data available.")
                    
                    # Get user activity metrics
                    user_metrics = run_async_helper(
                        metrics_service.get_user_activity_metrics(start_time, end_time)
                    )
                    
                    if user_metrics and "activity_counts" in user_metrics:
                        st.subheader("User Activity")
                        
                        # Create chart data
                        activity_types = list(user_metrics["activity_counts"].keys())
                        activity_counts = list(user_metrics["activity_counts"].values())
                        
                        if activity_types and activity_counts:
                            # Create bar chart
                            fig = px.bar(
                                x=activity_types,
                                y=activity_counts,
                                title="User Activity by Type",
                                labels={"x": "Activity Type", "y": "Count"}
                            )
                            st.plotly_chart(fig)
                        else:
                            st.info("No user activity data available.")
                    
                    # Check for any performance alerts
                    if "alerts" in api_metrics and api_metrics["alerts"]:
                        st.subheader("Performance Alerts")
                        for alert in api_metrics["alerts"]:
                            alert_msg = f"⚠️ {alert['message']} ({alert['severity']})"
                            st.warning(alert_msg)
                except Exception as e:
                    st.error(f"Error loading performance metrics: {str(e)}")
        except ImportError:
            st.info("Performance monitoring features are not available.")

# Route to the appropriate page
if page == "User Assessment":
    user_assessment_page()
elif page == "Chat Assistant":
    chat_assistant_page()
elif page == "Job Search":
    job_search_page()
elif page == "Training Programs":
    training_programs_page()
else:
    dashboard_page() 