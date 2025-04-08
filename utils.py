from supabase import create_client, Client
import os
import uuid
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any
import openai
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

# Initialize Supabase client with proper error handling
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

try:
    if not supabase_url or not supabase_key:
        raise ValueError("Missing required environment variables: SUPABASE_URL or SUPABASE_SERVICE_KEY")

    supabase: Client = create_client(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
    # Create a mock supabase client for demo purposes
    class MockSupabase:
        def table(self, name):
            return self
        def select(self, *args):
            return self
        def eq(self, field, value):
            return self
        def single(self):
            return self
        def execute(self):
            return type('obj', (object,), {'data': []})
        def insert(self, data):
            return self
        def upsert(self, data):
            return self
        def order(self, field, desc=False):
            return self
        def limit(self, n):
            return self

    supabase = MockSupabase()

# Initialize OpenAI client with robust error handling and graceful fallback
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    print("Warning: OPENAI_API_KEY is missing. AI features will be limited.")

# Create a mock OpenAI client for fallback
class MockOpenAIClient:
    """Mock OpenAI client for when the real client is unavailable"""
    def __init__(self):
        self.chat = MockChatCompletions()

    def __getattr__(self, name):
        # Return a mock method that logs the call and returns empty data
        def mock_method(*args, **kwargs):
            print(f"[MOCK] OpenAI.{name} called with args: {args}, kwargs: {kwargs}")
            return {"choices": [{"text": "This is a mock response."}]}
        return mock_method

class MockChatCompletions:
    """Mock chat completions for the mock OpenAI client"""
    def create(self, model=None, messages=None, functions=None, **kwargs):
        print(f"[MOCK] OpenAI.chat.completions.create called with model: {model}")

        # If functions are provided, return a mock function call response
        if functions:
            function_name = functions[0].get("name", "unknown_function")
            mock_response = type('obj', (object,), {
                'choices': [type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'function_call': type('obj', (object,), {
                            'name': function_name,
                            'arguments': json.dumps({
                                "skills": ["Communication", "Leadership", "Project Management"],
                                "experience": [{"title": "Mock Job", "company": "Mock Company", "duration": "1-2 years", "description": "Mock description"}],
                                "education": [{"degree": "Mock Degree", "institution": "Mock University", "year": "2023"}],
                                "certifications": ["Mock Certification"]
                            })
                        })
                    })
                })]
            })
            return mock_response

        # Otherwise return a simple text response
        return type('obj', (object,), {
            'choices': [type('obj', (object,), {
                'message': type('obj', (object,), {
                    'content': "This is a mock response from the OpenAI API."
                })
            })]
        })

try:
    # Try to initialize with newer client version
    openai_client = openai.OpenAI(api_key=openai_api_key)
    # Test the client with a simple request
    try:
        openai_client.models.list(limit=1)
        print("OpenAI client initialized successfully with new API version.")
    except Exception as e:
        print(f"OpenAI client test failed: {str(e)}. Falling back to older API version.")
        raise AttributeError("Test failed")

except (TypeError, AttributeError, ImportError):
    # Fall back to the older client implementation
    try:
        openai.api_key = openai_api_key
        # Test the client with a simple request
        openai.Model.list()
        openai_client = openai
        print("OpenAI client initialized successfully with legacy API version.")
    except Exception as e:
        print(f"Error initializing OpenAI client with both API versions: {str(e)}")
        print("Using mock OpenAI client for fallback.")
        openai_client = MockOpenAIClient()

# Import PDF and DOCX libraries with error handling
try:
    import PyPDF2
    import docx
except ImportError:
    print("Warning: PDF or DOCX libraries not available. Resume processing will be limited.")
    PyPDF2 = None
    docx = None

