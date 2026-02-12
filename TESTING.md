# Testing Your Remote MCP Server Connection

This guide helps you verify that your remotely deployed MalayLanguage MCP server is working correctly.

## Automated Connection Test

Use the included test script for a quick verification:

```bash
# Test a remote deployment
python test_connection.py https://your-app.railway.app

# Test a local deployment
python test_connection.py http://localhost:8000
```

The script will:
- ✅ Test the health check endpoint
- ✅ Verify the root endpoint
- ✅ Check SSE endpoint accessibility
- ✅ Display configuration for your MCP client

## Quick Health Check

After deploying your server, verify it's running:

```bash
# Replace with your actual server URL
curl https://your-app.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "malaylanguage-mcp-server",
  "version": "1.0.0"
}
```

## Test Root Endpoint

Check the service information:

```bash
curl https://your-app.railway.app/
```

**Expected response:**
```json
{
  "service": "MalayLanguage MCP Server",
  "version": "1.0.0",
  "mcp_endpoint": "/sse",
  "post_endpoint": "/messages",
  "health_endpoint": "/health",
  "documentation": "https://github.com/zairulanuar/MalayLanguage"
}
```

## Configure Your MCP Client

### Claude Desktop

1. Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-app.railway.app/sse",
      "transport": "sse"
    }
  }
}
```

3. Restart Claude Desktop

4. Verify the server appears in the available MCP servers list

### VS Code / Cursor

1. Create or open `.vscode/mcp.json` in your project

2. Add the configuration:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://your-app.railway.app/sse",
      "transport": "sse",
      "disabled": false
    }
  }
}
```

3. Reload the VS Code window

### Custom MCP Client

**Python Example:**

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

async def test_malaylanguage_server():
    """Test connection to remote MalayLanguage MCP server."""
    url = "https://your-app.railway.app/sse"
    
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Test translate tool
            result = await session.call_tool(
                "translate",
                arguments={
                    "text": "Hello, how are you?",
                    "source_lang": "en",
                    "target_lang": "ms"
                }
            )
            print(f"Translation result: {result.content[0].text}")

# Run the test
asyncio.run(test_malaylanguage_server())
```

## Test Each Tool

Once connected, test each tool to ensure they're working:

### 1. Language Detection

**Prompt in Claude/Cursor:**
```
Use the detect_language tool to identify the language of this text: "Selamat pagi, apa khabar?"
```

**Expected output:**
```
Language Detection Result:
Language: malay
Confidence: 99.8%

Input text: Selamat pagi, apa khabar?
```

### 2. Normalize Malay Text

**Prompt:**
```
Use the normalize_malay tool to normalize this text: "saya x tau la bro"
```

**Expected output:**
```
Text Normalization Result:

Original: saya x tau la bro

Normalized: saya tidak tahu la abang
```

### 3. Correct Spelling

**Prompt:**
```
Use the correct_spelling tool to fix spelling in: "sya ingin mkan nasi"
```

**Expected output:**
```
Spelling Correction Result:

Original: sya ingin mkan nasi

Corrected: saya ingin makan nasi
```

### 4. Translate

**Prompt:**
```
Use the translate tool to translate "Good morning" from English to Malay
```

**Expected output:**
```
Translation Result:

Source (English): Good morning

Translation (Malay): Selamat pagi
```

### 5. Rewrite Style

**Prompt:**
```
Use the rewrite_style tool to rewrite "Saya nak pergi kedai" in formal style
```

**Expected output:**
```
Style Rewrite Result (Target: formal):

Original: Saya nak pergi kedai

Rewritten: Saya ingin pergi ke kedai
```

### 6. Term Lookup

**Prompt:**
```
Use the term_lookup tool to get information about the term "sekolah"
```

**Expected output:**
```
Term Lookup: sekolah

Language: malay (confidence: 99.9%)
Translation: school

Note: For comprehensive linguistic analysis...
```

### 7. Apply Glossary

**Prompt:**
```
Use the apply_glossary tool to look up "universiti"
```

**Expected output:**
```
Glossary Lookup: universiti

Translation (EN): university

