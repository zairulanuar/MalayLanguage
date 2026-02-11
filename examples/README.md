# MalayLanguage MCP Server - Examples

This directory contains example configuration files for using the MalayLanguage MCP server with various clients.

## Files

- **hf-spaces-config.json** - 🆕 **Hugging Face Spaces**: Free ML-optimized hosting configuration
- **remote-http-config.json** - ⭐ **Recommended**: Connect to a remote server without local installation
- **vscode-mcp.json** - Configuration for VS Code or Cursor editors (local)
- **claude-desktop-config.json** - Configuration for Claude Desktop app (local)
- **docker-config.json** - Configuration for Docker-based deployments

## Usage

### Hugging Face Spaces (Free & Easy) 🆕

**Perfect for**: Demos, personal use, ML/NLP workloads

1. Deploy the server to Hugging Face Spaces - see [HF_SPACES_DEPLOYMENT.md](../HF_SPACES_DEPLOYMENT.md)
2. Get your Space URL (e.g., `https://YOUR_USERNAME-malaylanguage-mcp.hf.space`)
3. Use the HF Spaces configuration:

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

See `hf-spaces-config.json` for complete examples including private spaces.

**Notes**:
- First request may be slow (30-90s for model download)
- Free tier sleeps after 48h inactivity
- Upgrade for always-on and better performance

### Remote HTTP Connection (Production) ⭐

**This is the recommended approach** - deploy the server once and connect from any client.

1. Deploy the server to a cloud platform (Railway, Render, Fly.io, HF Spaces) - see [DEPLOYMENT.md](../DEPLOYMENT.md)
2. Get your server URL (e.g., `https://your-app.railway.app`)
3. Use the remote HTTP configuration:

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

See `remote-http-config.json` for complete examples.

### VS Code / Cursor

1. Copy `vscode-mcp.json` to your project's `.vscode/` directory as `mcp.json`
2. Update the path to point to your MalayLanguage installation
3. Reload VS Code

### Claude Desktop

1. Locate your Claude Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Merge the contents of `claude-desktop-config.json` into your config
3. Update the path to point to your MalayLanguage installation
4. Restart Claude Desktop

### Docker

Use the configurations in `docker-config.json` to:
- Run via Docker container (stdio mode)
- Connect to HTTP endpoint (requires running server separately)

## Path Configuration

Replace placeholder paths with actual paths:
- `/absolute/path/to/MalayLanguage` → actual path to your clone
- `/Users/your-username/path/to` → your user directory

## Testing Configuration

After setting up, verify the server appears in your MCP client's server list and that you can invoke the tools:
- detect_language
- normalize_malay
- correct_spelling
- apply_glossary
- rewrite_style
- translate
- term_lookup
