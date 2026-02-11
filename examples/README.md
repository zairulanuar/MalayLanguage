# MalayLanguage MCP Server - Examples

This directory contains example configuration files for using the MalayLanguage MCP server with various clients.

## Files

- **vscode-mcp.json** - Configuration for VS Code or Cursor editors
- **claude-desktop-config.json** - Configuration for Claude Desktop app
- **docker-config.json** - Configuration for Docker-based deployments

## Usage

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
