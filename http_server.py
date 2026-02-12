#!/usr/bin/env python3
"""
HTTP Server wrapper for MalayLanguage MCP Server

Provides HTTP/SSE streaming support at /sse endpoint.
"""

import asyncio
import logging
import os
from typing import Any

import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, PlainTextResponse

from server import app as mcp_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("malaylanguage-http")


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
        "mcp_endpoint": "/sse",
        "post_endpoint": "/messages",
        "health_endpoint": "/health",
        "documentation": "https://github.com/zairulanuar/MalayLanguage"
    })


async def handle_sse(request):
    """Handle SSE connections for MCP protocol."""
    sse = SseServerTransport("/messages")
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await mcp_app.run(read_stream, write_stream, mcp_app.create_initialization_options())
    return PlainTextResponse("SSE connection closed")


async def handle_post_messages(request):
    """Handle POST messages for MCP protocol."""
    # This is a simpler approach - create transport per request
    sse = SseServerTransport("/messages")
    return await sse.handle_post_message(request)


# Create Starlette app
routes = [
    Route("/", endpoint=root_handler, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/messages", endpoint=handle_post_messages, methods=["POST"]),
]

http_app = Starlette(routes=routes)


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the HTTP server."""
    logger.info(f"Starting MalayLanguage MCP HTTP server on {host}:{port}")
    logger.info(f"MCP SSE endpoint available at http://{host}:{port}/sse")
    logger.info(f"Health check available at http://{host}:{port}/health")
    uvicorn.run(http_app, host=host, port=port)


if __name__ == "__main__":
    import sys
    
    # Support environment variables for deployment platforms
    host = os.getenv("HOST", sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0")
    port = int(os.getenv("PORT", sys.argv[2] if len(sys.argv) > 2 else "8000"))
    
    start_server(host, port)
