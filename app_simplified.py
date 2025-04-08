import streamlit as st
import os
import sys
from datetime import datetime
import uuid
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="MA Clean Tech Ecosystem Assistant",
    page_icon="🌱",
    layout="wide"
)

# Simple utility functions for demonstration purposes
def store_chat_message(user_id, role, content):
    """Store a chat message (demo function)"""
    print(f"Storing message: {user_id} - {role}: {content}")
    return {"id": "msg_" + str(hash(content) % 10000)}

def get_user_metrics():
    """Get user metrics (demo function)"""
    return {
        'active_users': 120,
        'job_matches': 45,
        'training_programs': 23
    }

def get_user_distribution():
    """Get user distribution (demo function)"""
    return {
        'regions': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Other'],
        'counts': [45, 22, 18, 15, 20]
    }

def get_recent_activity(limit=10):
    """Get recent activity (demo function)"""
    activities = []
    for i in range(min(limit, 10)):
        activities.append({
            'created_at': pd.Timestamp.now() - pd.Timedelta(days=i),
            'user_id': f"user_{100+i}",
            'activity_type': "chat" if i % 3 == 0 else ("job_search" if i % 3 == 1 else "profile_update"),
            'status': "completed"
        })
    return activities

def process_resume(file_content, file_type):
    """Process resume (demo function)"""
    return {
        "skills": ["Communication", "Leadership", "Project Management", "Python", "Data Analysis"],
        "experience": [
            {"title": "Data Analyst", "company": "Tech Corp", "duration": "2-3 years", "description": "Analyzed data for clean energy projects"}
        ],
        "education": [
            {"degree": "BS Computer Science", "institution": "State University", "year": "2020"}
        ],
        "certifications": ["Project Management Professional", "Data Science Certificate"]
    }

def store_user_profile(user_id, profile_data):
    """Store user profile (demo function)"""
    print(f"Storing profile for user {user_id}")
    return {"id": user_id, "status": "success"}

def get_job_matches(user_id, filters=None):
    """Get job matches (demo function)"""
    jobs = [
        {
            "id": "job_1",
            "title": "Solar Panel Installer",
            "company": "Green Energy Inc",
            "location": "Boston",
            "job_type": "Full-time",
            "description": "Install solar panels on residential and commercial buildings",
            "requirements": {"skills": ["Technical", "Physical Fitness", "Safety", "Electrical"]},
            "match_score": 85,
            "is_veteran_friendly": True
        },
        {
            "id": "job_2",
            "title": "Energy Efficiency Consultant",
            "company": "EcoSave Solutions",
            "location": "Cambridge",
            "job_type": "Full-time",
            "description": "Conduct energy audits and recommend efficiency improvements",
            "requirements": {"skills": ["Analysis", "Communication", "Energy Systems", "Customer Service"]},
            "match_score": 78
        },
        {
            "id": "job_3",
            "title": "Wind Turbine Technician",
            "company": "WindPower Corp",
            "location": "Springfield",
            "job_type": "Full-time",
            "description": "Maintain and repair wind turbines",
            "requirements": {"skills": ["Technical", "Mechanical", "Physical Fitness", "Safety"]},
            "match_score": 72,
            "is_ej_friendly": True
        }
    ]
    
    # Apply filters if provided
    if filters:
        filtered_jobs = []
        for job in jobs:
            # Check if job matches all provided filters
            matches = True
            if filters.get('sector') and filters['sector'] != 'All':
                # In the demo data we don't have sectors, so we'll just match by title for simplicity
                if filters['sector'].lower() not in job['title'].lower():
                    matches = False
            if filters.get('location') and filters['location'] != 'All':
                if job['location'] != filters['location']:
                    matches = False
            if filters.get('job_type') and filters['job_type'] != 'All':
                if job['job_type'] != filters['job_type']:
                    matches = False
            if matches:
                filtered_jobs.append(job)
        return filtered_jobs
    
    return jobs

