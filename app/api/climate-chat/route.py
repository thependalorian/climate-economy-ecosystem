from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import os
import time
import openai
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import asyncio

# Import consolidated services
from lib.memory.memory_service import MemoryService, ClimateMemoryEntry, MemoryServiceError
from lib.redis.redis_service import RedisService, RedisServiceError
from lib.tracing.langsmith_service import TracingService, TracingServiceError

# Import tools
from tools.base_tool import BaseTool, ToolError
from tools.ej_geospatial import EJGeospatialTool
from tools.international_credential_evaluator import InternationalCredentialEvaluator

# Load environment variables
load_dotenv()

# Initialize services
memory_service = MemoryService()
redis_service = RedisService()
tracing_service = TracingService()

# Initialize tools
ej_geospatial_tool = EJGeospatialTool()
international_credential_evaluator = InternationalCredentialEvaluator()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI()

SYSTEM_PROMPT = """You are a specialized assistant for the Massachusetts Clean Tech Ecosystem. Your purpose is to help individuals in Massachusetts find jobs, training, and resources in the clean energy economy.

Special considerations:
1. For Veterans: Help translate military experience to clean energy careers
2. For International Professionals: Help evaluate overseas credentials for Massachusetts
3. For Environmental Justice Communities: Prioritize opportunities in Gateway Cities

Focus on Massachusetts-specific information whenever possible. If you don't have specific Massachusetts information, clearly indicate this.

Your tone should be helpful, informative, and encouraging.
"""

