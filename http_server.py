#!/usr/bin/env python3
"""
HTTP Server wrapper for MalayLanguage MCP Server

Provides HTTP/SSE streaming support at /mcp endpoint.
"""

import asyncio
import logging
import os
from typing import Any

import uvicorn
from mcp.server.sse import sse_server
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from sse_starlette import EventSourceResponse

from server import app as mcp_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("malaylanguage-http")


async def handle_sse(request):
    """Handle SSE connections for MCP protocol."""
    async with sse_server() as (read_stream, write_stream):
        await mcp_app.run(
            read_stream, 
            write_stream, 
            mcp_app.create_initialization_options()
        )


async def handle_messages(request):
    """Handle MCP messages over HTTP."""
    return EventSourceResponse(handle_sse(request))


async def health_check(request):
    """Health check endpoint for deployment platforms."""
    return JSONResponse({
        "status": "healthy",
        "service": "malaylanguage-mcp-server",
        "version": "1.0.0"
    })


async def root_handler(request):
    """Root endpoint with service information."""
    return JSONResponse({
        "service": "MalayLanguage MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health",
        "documentation": "https://github.com/zairulanuar/MalayLanguage"
    })


# Create Starlette app
routes = [
    Route("/", endpoint=root_handler, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Route("/mcp", endpoint=handle_messages, methods=["GET", "POST"]),
]

http_app = Starlette(routes=routes)


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the HTTP server."""
    logger.info(f"Starting MalayLanguage MCP HTTP server on {host}:{port}")
    logger.info(f"MCP endpoint available at http://{host}:{port}/mcp")
    logger.info(f"Health check available at http://{host}:{port}/health")
    uvicorn.run(http_app, host=host, port=port)


if __name__ == "__main__":
    import sys
    
    # Support environment variables for deployment platforms
    host = os.getenv("HOST", sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0")
    port = int(os.getenv("PORT", sys.argv[2] if len(sys.argv) > 2 else "8000"))
    
    start_server(host, port)