Note: This is a basic translation...
```

## Troubleshooting

### Connection Refused / Timeout

**Problem**: Cannot connect to the server

**Solutions**:
1. Verify the server is deployed and running:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. Check if you're using the correct URL and endpoint (`/sse`)

3. For local deployments, ensure the port is accessible:
   ```bash
   curl http://localhost:8000/health
   ```

### "Server not responding"

**Problem**: Server is deployed but not responding to MCP requests

**Solutions**:
1. Check server logs in your deployment platform (Railway, Render, etc.)

2. Verify environment variables are set correctly:
   - `PORT` should match what your platform expects
   - `HOST` should be `0.0.0.0`

3. Ensure the health check is passing:
   ```bash
   curl -v https://your-app.railway.app/health
   ```

### First Request is Very Slow

**Problem**: The first tool call takes a very long time (30s+)

**Explanation**: This is normal! The Malaya library downloads ML models on first use (~500MB+). Subsequent requests will be fast.

**Solutions**:
1. Be patient on the first request
2. Models are cached, so subsequent requests are fast
3. Use a paid hosting tier to ensure the server doesn't sleep
4. For Docker deployments, mount a persistent volume for the cache

### Tool Returns Error

**Problem**: Tool execution fails with an error message

**Solutions**:
1. Check that you're providing the correct arguments
2. Verify the text input is not empty
3. For translation, ensure source and target languages are different
4. Check server logs for detailed error information

### Models Not Loading

**Problem**: Server starts but models fail to load

**Solutions**:
1. Ensure sufficient disk space (models are ~500MB+ each)
2. Check internet connectivity from the server
3. Verify `MALAYA_CACHE` directory has write permissions
4. For Docker: ensure volume is properly mounted

## Performance Benchmarks

Typical response times (after models are loaded):

| Tool | First Load | Subsequent Calls |
|------|------------|------------------|
| detect_language | ~30s | <1s |
| normalize_malay | ~45s | ~2s |
| correct_spelling | ~60s | ~3s |
| translate | ~60s | ~3s |
| rewrite_style | ~60s | ~3s |
| term_lookup | ~45s | ~2s |
| apply_glossary | ~60s | ~3s |

**Note**: First load times include model download and initialization. Use a persistent volume to avoid re-downloading.

## Monitoring Your Deployment

### Health Check Monitoring

Set up automated monitoring for your deployment:

**Uptime Robot** (free):
```
URL: https://your-app.railway.app/health
Method: GET
Expected: 200 status code
Interval: 5 minutes
```

**Better Uptime**:
```
URL: https://your-app.railway.app/health
Method: GET
Expected Body Contains: "healthy"
```

### Log Monitoring

Check logs regularly to catch issues early:

**Railway**:
```bash
railway logs
```

**Render**:
View logs in the Render dashboard

**Fly.io**:
```bash
fly logs
```

**Docker Compose**:
```bash
docker-compose logs -f malaylanguage-mcp
```

## Advanced Testing

### Load Testing

Test server performance under load:

```bash
# Install Apache Bench
apt-get install apache2-utils  # Ubuntu/Debian
brew install httpd  # macOS

# Test health endpoint
ab -n 100 -c 10 https://your-app.railway.app/health

# Expected: All requests should succeed
```

### Integration Testing

Create automated integration tests:

```python
import asyncio
import pytest
from mcp.client.sse import sse_client
from mcp import ClientSession

@pytest.mark.asyncio
async def test_server_connection():
    """Test basic server connection."""
    url = "https://your-app.railway.app/sse"
    
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert len(tools.tools) == 7

@pytest.mark.asyncio
async def test_translate_tool():
    """Test translation functionality."""
    url = "https://your-app.railway.app/sse"
    
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "translate",
                arguments={
                    "text": "Hello",
                    "source_lang": "en",
                    "target_lang": "ms"
                }
            )
            
            assert "Translation" in result.content[0].text
            assert "Malay" in result.content[0].text
```

Run tests:
```bash
pytest test_remote_server.py -v
```

## Getting Help

If you're still having issues:

1. **Check the logs**: Most issues can be diagnosed from server logs
2. **Verify configuration**: Double-check your MCP client configuration
3. **Test incrementally**: Test health → root → SSE connection → tools
4. **GitHub Issues**: Open an issue at https://github.com/zairulanuar/MalayLanguage/issues

Include in your bug report:
- Deployment platform (Railway, Render, etc.)
- Server URL (without sensitive tokens)
- Client (Claude Desktop, VS Code, custom)
- Error messages from both client and server logs
- Steps to reproduce

## Next Steps

Once your server is tested and working:

1. **Set up monitoring** to track uptime and performance
2. **Configure alerts** for health check failures
3. **Document your deployment** for team members
4. **Consider scaling** if you have high usage
5. **Implement caching** at the application level if needed

For production deployments, see the [DEPLOYMENT.md](DEPLOYMENT.md) guide for best practices.