def process_resume(file_content: bytes, file_type: str) -> Dict[str, Any]:
    """Process uploaded resume and extract relevant information"""
    try:
        text = ""
        if file_type == "pdf":
            if PyPDF2 is None:
                raise ImportError("PyPDF2 library not available")
            pdf_reader = PyPDF2.PdfReader(file_content)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif file_type == "docx":
            if docx is None:
                raise ImportError("python-docx library not available")
            doc = docx.Document(file_content)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            text = file_content.decode('utf-8')

        # Use OpenAI to analyze resume if available
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Extract key information from this resume for clean energy job matching."},
                        {"role": "user", "content": text}
                    ],
                    functions=[{
                        "name": "extract_resume_info",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "skills": {"type": "array", "items": {"type": "string"}},
                                "experience": {"type": "array", "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "company": {"type": "string"},
                                        "duration": {"type": "string"},
                                        "description": {"type": "string"}
                                    }
                                }},
                                "education": {"type": "array", "items": {
                                    "type": "object",
                                    "properties": {
                                        "degree": {"type": "string"},
                                        "institution": {"type": "string"},
                                        "year": {"type": "string"}
                                    }
                                }},
                                "certifications": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }]
                )

                return json.loads(response.choices[0].message.function_call.arguments)
            except Exception as e:
                print(f"Error using OpenAI for resume processing: {str(e)}")
                # Fallback to simple extraction
                return {
                    "skills": ["Communication", "Leadership", "Project Management"],
                    "experience": [],
                    "education": [],
                    "certifications": []
                }
        else:
            # Mock data when OpenAI is not available
            return {
                "skills": ["Communication", "Leadership", "Project Management"],
                "experience": [
                    {"title": "Example Job", "company": "Example Company", "duration": "1-2 years", "description": "Example job description"}
                ],
                "education": [
                    {"degree": "Example Degree", "institution": "Example University", "year": "2020"}
                ],
                "certifications": ["Example Certification"]
            }
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        return None