def store_feedback(user_id, message_id, feedback_type, score):
    """Store feedback (demo function)"""
    print(f"Storing feedback: {user_id} - {message_id}: {feedback_type} ({score})")
    return {"id": "feedback_" + str(hash(message_id) % 10000), "status": "success"}

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
    
# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["User Assessment", "Chat Assistant", "Job Search", "Dashboard"])

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
                    
                    # Create profile data
                    profile_data = {
                        "user_type": st.session_state.user_type,
                        "resume_data": resume_data,
                        "created_at": datetime.utcnow().isoformat(),
                        "is_ej_community": st.session_state.is_ej_community,
                        "military_data": st.session_state.military_data
                    }
                    
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

def chat_assistant_page():
    st.title("Chat Assistant")
    
    if not st.session_state.profile_complete:
        st.warning("Please complete your profile assessment first.")
        st.write("Go to the User Assessment page to complete your profile.")
        return
    
    st.write("Ask me anything about clean energy opportunities in Massachusetts!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        store_chat_message(st.session_state.user_id, "user", prompt)
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    # Here you would integrate with your AI model
                    response = "I understand you're interested in clean energy opportunities. Let me help you with that! (This is a placeholder response - AI integration pending)"
                    st.write(response)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    message_id = store_chat_message(st.session_state.user_id, "assistant", response).get('id', 'msg_1234')
                    
                    # Add feedback buttons
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
                st.session_state.chat_history.append({"role": "assistant", "content": "I apologize, but I encountered an error. Please try again."})

def job_search_page():
    st.title("Job Search")
    
    if not st.session_state.profile_complete:
        st.warning("Please complete your profile assessment first.")
        st.write("Go to the User Assessment page to complete your profile.")
        return
    
    st.write("Find clean energy job opportunities that match your profile.")
    
    # Filters
    with st.expander("Search Filters", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sector = st.selectbox("Sector", 
                ["All", "Solar", "Wind", "Energy Efficiency", "Clean Transportation", 
                "Battery Storage", "Green Building", "Climate Tech"])
                
            location = st.selectbox("Location", 
                ["All", "Boston", "Worcester", "Springfield", "Cambridge", "Lowell", 
                "New Bedford", "Fall River", "Lawrence", "Holyoke"])
        
        with col2:
            job_type = st.selectbox("Job Type", 
                ["All", "Full-time", "Part-time", "Contract", "Internship", "Apprenticeship"])
                
            experience_level = st.selectbox("Experience Level",
                ["All", "Entry Level", "Mid Level", "Senior Level", "Management", "Executive"])
    
        # Skills selection
        default_skills = []
        skills = st.multiselect("Skills", 
            ["Solar Installation", "Electrical", "HVAC", "Energy Auditing", "Project Management",
            "Customer Service", "Sales", "Engineering", "Design", "Technical Support",
            "Data Analysis", "Software Development", "Construction", "Mechanical", "Administrative"],
            default=default_skills)
    
    # Search button
    if st.button("Search Jobs"):
        with st.spinner("Searching for jobs..."):
            # Build filters
            filters = {
                "sector": sector if sector != "All" else None,
                "location": location if location != "All" else None,
                "job_type": job_type if job_type != "All" else None,
                "experience_level": experience_level if experience_level != "All" else None,
                "skills": skills if skills else None
            }
            
            # Get job matches
            jobs = get_job_matches(st.session_state.user_id, filters)
            
            # Display results
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
                                    if skills and skill in skills:
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

def dashboard_page():
    st.title("Analytics Dashboard")
    
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
        st.dataframe(
            df[['created_at', 'user_id', 'activity_type', 'status']],
            hide_index=True
        )

# Route to the appropriate page
if page == "User Assessment":
    user_assessment_page()
elif page == "Chat Assistant":
    chat_assistant_page()
elif page == "Job Search":
    job_search_page()
else:
    dashboard_page() 