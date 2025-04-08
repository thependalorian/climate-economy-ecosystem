# MA Clean Tech Ecosystem Assistant - Streamlit Version

This is a Streamlit-based version of the Massachusetts Clean Tech Ecosystem Assistant, providing a chat interface and analytics dashboard for connecting individuals with clean energy opportunities.

## Features

- **Chat Assistant**: Interactive chat interface with GPT-4 integration for personalized assistance
- **Analytics Dashboard**: Real-time metrics and visualizations of system usage
- **Database Integration**: Supabase integration for data persistence
- **RLHF Support**: Feedback collection for continuous improvement

## Prerequisites

- Python 3.8+
- Supabase account
- OpenAI API key

## Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/climate_economy_ecosystem.git
cd climate_economy_ecosystem
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

## Features

### Chat Assistant
- Real-time conversation with AI
- Context-aware responses
- Support for veterans and international professionals
- Focus on Environmental Justice communities

### Dashboard
- User engagement metrics
- Geographic distribution
- Activity tracking
- Performance analytics

## Database Schema

The application uses the following main tables in Supabase:

- `chats`: Stores chat messages and interactions
- `profiles`: User profiles and preferences
- `job_matches`: Job matching records
- `training_programs`: Available training programs
- `chat_feedback`: User feedback for RLHF
- `activity_log`: System activity tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 