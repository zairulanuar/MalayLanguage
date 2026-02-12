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
from server import (
    detect_language, normalize_malay, correct_spelling, 
    apply_glossary, rewrite_style, translate, term_lookup
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("malaylanguage-http")


async def health_check(request):
    """Health check endpoint for deployment platforms."""
    try:
        # Quick health check that doesn't load models
        return JSONResponse({
            "status": "healthy",
            "service": "malaylanguage-mcp-server",
            "version": "1.0.0",
            "timestamp": asyncio.get_event_loop().time()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)


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


async def handle_tool_execute(request):
    """Execute a tool directly via HTTP POST."""
    try:
        data = await request.json()
        name = data.get("name")
        arguments = data.get("arguments", {})
        
        if not name:
            return JSONResponse({"error": "Tool name is required"}, status_code=400)
            
        result = []
        if name == "detect_language":
            result = await detect_language(arguments.get("text", ""))
        elif name == "normalize_malay":
            result = await normalize_malay(arguments.get("text", ""))
        elif name == "correct_spelling":
            result = await correct_spelling(arguments.get("text", ""))
        elif name == "apply_glossary":
            result = await apply_glossary(arguments.get("term", ""))
        elif name == "rewrite_style":
            result = await rewrite_style(
                arguments.get("text", ""),
                arguments.get("style", "formal")
            )
        elif name == "translate":
            result = await translate(
                arguments.get("text", ""),
                arguments.get("source_lang", "ms"),
                arguments.get("target_lang", "en")
            )
        elif name == "term_lookup":
            result = await term_lookup(arguments.get("term", ""))
        else:
            return JSONResponse({"error": f"Unknown tool: {name}"}, status_code=400)
            
        # Result is list[TextContent]. Convert to JSON.
        return JSONResponse({
            "tool": name,
            "result": [
                {"type": c.type, "text": c.text} for c in result
            ]
        })
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# Create Starlette app
routes = [
    Route("/", endpoint=root_handler, methods=["GET"]),
    Route("/health", endpoint=health_check, methods=["GET"]),
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/messages", endpoint=handle_post_messages, methods=["POST"]),
    Route("/tools/execute", endpoint=handle_tool_execute, methods=["POST"]),
]

http_app = Starlette(routes=routes)


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the HTTP server."""
    logger.info(f"Starting MalayLanguage MCP HTTP server on {host}:{port}")
    logger.info(f"MCP SSE endpoint available at http://{host}:{port}/sse")
    logger.info(f"Health check available at http://{host}:{port}/health")
    logger.info("Server initialization complete - ready to accept connections")
    uvicorn.run(http_app, host=host, port=port)


if __name__ == "__main__":
    import sys
    import os
    
    # Support environment variables for deployment platforms
    host = os.getenv("HOST", sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0")
    port = int(os.getenv("PORT", sys.argv[2] if len(sys.argv) > 2 else "8000"))
    
    start_server(host, port)
