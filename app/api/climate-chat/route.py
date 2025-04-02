from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
import json
import os
import time
import openai
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import asyncio
from ....lib.memory.mem0_service import MemoryService, ClimateMemoryEntry
from ....lib.tools.web_search import WebSearchTool, WebSearchParams
from ....lib.tools.db_retriever import DBRetrieverTool, DBRetrieverParams
from ....lib.monitoring.metrics_service import MetricsService
import langsmith
from langsmith import Client as LangSmithClient

# Load environment variables
load_dotenv()

# Initialize services
memory_service = MemoryService()
web_search_tool = WebSearchTool()
db_retriever_tool = DBRetrieverTool()
metrics_service = MetricsService()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize LangSmith client
langsmith_client = LangSmithClient(
    api_key=os.environ.get("LANGSMITH_API_KEY"),
    api_url="https://api.smith.langchain.com"
)

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
    
    # Create a child run in LangSmith if a run_id is provided
    if run_id:
        with langsmith_client.trace(
            name="get_relevant_context",
            run_id=run_id,
            run_type="chain",
            inputs={"query": query, "user_id": user_id}
        ) as child_run:
            try:
                context = []
                
                # First, try to get information from our database
                with langsmith_client.trace(
                    name="db_retrieval",
                    run_id=child_run.id,
                    run_type="retriever",
                    inputs={"query": query}
                ) as db_run:
                    db_params = DBRetrieverParams(
                        query=query,
                        user_id=user_id,
                        categories=["report", "job", "training"],
                        limit=3,
                        threshold=0.6
                    )
                    
                    db_results = await db_retriever_tool.retrieve(db_params)
                    
                    # Add database results to context
                    for result in db_results:
                        context.append({
                            "source": "database",
                            "content": result.content,
                            "metadata": result.metadata,
                            "relevance_score": result.relevance_score or 0.0
                        })
                    
                    # Update the run with outputs
                    db_run.end(
                        outputs={
                            "result_count": len(db_results),
                            "results": [r.content[:100] + "..." for r in db_results]
                        }
                    )
                
                # Then, supplement with web search if needed
                if len(context) < 3:
                    with langsmith_client.trace(
                        name="web_search",
                        run_id=child_run.id,
                        run_type="retriever",
                        inputs={"query": query, "location": "Massachusetts"}
                    ) as web_run:
                        search_params = WebSearchParams(
                            query=query,
                            num_results=3,
                            location="Massachusetts"
                        )
                        
                        web_results = await web_search_tool.search(search_params)
                        
                        # Add web results to context
                        for result in web_results:
                            context.append({
                                "source": "web",
                                "content": f"Title: {result.title}\nSnippet: {result.snippet}\nURL: {result.url}",
                                "metadata": {"url": result.url},
                                "relevance_score": result.score
                            })
                        
                        # Update the run with outputs
                        web_run.end(
                            outputs={
                                "result_count": len(web_results),
                                "results": [r.title for r in web_results]
                            }
                        )
                
                # Sort by relevance score
                context.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                # Limit to top 5 most relevant items
                context = context[:5]
                
                # End the parent run with the final context
                child_run.end(
                    outputs={
                        "context_count": len(context),
                        "sources": [item["source"] for item in context]
                    }
                )
                
                return context
            except Exception as e:
                # End the run with error if something goes wrong
                child_run.end(error=str(e))
                raise
    else:
        # Original implementation when not using LangSmith tracing
        context = []
        
        # First, try to get information from our database
        db_params = DBRetrieverParams(
            query=query,
            user_id=user_id,
            categories=["report", "job", "training"],
            limit=3,
            threshold=0.6
        )
        
        db_results = await db_retriever_tool.retrieve(db_params)
        
        # Add database results to context
        for result in db_results:
            context.append({
                "source": "database",
                "content": result.content,
                "metadata": result.metadata,
                "relevance_score": result.relevance_score or 0.0
            })
        
        # Then, supplement with web search if needed
        if len(context) < 3:
            search_params = WebSearchParams(
                query=query,
                num_results=3,
                location="Massachusetts"
            )
            
            web_results = await web_search_tool.search(search_params)
            
            # Add web results to context
            for result in web_results:
                context.append({
                    "source": "web",
                    "content": f"Title: {result.title}\nSnippet: {result.snippet}\nURL: {result.url}",
                    "metadata": {"url": result.url},
                    "relevance_score": result.score
                })
        
        # Sort by relevance score
        context.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Limit to top 5 most relevant items
        return context[:5]

