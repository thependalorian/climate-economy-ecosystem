#!/usr/bin/env python3
"""
Base Tool for Climate Economy Ecosystem

This module provides a base class for all tools in the climate economy ecosystem.
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ToolError(Exception):
    """Base exception for tool errors"""
    pass

class ToolUnavailableError(ToolError):
    """Exception raised when a tool is unavailable"""
    pass

class ToolConfigurationError(ToolError):
    """Exception raised when a tool is misconfigured"""
    pass

class ToolExecutionError(ToolError):
    """Exception raised when a tool execution fails"""
    pass

class BaseTool(ABC):
    """Base class for all climate economy ecosystem tools"""

    def __init__(self, supabase_client=None, openai_client=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the tool with optional clients and configuration

        Args:
            supabase_client: Supabase client instance
            openai_client: OpenAI client instance
            config: Tool configuration
        """
        # Import here to avoid circular imports
        from utils import get_supabase_client, get_openai_client

        self.supabase = supabase_client or get_supabase_client()
        self.openai = openai_client or get_openai_client()
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Check if required clients are available
        if self.requires_supabase() and not self.supabase:
            self.logger.warning(f"{self.__class__.__name__} requires Supabase but client is not available")

        if self.requires_openai() and not self.openai:
            self.logger.warning(f"{self.__class__.__name__} requires OpenAI but client is not available")

    def requires_supabase(self) -> bool:
        """
        Check if this tool requires Supabase

        Returns:
            True if this tool requires Supabase, False otherwise
        """
        return False

    def requires_openai(self) -> bool:
        """
        Check if this tool requires OpenAI

        Returns:
            True if this tool requires OpenAI, False otherwise
        """
        return False

    async def initialize(self) -> None:
        """
        Initialize any resources needed by the tool

        Raises:
            ToolConfigurationError: If the tool is misconfigured
        """
        self.logger.info(f"Initializing {self.__class__.__name__}")

        # Check if required clients are available
        if self.requires_supabase() and not self.supabase:
            raise ToolConfigurationError(f"{self.__class__.__name__} requires Supabase but client is not available")

        if self.requires_openai() and not self.openai:
            raise ToolConfigurationError(f"{self.__class__.__name__} requires OpenAI but client is not available")

    async def cleanup(self) -> None:
        """
        Clean up any resources used by the tool
        """
        self.logger.info(f"Cleaning up {self.__class__.__name__}")

    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the tool with the given arguments

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Dict containing the results

        Raises:
            ToolExecutionError: If the tool execution fails
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the tool

        Returns:
            Dict containing health check results
        """
        return {
            "name": self.__class__.__name__,
            "status": "available",
            "requires_supabase": self.requires_supabase(),
            "requires_openai": self.requires_openai(),
            "supabase_available": self.supabase is not None if self.requires_supabase() else None,
            "openai_available": self.openai is not None if self.requires_openai() else None
        }

    def _check_availability(self) -> None:
        """
        Check if the tool is available

        Raises:
            ToolUnavailableError: If the tool is not available
        """
        if self.requires_supabase() and not self.supabase:
            raise ToolUnavailableError(f"{self.__class__.__name__} requires Supabase but client is not available")

        if self.requires_openai() and not self.openai:
            raise ToolUnavailableError(f"{self.__class__.__name__} requires OpenAI but client is not available")
