# MalayLanguage MCP Server

A Model Context Protocol (MCP) server for superb Malay language processing, powered by the [Malaya](https://github.com/huseinzol05/malaya) library. This server provides advanced Natural Language Processing (NLP) tools for Bahasa Malaysia (BM).

## Features

### Available Tools

1. **detect_language** - Detect the language of text (Malay, English, and other languages)
2. **normalize_malay** - Normalize Malay text by fixing informal writing patterns and colloquialisms
3. **correct_spelling** - Correct spelling errors in Malay text using transformer models
4. **apply_glossary** - Look up Malay terms with translations and definitions
5. **rewrite_style** - Rewrite text in different styles (formal, casual, simplified)
6. **translate** - Bidirectional translation between Malay and English
7. **term_lookup** - Detailed linguistic information about Malay terms

### Transport Support

- **stdio** - Standard input/output for local integration
- **HTTP/SSE** - Streamable HTTP server at `/mcp` endpoint

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/zairulanuar/MalayLanguage.git
cd MalayLanguage
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

Pull the pre-built image from GitHub Container Registry:
```bash
docker pull ghcr.io/zairulanuar/malaylanguage:latest
```

Or build locally:
```bash
docker build -t malaylanguage-mcp .
```

## Usage

### Running with stdio (default)

```bash
python server.py
```

### Running HTTP Server

```bash
python http_server.py
```

The server will start on `http://0.0.0.0:8000` with the MCP endpoint at `/mcp`.

You can specify custom host and port:
```bash
python http_server.py 127.0.0.1 3000
```

### Docker Usage

**stdio mode:**
```bash
docker run -i malaylanguage-mcp
```

**HTTP mode:**
```bash
docker run -p 8000:8000 malaylanguage-mcp python http_server.py
```

## Configuration

### VS Code / Claude Desktop / Cursor

Add the server to your MCP configuration file:

**For Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):**
```json
{
  "mcpServers": {
    "malaylanguage": {
      "command": "python",
      "args": ["/path/to/MalayLanguage/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/MalayLanguage"
      }
    }
  }
}
```

**For VS Code / Cursor (`mcp.json`):**
```json
{
  "mcpServers": {
    "malaylanguage": {
      "command": "python",
      "args": ["/path/to/MalayLanguage/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/MalayLanguage"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

**Using Docker:**
```json
{
  "mcpServers": {
    "malaylanguage": {
      "command": "docker",
      "args": ["run", "-i", "ghcr.io/zairulanuar/malaylanguage:latest"]
    }
  }
}
```

### HTTP Client Configuration

For HTTP-based clients, point to:
```
http://localhost:8000/mcp
```

## Example Usage

### Detect Language
```json
{
  "tool": "detect_language",
  "arguments": {
    "text": "Selamat pagi, apa khabar?"
  }
}
```

### Normalize Text
```json
{
  "tool": "normalize_malay",
  "arguments": {
    "text": "saya x tau la bro"
  }
}
```

### Correct Spelling
```json
{
  "tool": "correct_spelling",
  "arguments": {
    "text": "sya ingin mkan nasi"
  }
}
```

### Translate
```json
{
  "tool": "translate",
  "arguments": {
    "text": "Good morning",
    "source_lang": "en",
    "target_lang": "ms"
  }
}
```

### Rewrite Style
```json
{
  "tool": "rewrite_style",
  "arguments": {
    "text": "Saya nak pergi kedai",
    "style": "formal"
  }
}
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Linting

```bash
# Format with black
black server.py http_server.py tests/

# Lint with ruff
ruff check server.py http_server.py tests/
```

## Model Caching

The Malaya library downloads and caches models on first use. Models are stored in:
- Default: `~/.malaya/`
- Docker: `/root/.malaya/`

Set custom cache directory:
```bash
export MALAYA_CACHE=/path/to/cache
```

## Architecture

```
MalayLanguage/
├── server.py              # Main MCP server (stdio)
├── http_server.py         # HTTP/SSE wrapper
├── server.json            # Server metadata
├── mcp.json              # Example client configuration
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── tests/                # Test suite
│   ├── __init__.py
│   └── test_server.py
└── .github/
    └── workflows/
        └── docker-build-push.yml  # CI/CD pipeline
```

## GitHub Actions

The repository includes automated CI/CD that:
- Builds Docker images on push to main/master
- Publishes to GitHub Container Registry (GHCR)
- Supports version tagging (e.g., `v1.0.0`)
- Generates build provenance attestations

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Credits

- Powered by [Malaya](https://github.com/huseinzol05/malaya) - Advanced NLP library for Bahasa Malaysia
- Built on [Model Context Protocol](https://modelcontextprotocol.io/)

## Support

For issues and questions:
- GitHub Issues: https://github.com/zairulanuar/MalayLanguage/issues
- Malaya Documentation: https://malaya.readthedocs.io/