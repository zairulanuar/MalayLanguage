---
title: MalayLanguage MCP Server
emoji: 🇲🇾
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# MalayLanguage MCP Server on Hugging Face Spaces

A Model Context Protocol (MCP) server for Malay language processing, powered by the [Malaya](https://github.com/huseinzol05/malaya) library. This Space provides advanced NLP tools for Bahasa Malaysia through an HTTP/SSE interface.

## 🚀 Quick Start

This Space is running the MalayLanguage MCP server and is accessible via the SSE endpoint.

### Connect Your MCP Client

Use the following configuration to connect your MCP client to this Space:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR_USERNAME-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

Replace `YOUR_USERNAME` with your Hugging Face username.

## 📡 Endpoints

- **`/`** - Service information
- **`/health`** - Health check endpoint
- **`/sse`** - Server-Sent Events endpoint for MCP protocol
- **`/messages`** - POST endpoint for MCP messages

## 🛠️ Available Tools

1. **detect_language** - Detect the language of text (Malay, English, and others)
2. **normalize_malay** - Normalize Malay text by fixing informal writing patterns
3. **correct_spelling** - Correct spelling errors in Malay text
4. **translate** - Bidirectional translation between Malay and English
5. **rewrite_style** - Rewrite text in different styles (formal, casual, simplified)
6. **term_lookup** - Get detailed linguistic information about Malay terms
7. **apply_glossary** - Look up Malay terms with translations and definitions

## 🧪 Testing Your Connection

Test the Space is running:

```bash
curl https://YOUR_USERNAME-malaylanguage-mcp.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "malaylanguage-mcp-server",
  "version": "1.0.0"
}
```

## 💡 Usage Examples

### With Claude Desktop

Edit your Claude Desktop configuration file and add:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR_USERNAME-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

### With VS Code / Cursor

Create `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://YOUR_USERNAME-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

### Example Prompts

Try these prompts in Claude or your MCP client:

- "Use detect_language to identify: 'Selamat pagi, apa khabar?'"
- "Use translate to convert 'Good morning' from English to Malay"
- "Use normalize_malay to fix: 'saya x tau la bro'"
- "Use correct_spelling on: 'sya ingin mkan nasi'"

## ⚙️ Configuration

### Environment Variables

You can configure these in your Space settings:

- `PORT` - Server port (default: 7860 for HF Spaces)
- `HOST` - Server bind address (default: 0.0.0.0)
- `MALAYA_CACHE` - Model cache directory (default: /tmp/.malaya)

### Model Caching

Models are cached in `/tmp/.malaya` on HF Spaces. The first request to each tool will download the required models (~500MB+), which may take 30-60 seconds. Subsequent requests will be much faster (2-3 seconds).

**Note**: HF Spaces may restart periodically, clearing the cache. Consider using a persistent Space tier for production use.

## 📊 Performance

Typical response times on HF Spaces (after model loading):

| Tool | First Load | Subsequent Calls |
|------|------------|------------------|
| detect_language | ~30-45s | <2s |
| normalize_malay | ~45-60s | ~2-3s |
| correct_spelling | ~60-90s | ~3-4s |
| translate | ~60-90s | ~3-4s |
| rewrite_style | ~60-90s | ~3-4s |

**Free tier**: May sleep after inactivity. First wake-up request may be slower.

## 🔧 Deployment Information

This Space uses:
- **Python 3.11** runtime
- **Docker SDK** for containerization
- **Starlette + Uvicorn** for ASGI server
- **Malaya library** for NLP models
- **MCP SDK** for protocol implementation

### Resources Required

- **Memory**: Minimum 4GB RAM recommended (models are memory-intensive)
- **Storage**: ~2GB for models and dependencies
- **CPU**: Standard CPU is sufficient (GPU not required)

## 📖 Documentation

For more information:

- [Full Documentation](https://github.com/zairulanuar/MalayLanguage)
- [Deployment Guide](https://github.com/zairulanuar/MalayLanguage/blob/main/DEPLOYMENT.md)
- [Testing Guide](https://github.com/zairulanuar/MalayLanguage/blob/main/TESTING.md)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Malaya Library](https://github.com/huseinzol05/malaya)

## 🐛 Troubleshooting

### Space is sleeping
- Free tier Spaces sleep after 48 hours of inactivity
- First request after sleep will take longer to wake up

### Models not loading
- Check Space logs for errors
- Verify you have at least 4GB RAM allocated
- Models download on first use - be patient

### Connection issues
- Verify the URL matches your Space URL
- Check that `/sse` endpoint is accessible
- Ensure `transport: "sse"` is set in your client config

## 📝 License

MIT License - see [LICENSE](https://github.com/zairulanuar/MalayLanguage/blob/main/LICENSE) for details

## 🙏 Credits

- Powered by [Malaya](https://github.com/huseinzol05/malaya) - Advanced NLP library for Bahasa Malaysia
- Built on [Model Context Protocol](https://modelcontextprotocol.io/)
- Hosted on [Hugging Face Spaces](https://huggingface.co/spaces)