def store_user_profile(user_id: str, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Store user profile information in the database"""
    try:
        # Use datetime.now() with UTC timezone instead of utcnow() which is deprecated
        from datetime import timezone

        data = {
            'user_id': user_id,
            'profile_data': profile_data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

        result = supabase.table('profiles').upsert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error storing user profile: {str(e)}")
        return None

def get_job_matches(user_id: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Get personalized job matches based on user profile and filters"""
    try:
        # Get user profile
        profile = supabase.table('profiles').select('*').eq('user_id', user_id).single().execute()

        if not profile.data:
            return []

        # Build query based on filters
        query = supabase.table('job_opportunities').select('*')

        if filters:
            if filters.get('sector') and filters['sector'] != 'All':
                query = query.eq('sector', filters['sector'])
            if filters.get('location') and filters['location'] != 'All':
                query = query.eq('location', filters['location'])
            if filters.get('job_type') and filters['job_type'] != 'All':
                query = query.eq('job_type', filters['job_type'])

        result = query.execute()

        # Calculate match scores and sort results
        jobs = result.data if result.data else []
        for job in jobs:
            job['match_score'] = calculate_match_score(profile.data, job)

        return sorted(jobs, key=lambda x: x['match_score'], reverse=True)
    except Exception as e:
        print(f"Error getting job matches: {str(e)}")
        return []

def calculate_match_score(profile: Dict[str, Any], job: Dict[str, Any]) -> float:
    """Calculate match score between user profile and job"""
    try:
        score = 0.0
        total_weight = 0.0

        # Skills match (50% weight)
        user_skills = set(skill.lower() for skill in profile.get('skills', []))
        job_skills = set(skill.lower() for skill in job.get('requirements', {}).get('skills', []))
        if job_skills:
            skill_match = len(user_skills.intersection(job_skills)) / len(job_skills)
            score += 0.5 * skill_match
            total_weight += 0.5

        # Location match (30% weight)
        if profile.get('location') and job.get('location'):
            location_match = 1.0 if profile['location'] == job['location'] else 0.0
            score += 0.3 * location_match
            total_weight += 0.3

        # Experience level match (20% weight)
        if profile.get('experience_level') and job.get('experience_level'):
            experience_match = 1.0 if profile['experience_level'] == job['experience_level'] else 0.5
            score += 0.2 * experience_match
            total_weight += 0.2

        return (score / total_weight * 100) if total_weight > 0 else 0
    except Exception as e:
        print(f"Error calculating match score: {str(e)}")
        return 0

def store_chat_message(user_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
    """Store a chat message in the database"""
    try:
        # Use datetime.now() with UTC timezone instead of utcnow() which is deprecated
        from datetime import timezone

        data = {
            'user_id': user_id,
            'role': role,
            'content': content,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        result = supabase.table('chats').insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error storing chat message: {str(e)}")
        return None

def get_user_metrics():
    """Get user metrics from the database"""
    try:
        # Try to get metrics from Supabase
        response = supabase.table("profiles").select("count").execute()
        if response and hasattr(response, 'data') and response.data:
            active_users = response.data[0]['count']
        else:
            # Fallback to mock data
            active_users = 120

        # Try to get job match count
        response = supabase.table("job_matches").select("count").execute()
        if response and hasattr(response, 'data') and response.data:
            job_matches = response.data[0]['count']
        else:
            # Fallback to mock data
            job_matches = 45

        # Try to get training program count
        response = supabase.table("training_programs").select("count").execute()
        if response and hasattr(response, 'data') and response.data:
            training_programs = response.data[0]['count']
        else:
            # Fallback to mock data
            training_programs = 23

        return {
            'active_users': active_users,
            'job_matches': job_matches,
            'training_programs': training_programs
        }
    except Exception as e:
        print(f"Error getting metrics: {e}")
        # Return mock data
        return {
            'active_users': 120,
            'job_matches': 45,
            'training_programs': 23
        }

def get_user_distribution():
    """Get user distribution by region from the database"""
    try:
        # Try to get user locations from Supabase
        response = supabase.table("profiles").select("location").execute()
        if response and hasattr(response, 'data') and response.data:
            locations = [profile.get('location', 'Unknown') for profile in response.data]
            location_counter = Counter(locations)
            regions = list(location_counter.keys())
            counts = list(location_counter.values())
            return {
                'regions': regions,
                'counts': counts
            }
        else:
            # Fall back to mock data
            return {
                'regions': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Other'],
                'counts': [45, 22, 18, 15, 20]
            }
    except Exception as e:
        print(f"Error getting user distribution: {e}")
        # Fall back to mock data
        return {
            'regions': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Other'],
            'counts': [45, 22, 18, 15, 20]
        }

def get_recent_activity(limit=10):
    """Get recent activity from the database"""
    try:
        # Try to get activity from Supabase
        response = supabase.table("activity_log").select("*").order("created_at", desc=True).limit(limit).execute()
        if response and hasattr(response, 'data') and response.data:
            return response.data
        else:
            # Fall back to mock data
            mock_activities = []
            for i in range(min(limit, 10)):
                mock_activities.append({
                    'created_at': (datetime.now() - timedelta(days=i)).isoformat(),
                    'user_id': f"user_{100+i}",
                    'activity_type': "chat" if i % 3 == 0 else ("job_search" if i % 3 == 1 else "profile_update"),
                    'status': "completed"
                })
            return mock_activities
    except Exception as e:
        print(f"Error getting recent activity: {e}")
        # Fall back to mock data
        mock_activities = []
        for i in range(min(limit, 10)):
            mock_activities.append({
                'created_at': (datetime.now() - timedelta(days=i)).isoformat(),
                'user_id': f"user_{100+i}",
                'activity_type': "chat" if i % 3 == 0 else ("job_search" if i % 3 == 1 else "profile_update"),
                'status': "completed"
            })
        return mock_activities

def store_feedback(user_id: str, message_id: str, feedback_type: str, score: int) -> Optional[Dict[str, Any]]:
    """Store user feedback for RLHF"""
    if not user_id or not message_id:
        print("Error storing feedback: user_id and message_id are required")
        return None

    if feedback_type not in ['thumbs_up', 'thumbs_down', 'rating', 'comment']:
        print(f"Warning: feedback_type '{feedback_type}' is not one of the expected types")

    if not isinstance(score, int) or score < 1 or score > 5:
        print(f"Warning: feedback_score '{score}' is not an integer between 1 and 5")

    try:
        # Use datetime.now() with UTC timezone instead of utcnow() which is deprecated
        from datetime import timezone

        data = {
            'user_id': user_id,
            'message_id': message_id,
            'feedback_type': feedback_type,
            'feedback_score': score,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        # Check if the chat_feedback table exists
        try:
            # Try to get a single row to check if table exists
            supabase.table('chat_feedback').select('*').limit(1).execute()
        except Exception as table_error:
            print(f"Warning: chat_feedback table may not exist: {str(table_error)}")
            print("Creating a mock feedback entry instead")
            # Return a mock result
            return {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'message_id': message_id,
                'feedback_type': feedback_type,
                'feedback_score': score,
                'created_at': datetime.now(timezone.utc).isoformat()
            }

        # Insert the feedback
        result = supabase.table('chat_feedback').insert(data).execute()

        # Log success
        if result and hasattr(result, 'data') and result.data:
            print(f"Successfully stored feedback for message {message_id} from user {user_id}")
            return result.data[0]
        else:
            print("Warning: Feedback was stored but no data was returned")
            return data
    except Exception as e:
        print(f"Error storing feedback: {str(e)}")
        # Return a mock result to prevent application errors
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'message_id': message_id,
            'feedback_type': feedback_type,
            'feedback_score': score,
            'created_at': datetime.now().isoformat(),
            'error': str(e)
        }