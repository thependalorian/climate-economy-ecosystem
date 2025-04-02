# Climate Economy Assistant Documentation

## Architecture Overview

The Climate Economy Assistant is built using a function-calling architecture that routes vector searches and other operations through the OpenAI assistant. This approach provides several benefits:

1. **Flexibility**: The assistant can decide when to search for information based on the context of the conversation.
2. **Contextual awareness**: The assistant understands what to search for and how to interpret the results.
3. **Enhanced user experience**: Users receive more natural and comprehensive responses.
4. **Multiple data sources**: The assistant can combine information from the vector database, user profiles, and eligibility checks.

## Components

### 1. Assistant Tools (Function Definitions)

Located in `/lib/assistant/tools.js`, this module defines the tools available to the assistant and their implementations:

- `search_knowledge_base`: Searches the vector database for relevant content based on semantic similarity.
- `get_user_profile`: Retrieves the user's profile for personalized responses.
- `check_connection_eligibility`: Checks if a user meets the criteria to connect with partners.

### 2. Chat API

Located in `/app/api/assistant/chat/route.js`, this endpoint:

- Processes incoming user messages
- Manages conversation history and memory
- Handles the function calling flow with OpenAI
- Routes vector searches through the assistant's function calling
- Caches responses for improved performance

### 3. Search API

Located in `/app/api/assistant/search/route.js`, this endpoint:

- Provides a dedicated search interface
- Uses the same function calling infrastructure as the chat API
- Supports filtering by content type and source
- Caches search results for better performance

### 4. Memory Management

Located in `/lib/memory.js`, this system:

- Stores conversation history for authenticated users
- Builds context from previous conversations
- Generates summaries of longer conversations
- Manages memory expiration and cleanup

### 5. Redis Cache

Located in `/lib/redis.js`, this utility:

- Provides caching for chat responses and search results
- Reduces latency and API costs
- Manages cache expiration and invalidation

## Function Calling Flow

When a user sends a message, the system follows this process:

1. **Chat Message Received**: The chat API receives a message from the user.
2. **User Authentication**: If the user is authenticated, their profile and memory are retrieved.
3. **System Prompt Creation**: A custom system prompt is created based on user information and conversation history.
4. **Initial Response Generation**: The message is sent to OpenAI's API with the function tools available.
5. **Function Calling Decision**: The model determines if it needs to call any functions to provide a better response.
6. **Function Execution**: If functions are called, they are executed and the results are provided back to the model.
7. **Final Response Generation**: The model generates a final response incorporating the function results.
8. **Memory Storage**: The conversation is stored in memory for authenticated users.
9. **Response Caching**: Responses are cached for anonymous users to improve performance.

## Vector Search Process

The vector search process follows these steps:

1. **Query Processing**: The user's query is processed to determine search intent.
2. **Function Calling**: The assistant calls the `search_knowledge_base` function.
3. **Embedding Generation**: The query is converted to an embedding vector.
4. **Vector Store Search**: The embedding is used to search the Supabase vector store.
5. **Result Filtering**: Results are filtered by relevance, type, and source.
6. **Response Formatting**: Search results are formatted for the assistant to use.
7. **Result Integration**: The assistant incorporates the search results into its response.

## Redis Caching

The system uses Redis for caching:

- **Chat Responses**: Caches responses to similar questions for 24 hours.
- **Search Results**: Caches search results for 1 hour.
- **Memory Storage**: Uses Redis to store conversation history and summaries.

## Updating and Extending the Assistant

To add new functions to the assistant:

1. Define the function in the `assistantTools` array in `/lib/assistant/tools.js`.
2. Implement the function in the same file.
3. Update the function calling handling in the chat API.
4. Update the system prompt to inform the assistant about the new capability.

## Security Considerations

The assistant implements several security measures:

- User data is only accessible to authenticated users.
- Function calls that retrieve user data validate the requesting user's ID.
- Sensitive operations like checking connection eligibility include authorization checks.
- Redis connections are secured using environment variables.

## Performance Optimizations

To ensure good performance:

- Responses are cached to reduce latency and API costs.
- Memory is managed efficiently with expiration policies.
- Search results are filtered before being sent to the client.
- Heavy operations like embedding generation are minimized.

## Environment Variables

The following environment variables are required:

```
OPENAI_API_KEY=your-openai-api-key
UPSTASH_REDIS_REST_URL=your-upstash-redis-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-token
```

## Deployment Considerations

When deploying to Vercel:

1. Set all required environment variables.
2. Ensure the Redis instance is accessible from the Vercel deployment.
3. Configure appropriate timeouts for function execution.
4. Monitor usage to optimize cache settings and API costs. 