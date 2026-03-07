"""
MCP Tool Connections

This module provides connections to the custom MCP server (location-analyzer)
deployed on Cloud Run.

Connection Pattern: StreamableHTTP
- Uses StreamableHTTPConnectionParams for HTTP-based MCP communication
- The MCP endpoint is at: {MCP_SERVER_URL}/mcp
- This is the CUSTOM MCP pattern (vs. Google Cloud MCP servers which are managed by Google)

The MCP server provides:
- analyze_geological: Soil sample analysis via Gemini Vision
- analyze_botanical: Flora recording analysis via Gemini multimodal

Configuration: Uses MCP_SERVER_URL environment variable
- Set by sourcing set_env.sh after deploying the MCP server
- Or passed as env var in Cloud Run deployment
"""

import os
import logging

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)


# =============================================================================
# MCP SERVER CONFIGURATION
# =============================================================================

# Get MCP server URL from environment
# This should be set to your Cloud Run service URL
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL")

def _make_mcp_toolset():
    """Create a fresh MCPToolset instance connected to the location-analyzer server."""
    if not MCP_SERVER_URL:
        raise ValueError(
            "MCP_SERVER_URL environment variable not set.\n"
            "Please set MCP_SERVER_URL to your Cloud Run service URL."
        )

    mcp_endpoint = f"{MCP_SERVER_URL}/mcp"
    logger.info(f"[MCP Tools] Connecting to: {mcp_endpoint}")

    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=mcp_endpoint,
            timeout=120,
        )
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================
# Each parallel agent gets its OWN MCPToolset instance.
# Sharing a singleton across parallel agents causes "Unexpected tool call" errors.

def get_geological_tool():
    """
    Get a fresh MCPToolset for the geological analysis tool.
    Creates a new instance so parallel agents don't share a connection.
    """
    return _make_mcp_toolset()


def get_botanical_tool():
    """
    Get a fresh MCPToolset for the botanical analysis tool.
    Creates a new instance so parallel agents don't share a connection.
    """
    return _make_mcp_toolset()
