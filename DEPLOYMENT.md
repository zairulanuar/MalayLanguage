# Remote Deployment Guide

This guide explains how to deploy and connect to the MalayLanguage MCP Server **without** installing it locally on your machine.

## Table of Contents

- [Quick Start](#quick-start)
- [Deployment Options](#deployment-options)
  - [Cloud Platforms](#cloud-platforms)
  - [Docker Compose](#docker-compose)
  - [Pre-built Docker Image](#pre-built-docker-image)
- [Connecting Your App](#connecting-your-app)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

The fastest way to use this MCP server remotely:

1. **Deploy to a cloud platform** (Railway, Render, or Fly.io)
2. **Get your server URL** (e.g., `https://your-app.railway.app`)
3. **Configure your MCP client** to use the HTTP endpoint

---

## Deployment Options

### Cloud Platforms

#### Railway (Recommended)

Railway provides automatic deployments from GitHub with zero configuration.

**Step 1: Deploy to Railway**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/malaylanguage)

Or manually:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize and deploy
railway init
railway up
```

**Step 2: Get Your URL**

After deployment, Railway provides a URL like: `https://malaylanguage-mcp-production.up.railway.app`

**Step 3: Configure Your MCP Client**

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-app.railway.app/sse",
      "transport": "http"
    }
  }
}
```

---

#### Render

Render offers free tier with automatic deployments.

**Step 1: Deploy to Render**

1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your forked repository
5. Render will auto-detect the `render.yaml` configuration
6. Click "Create Web Service"

**Step 2: Access Your Service**

Render provides a URL like: `https://malaylanguage-mcp.onrender.com`

**Step 3: Configure Your Client**

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://malaylanguage-mcp.onrender.com/sse",
      "transport": "http"
    }
  }
}
```

---

#### Fly.io

Fly.io provides edge deployment with global regions.

**Step 1: Install Fly CLI**

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Windows
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Step 2: Deploy**

```bash
# Login
fly auth login

# Launch the app (uses fly.toml config)
fly launch

# Deploy
fly deploy
```

**Step 3: Get Your URL**

```bash
fly status
# Shows: https://malaylanguage-mcp.fly.dev
```

**Step 4: Configure Your Client**

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://malaylanguage-mcp.fly.dev/sse",
      "transport": "http"
    }
  }
}
```

---

### Docker Compose

For local or server deployment with persistent storage.

**Step 1: Start the Server**

```bash
# Clone the repository
git clone https://github.com/zairulanuar/MalayLanguage.git
cd MalayLanguage

# Start with Docker Compose
docker-compose up -d
```

The server will be available at `http://localhost:8000`

**Step 2: Configure Your Client**

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "http://localhost:8000/sse",
      "transport": "http"
    }
  }
}
```

**Management Commands**

```bash
# View logs
docker-compose logs -f

# Stop the server
docker-compose down

# Restart the server
docker-compose restart

# Update to latest version
docker-compose pull
docker-compose up -d
```

---

### Pre-built Docker Image

Use the official pre-built image from GitHub Container Registry.

**Step 1: Run the Container**

```bash
# Pull the latest image
docker pull ghcr.io/zairulanuar/malaylanguage:latest

# Run in HTTP mode
docker run -d \
  --name malaylanguage-mcp \
  -p 8000:8000 \
  ghcr.io/zairulanuar/malaylanguage:latest \
  python http_server.py

# Check if it's running
docker ps
```

**Step 2: Test the Connection**

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"healthy","service":"malaylanguage-mcp-server","version":"1.0.0"}
```

**Step 3: Configure Your Client**

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "http://localhost:8000/sse",
      "transport": "http"
    }
  }
}
```

---

## Connecting Your App

### Claude Desktop

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the remote server configuration:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-deployed-app.com/sse",
      "transport": "http"
    }
  }
}
```

Restart Claude Desktop.

---

### VS Code / Cursor

Create or edit `.vscode/sse.json` in your project:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-deployed-app.com/sse",
      "transport": "http",
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

Reload the window.

---

### Custom MCP Client

Use the MCP SDK to connect to the HTTP endpoint:

**Python Example**

```python
from mcp.client.http import HttpClient

async def main():
    async with HttpClient("https://your-deployed-app.com/sse") as client:
        # List available tools
        tools = await client.list_tools()
        
        # Call a tool
        result = await client.call_tool(
            "translate",
            arguments={
                "text": "Hello, how are you?",
                "source_lang": "en",
                "target_lang": "ms"
            }
        )
        print(result)
```

**JavaScript Example**

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const transport = new SSEClientTransport(
  "https://your-deployed-app.com/sse"
);
const client = new Client({ name: "my-app", version: "1.0.0" }, {});

await client.connect(transport);

// List tools
const tools = await client.listTools();

// Call a tool
const result = await client.callTool({
  name: "translate",
  arguments: {
    text: "Hello",
    source_lang: "en",
    target_lang: "ms"
  }
});
```

---

## Environment Variables

Configure the server using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `MALAYA_CACHE` | Model cache directory | `~/.malaya` |
| `PYTHONUNBUFFERED` | Disable Python output buffering | `1` |

**Example:**

```bash
export HOST=0.0.0.0
export PORT=3000
export MALAYA_CACHE=/path/to/cache
python http_server.py
```

---

## Available Endpoints

Once deployed, your server provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health check for monitoring |
| `/sse` | GET/POST | MCP protocol endpoint (SSE) |

**Test the endpoints:**

```bash
# Service info
curl https://your-app.com/

# Health check
curl https://your-app.com/health
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to the server

**Solutions**:
1. Verify the server is running: `curl https://your-app.com/health`
2. Check firewall rules and port accessibility
3. Ensure the URL includes `/sse` endpoint
4. Check server logs for errors

### Cold Start Delays

**Problem**: First request is slow on cloud platforms

**Explanation**: Free tier platforms may sleep after inactivity. The first request wakes the server and loads ML models.

**Solutions**:
1. Use a paid tier with always-on instances
2. Implement a keep-alive ping service
3. Use Railway or Render's always-on feature

### Model Loading Errors

**Problem**: Models fail to download or load

**Solutions**:
1. Ensure sufficient disk space (models are ~500MB+)
2. Check internet connectivity from the server
3. Verify `MALAYA_CACHE` directory permissions
4. For Docker: ensure volume is properly mounted

### Memory Issues

**Problem**: Server crashes with out-of-memory errors

**Solutions**:
1. Increase server memory allocation (min 1GB recommended)
2. Use a platform with higher memory limits
3. Reduce concurrent requests

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Persistent Storage |
|----------|-----------|-----------|-------------------|
| Railway | 500h/month | $5+/month | ✅ Yes |
| Render | 750h/month | $7+/month | ✅ Yes |
| Fly.io | 3 VMs free | $0.02/GB-hr | ✅ Yes |
| Docker Local | ✅ Free | N/A | ✅ Yes |

---

## Next Steps

1. **Deploy** the server to your preferred platform
2. **Configure** your MCP client with the server URL
3. **Test** the connection with a simple tool call
4. **Monitor** using the `/health` endpoint
5. **Scale** as needed based on usage

For issues and support, visit: https://github.com/zairulanuar/MalayLanguage/issues
