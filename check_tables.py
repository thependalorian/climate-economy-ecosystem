from supabase import create_client
import os

# Initialize Supabase client
supabase = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_SERVICE_KEY')
)

print('Connected to Supabase successfully!')

# Tables to check
tables_to_check = ['chat_feedback', 'chats', 'users', 'feedback_metrics']

# Check each table
for table in tables_to_check:
    try:
        # Just try to select a single row to check if table exists
        response = supabase.table(table).select('*').limit(1).execute()
        print(f'Table {table} exists')
    except Exception as e:
        print(f'Table {table} does not exist or error: {str(e)}')