async def get_relevant_context(query: str, user_id: str, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get relevant context from memory and web search for the climate chat"""
    try:
        # Create a trace for context retrieval
        with tracing_service.trace(
            name="get_relevant_context",
            run_id=run_id or tracing_service.create_run_id(),
            inputs={"query": query, "user_id": user_id}
        ) as trace_run:
            # Try to get cached context first
            try:
                cache_key = f"context:{user_id}:{query}"
                cached_context = await redis_service.get(cache_key)
                if cached_context:
                    trace_run.end(outputs={"source": "cache", "context_count": len(cached_context)})
                    return cached_context
            except RedisServiceError:
                # Continue if Redis is unavailable
                pass
            
            context = []
            
            # First, try to get information from memory
            try:
                # Search user's memories
                memory_results = await memory_service.search_memories(
                    query=query,
                    user_id=user_id,
                    limit=5,
                    categories=["report", "job", "training"]
                )
                
                # Add memory results to context
                for result in memory_results:
                    context.append({
                        "source": "memory",
                        "content": result["content"],
                        "metadata": result["metadata"],
                        "relevance_score": result.get("relevance_score", 0.0)
                    })
                    
            except MemoryServiceError as e:
                # Log the error but continue
                print(f"Error searching memories: {str(e)}")
            
            # If we have EJ community data, add it to the context
            try:
                # Get user profile
                user_profile = await memory_service.get_user_profile(user_id)
                
                if user_profile and user_profile.is_ej_community and user_profile.location:
                    # Get EJ community data
                    ej_data = await ej_geospatial_tool.run(
                        action="get_community_profile",
                        city=user_profile.location
                    )
                    
                    if ej_data:
                        context.append({
                            "source": "ej_data",
                            "content": f"The user is from {user_profile.location}, which is an Environmental Justice community with the following characteristics: {json.dumps(ej_data)}",
                            "metadata": {"type": "ej_community_data"},
                            "relevance_score": 0.9  # High relevance for personalized data
                        })
            except Exception as e:
                # Log the error but continue
                print(f"Error getting EJ data: {str(e)}")
            
            # If we have international professional data, add it to the context
            try:
                if user_profile and user_profile.has_international_credentials and user_profile.origin_country:
                    # Get international credential data
                    credential_data = user_profile.international_credentials
                    
                    if credential_data:
                        context.append({
                            "source": "international_data",
                            "content": f"The user is an international professional from {user_profile.origin_country} with credentials that may need evaluation: {json.dumps(credential_data)}",
                            "metadata": {"type": "international_credential_data"},
                            "relevance_score": 0.9  # High relevance for personalized data
                        })
            except Exception as e:
                # Log the error but continue
                print(f"Error getting international data: {str(e)}")
            
            # Sort by relevance score
            context.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Limit to top 5 most relevant items
            context = context[:5]
            
            # Cache the context in Redis if available
            try:
                cache_key = f"context:{user_id}:{query}"
                await redis_service.set(cache_key, context, 3600)  # Cache for 1 hour
            except RedisServiceError:
                # Continue if Redis is unavailable
                pass
            
            # End the trace with the final context
            trace_run.end(outputs={
                "context_count": len(context),
                "sources": [item["source"] for item in context]
            })
            
            return context
    except Exception as e:
        print(f"Error getting relevant context: {str(e)}")
        # If there's an error, return an empty context
        return []

async def chat_completion_with_streaming(query: str, user_id: str, stream_tokens: bool = False):
    """Generate a chat completion with optional streaming"""
    # Create a run ID for tracing
    run_id = tracing_service.create_run_id()
    
    try:
        # Create a trace for the chat completion
        with tracing_service.trace(
            name="climate_chat_completion",
            run_id=run_id,
            inputs={"query": query, "user_id": user_id, "stream_tokens": stream_tokens}
        ) as trace_run:
            start_time = time.time()
            
            # Get relevant context
            context = await get_relevant_context(query, user_id, run_id)
            
            # Format context for the prompt
            context_text = ""
            for item in context:
                source = item["source"]
                content = item["content"]
                context_text += f"[{source}]\n{content}\n\n"
            
            # Create messages for the chat completion
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"Context information:\n{context_text}"},
                {"role": "user", "content": query}
            ]
            
            # Generate completion
            if stream_tokens:
                # Stream the response
                completion_stream = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    stream=True
                )
                
                # Define the generator function for streaming
                async def generate():
                    try:
                        # Start the response
                        yield "data: {\"type\": \"start\", \"run_id\": \"" + run_id + "\"}\n\n"
                        
                        # Stream the tokens
                        full_response = ""
                        for chunk in completion_stream:
                            if chunk.choices and chunk.choices[0].delta.content:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                        
                        # End the response
                        end_time = time.time()
                        duration_ms = int((end_time - start_time) * 1000)
                        
                        # Store the response in memory
                        try:
                            memory_entry = ClimateMemoryEntry(
                                content=full_response,
                                user_id=user_id,
                                category="chat",
                                metadata={
                                    "query": query,
                                    "timestamp": time.time(),
                                    "context_sources": [item["source"] for item in context]
                                }
                            )
                            await memory_service.add_memory(memory_entry)
                        except MemoryServiceError as e:
                            print(f"Error storing chat in memory: {str(e)}")
                        
                        # End the trace
                        trace_run.end(outputs={
                            "response_length": len(full_response),
                            "response_time_ms": duration_ms
                        })
                        
                        yield f"data: {json.dumps({'type': 'end', 'duration_ms': duration_ms})}\n\n"
                    except Exception as e:
                        error_msg = str(e)
                        print(f"Error in streaming: {error_msg}")
                        yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                
                return generate()
            else:
                # Generate the full response at once
                completion = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7
                )
                
                response = completion.choices[0].message.content
                
                # Store the response in memory
                try:
                    memory_entry = ClimateMemoryEntry(
                        content=response,
                        user_id=user_id,
                        category="chat",
                        metadata={
                            "query": query,
                            "timestamp": time.time(),
                            "context_sources": [item["source"] for item in context]
                        }
                    )
                    await memory_service.add_memory(memory_entry)
                except MemoryServiceError as e:
                    print(f"Error storing chat in memory: {str(e)}")
                
                # End the trace
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                trace_run.end(outputs={
                    "response_length": len(response),
                    "response_time_ms": duration_ms
                })
                
                return {
                    "response": response,
                    "run_id": run_id,
                    "duration_ms": duration_ms
                }
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat completion: {error_msg}")
        return {
            "error": "Error generating response",
            "message": error_msg
        }

@app.post("/api/climate-chat")
async def climate_chat(request: Request):
    """API endpoint for climate chat"""
    try:
        # Parse request
        data = await request.json()
        query = data.get("query")
        user_id = data.get("user_id")
        stream_tokens = data.get("stream_tokens", False)
        
        # Validate request
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Generate response
        if stream_tokens:
            # Return streaming response
            return StreamingResponse(
                chat_completion_with_streaming(query, user_id, True),
                media_type="text/event-stream"
            )
        else:
            # Return regular response
            return await chat_completion_with_streaming(query, user_id, False)
    except Exception as e:
        # Handle errors
        error_msg = str(e)
        print(f"Error in climate chat endpoint: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
