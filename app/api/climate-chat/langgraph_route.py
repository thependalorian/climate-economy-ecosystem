#!/usr/bin/env python3
"""
API endpoint for the Climate Economy Ecosystem Agent Workflow

This module provides the API endpoint for the agent workflow using LangGraph's
Functional API. It supports both regular and streaming responses.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# Import the agent workflow
from lib.agents.agent_workflow import agent_chat, agent_chat_stream

# Import services
from lib.memory.memory_service import MemoryService, MemoryServiceError
from lib.redis.redis_service import RedisService, RedisServiceError
from lib.tracing.langsmith_service import TracingService, TracingServiceError

# Initialize services
memory_service = MemoryService()
redis_service = RedisService()
tracing_service = TracingService()

# Create router
router = APIRouter()

# Request models
class ChatRequest(BaseModel):
    """Chat request model"""
    user_id: str = Field(..., description="User ID")
    query: str = Field(..., description="User query")
    session_id: Optional[str] = Field(None, description="Session ID (optional)")
    agent_type: Optional[str] = Field(None, description="Force specific agent type (optional)")
    stream: bool = Field(False, description="Whether to stream the response")

# Response models
class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Agent response")
    agent_type: str = Field(..., description="Agent type used")
    agent_name: str = Field(..., description="Agent name")
    session_id: str = Field(..., description="Session ID")
    interaction_id: str = Field(..., description="Interaction ID")
    timestamp: str = Field(..., description="Timestamp")

async def generate_streaming_response(result) -> AsyncGenerator[str, None]:
    """
    Generate a streaming response from the agent workflow.
    
    Args:
        result: The streaming result from the agent workflow
        
    Yields:
        JSON-encoded chunks of the response
    """
    for chunk in result:
        # Check if the chunk is from the custom stream
        if chunk[0] == "custom":
            data = chunk[1]
            if isinstance(data, dict):
                # If it's a token, yield it
                if "token" in data:
                    yield f"data: {json.dumps({'type': 'token', 'content': data['token'], 'agent_type': data.get('agent_type'), 'agent_name': data.get('agent_name')})}\n\n"
                # If it's a status update, yield it
                elif "status" in data:
                    yield f"data: {json.dumps({'type': 'status', 'status': data['status'], 'agent_type': data.get('agent_type'), 'agent_name': data.get('agent_name')})}\n\n"
            elif isinstance(data, str):
                yield f"data: {json.dumps({'type': 'message', 'content': data})}\n\n"
        # Check if the chunk is from the updates stream (final result)
        elif chunk[0] == "updates" and "agent_chat_stream" in chunk[1]:
            result = chunk[1]["agent_chat_stream"]
            yield f"data: {json.dumps({'type': 'final', 'result': result})}\n\n"
    
    # End the stream
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

@router.post("/api/climate-chat/langgraph")
async def chat_with_langgraph(request: ChatRequest) -> JSONResponse:
    """
    Chat with the agent workflow using LangGraph.
    
    Args:
        request: The chat request
        
    Returns:
        JSON response with the agent's response or a streaming response
    """
    # Create a run ID for tracing
    run_id = tracing_service.create_run_id()
    
    try:
        # Create a trace for the API call
        with tracing_service.trace(
            name="chat_with_langgraph_api",
            run_id=run_id,
            inputs=request.dict()
        ) as trace:
            # Generate session ID if not provided
            session_id = request.session_id or str(uuid.uuid4())
            
            # Create the config with thread ID
            config = {
                "configurable": {
                    "thread_id": session_id
                }
            }
            
            # Create the inputs
            inputs = {
                "user_id": request.user_id,
                "query": request.query,
                "session_id": session_id,
                "agent_type": request.agent_type
            }
            
            # Check if streaming is requested
            if request.stream:
                # Use the streaming version of the workflow
                result = agent_chat_stream.stream(
                    inputs,
                    config=config,
                    stream_mode=["custom", "updates"]
                )
                
                # Return a streaming response
                return StreamingResponse(
                    generate_streaming_response(result),
                    media_type="text/event-stream"
                )
            else:
                # Use the regular version of the workflow
                result = await agent_chat.ainvoke(inputs, config=config)
                
                # Create the response
                chat_response = ChatResponse(
                    response=result["response"],
                    agent_type=result["agent_type"],
                    agent_name=result["agent_name"],
                    session_id=result["session_id"],
                    interaction_id=result["interaction_id"],
                    timestamp=result["timestamp"]
                )
                
                trace.end(outputs={
                    "agent_type": result["agent_type"],
                    "agent_name": result["agent_name"],
                    "response_length": len(result["response"])
                })
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=chat_response.dict()
                )
            
    except MemoryServiceError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Memory service error: {str(e)}"}
        )
    except RedisServiceError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Redis service error: {str(e)}"}
        )
    except TracingServiceError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Tracing service error: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Unexpected error: {str(e)}"}
        )

@router.post("/api/climate-chat/langgraph/resume")
async def resume_chat(
    session_id: str,
    feedback: Dict[str, Any]
) -> JSONResponse:
    """
    Resume a chat that was interrupted for human feedback.
    
    Args:
        session_id: The session ID
        feedback: The human feedback
        
    Returns:
        JSON response with the agent's response
    """
    try:
        # Create the config with thread ID
        config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        # Resume the workflow with the feedback
        from langgraph.types import Command
        result = await agent_chat.ainvoke(Command(resume=feedback), config=config)
        
        # Create the response
        chat_response = ChatResponse(
            response=result["response"],
            agent_type=result["agent_type"],
            agent_name=result["agent_name"],
            session_id=result["session_id"],
            interaction_id=result["interaction_id"],
            timestamp=result["timestamp"]
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=chat_response.dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Unexpected error: {str(e)}"}
        )
