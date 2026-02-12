# HuggingFace Spaces Deployment Guide

This directory contains automated tools for deploying the MalayLanguage MCP Server to HuggingFace Spaces.

## Quick Start

### Step 1: Run Deployment

Choose either Bash or Python script:

```bash
# Using Bash
./DEPLOY_TO_HF_SPACES.sh

# Using Python
python3 DEPLOY_TO_HF_SPACES.py
```

The script will:
- Clone or create the HF Space repository
- Copy all required files (Dockerfile, README, application files)
- Commit and push to HuggingFace
- Display deployment status and URLs

### Step 2: Monitor Build

Wait 5-10 minutes for the Space to build. Monitor progress using:

```bash
# View all logs
./HF_SPACE_LOGS.sh

# View only build logs
./HF_SPACE_LOGS.sh build

# View only runtime logs
./HF_SPACE_LOGS.sh run
```

Or use Python:

```bash
python3 HF_SPACE_LOGS.py
python3 HF_SPACE_LOGS.py build
python3 HF_SPACE_LOGS.py run
```

### Step 3: Test Deployment

Once the Space is running:

```bash
curl https://zairulanuar-malaylanguage-mcp.hf.space/health
```

Expected response:
```json
{"status":"healthy","service":"malaylanguage-mcp-server","version":"1.0.0"}
```

## Files Included

- **DEPLOY_TO_HF_SPACES.sh** - Bash deployment script
- **DEPLOY_TO_HF_SPACES.py** - Python deployment script  
- **HF_SPACE_LOGS.sh** - Bash log monitoring script
- **HF_SPACE_LOGS.py** - Python log monitoring script
- **QUICKSTART_HF_DEPLOYMENT.md** - Comprehensive deployment guide
- **.env.hf.example** - Example environment configuration

## Configuration

The scripts use environment variables for configuration:

```bash
# Set custom token (optional, default is already configured)
export HF_TOKEN="your_token_here"

# Run deployment
./DEPLOY_TO_HF_SPACES.sh
```

## API Access

The log monitoring scripts use the HuggingFace API with token authorization:

```bash
# Build logs endpoint (SSE stream)
curl -N -H "Authorization: Bearer $HF_TOKEN" \
     "https://huggingface.co/api/spaces/zairulanuar/malaylanguage-mcp/logs/build"

# Runtime logs endpoint (SSE stream)  
curl -N -H "Authorization: Bearer $HF_TOKEN" \
     "https://huggingface.co/api/spaces/zairulanuar/malaylanguage-mcp/logs/run"
```

## Important URLs

- **Space Dashboard**: https://huggingface.co/spaces/zairulanuar/malaylanguage-mcp
- **Space Logs**: https://huggingface.co/spaces/zairulanuar/malaylanguage-mcp/logs
- **SSE Endpoint**: https://zairulanuar-malaylanguage-mcp.hf.space/sse
- **Health Check**: https://zairulanuar-malaylanguage-mcp.hf.space/health

## MCP Client Configuration

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://zairulanuar-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

### VS Code / Cursor

Create `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "malaylanguage": {
      "url": "https://zairulanuar-malaylanguage-mcp.hf.space/sse",
      "transport": "sse"
    }
  }
}
```

## Troubleshooting

### Network Issues

If you see DNS resolution errors, you may be in a restricted network environment. The scripts require access to:
- `huggingface.co` - For Git push and API access
- `hf.space` - For Space endpoints

### Build Failures

1. Check build logs: `./HF_SPACE_LOGS.sh build`
2. Verify all required files are present
3. Check Dockerfile syntax
4. Ensure README.md has correct YAML frontmatter

### Runtime Issues

1. Check runtime logs: `./HF_SPACE_LOGS.sh run`
2. Verify port 7860 is used
3. Check Python dependencies
4. Ensure MALAYA_CACHE=/tmp/.malaya

## Manual Deployment

If automated scripts don't work, see QUICKSTART_HF_DEPLOYMENT.md for manual deployment instructions.

## Updates

To update your deployed Space:

```bash
# Run deployment script again
./DEPLOY_TO_HF_SPACES.sh
```

The script detects changes and pushes updates automatically.

## Documentation

- **QUICKSTART_HF_DEPLOYMENT.md** - Detailed deployment guide
- **HF_SPACES_DEPLOYMENT.md** - Complete HF Spaces documentation
- **README_HF_SPACES.md** - Space README content
- **Dockerfile.hf** - HF Spaces optimized Dockerfile

## Support

For issues or questions:
- Check the full documentation in QUICKSTART_HF_DEPLOYMENT.md
- Visit: https://github.com/zairulanuar/MalayLanguage/issues
- HF Docs: https://huggingface.co/docs/hub/spaces

---

**Ready to deploy? Run `./DEPLOY_TO_HF_SPACES.sh` now!** 🚀