async def chat_completion_with_streaming(query: str, user_id: str, stream_tokens: bool = False):
    """Generate a chat completion with optional streaming"""
    start_time = time.time()
    
    # Create a run in LangSmith
    run_id = str(uuid.uuid4())
    
    with langsmith_client.trace(
        name="climate_chat_completion",
        run_id=run_id,
        run_type="llm",
        inputs={"query": query, "user_id": user_id, "stream": stream_tokens}
    ) as run:
        try:
            # Get relevant context
            context = await get_relevant_context(query, user_id, run_id)
            
            # Track search metrics
            await metrics_service.track_search_event(
                user_id=user_id,
                query=query,
                db_results_count=len([c for c in context if c["source"] == "database"]),
                web_results_count=len([c for c in context if c["source"] == "web"])
            )
            
            # Format context for the prompt
            context_text = "\n\n".join([f"Source: {item['source']}\n{item['content']}" for item in context])
            
            # Create the messages for the chat completion
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Massachusetts Clean Energy Query: {query}\n\nRelevant Context:\n{context_text}"}
            ]
            
            # Track the prompt in LangSmith
            run.update(
                inputs={
                    "messages": [
                        {"role": m["role"], "content": m["content"][:100] + "..." if len(m["content"]) > 100 else m["content"]}
                        for m in messages
                    ]
                }
            )
            
            # Execute the chat completion
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                stream=stream_tokens,
                temperature=0.7,
                max_tokens=1024
            )
            
            if stream_tokens:
                # Streaming response
                async def generate():
                    full_response = ""
                    token_count = 0
                    
                    # Yield the start of the JSON
                    yield b'{"text":"'
                    
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            token_count += 1
                            
                            # Escape special characters in JSON
                            content_json = json.dumps(content)[1:-1]
                            yield content_json.encode('utf-8')
                    
                    # Yield the end of the JSON
                    yield b'", "sources": '
                    yield json.dumps([{
                        "source": item["source"],
                        "url": item.get("metadata", {}).get("url", ""),
                        "relevance": item.get("relevance_score", 0)
                    } for item in context]).encode('utf-8')
                    yield b'}'
                    
                    # Store the chat in memory
                    await memory_service.add_memory(ClimateMemoryEntry(
                        content=f"Q: {query}\nA: {full_response}",
                        user_id=user_id,
                        category="conversation",
                        source="assistant"
                    ))
                    
                    # Track metrics
                    end_time = time.time()
                    duration_ms = int((end_time - start_time) * 1000)
                    await metrics_service.track_chat_completion(
                        user_id=user_id,
                        query=query,
                        response_time_ms=duration_ms,
                        token_count=token_count
                    )
                    
                    # Complete the LangSmith run
                    run.end(
                        outputs={
                            "response_length": len(full_response),
                            "token_count": token_count,
                            "duration_ms": duration_ms
                        }
                    )
                    
                return StreamingResponse(generate(), media_type="application/json")
            else:
                # Non-streaming response
                full_response = response.choices[0].message.content
                token_count = len(full_response.split())
                
                # Store the chat in memory
                await memory_service.add_memory(ClimateMemoryEntry(
                    content=f"Q: {query}\nA: {full_response}",
                    user_id=user_id,
                    category="conversation",
                    source="assistant"
                ))
                
                # Track metrics
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                await metrics_service.track_chat_completion(
                    user_id=user_id,
                    query=query,
                    response_time_ms=duration_ms,
                    token_count=token_count
                )
                
                # Complete the LangSmith run
                run.end(
                    outputs={
                        "response": full_response[:100] + "...",
                        "response_length": len(full_response),
                        "token_count": token_count,
                        "duration_ms": duration_ms
                    }
                )
                
                return {
                    "text": full_response,
                    "sources": [{
                        "source": item["source"],
                        "url": item.get("metadata", {}).get("url", ""),
                        "relevance": item.get("relevance_score", 0)
                    } for item in context]
                }
        except Exception as e:
            # Track error
            await metrics_service.track_error(
                user_id=user_id,
                error_type="chat_completion_error",
                error_message=str(e),
                context={"query": query}
            )
            
            # End the LangSmith run with error
            run.end(error=str(e))
            
            raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/api/climate-chat")
async def climate_chat(request: Request):
    """API endpoint for climate chat"""
    try:
        body = await request.json()
        query = body.get("query")
        user_id = body.get("user_id")
        stream_tokens = body.get("stream", False)
        
        if not query or not user_id:
            raise HTTPException(status_code=400, detail="Missing required fields: query and user_id")
        
        return await chat_completion_with_streaming(query, user_id, stream_tokens)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}") 