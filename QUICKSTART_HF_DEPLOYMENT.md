# Quick Start: Deploy to Hugging Face Spaces

This guide provides step-by-step instructions to deploy the MalayLanguage MCP Server to Hugging Face Spaces.

## Prerequisites

- Git installed on your machine
- HuggingFace account (the token is already included in the scripts)

## Method 1: Automated Deployment (Recommended)

### Option A: Using Bash Script

```bash
# Make the script executable (if not already)
chmod +x DEPLOY_TO_HF_SPACES.sh

# Run the deployment
./DEPLOY_TO_HF_SPACES.sh
```

### Option B: Using Python Script

```bash
# Run the deployment
python3 DEPLOY_TO_HF_SPACES.py
```

Both scripts will:
1. Clone or create the HF Space repository
2. Copy all required files
3. Commit and push to HuggingFace
4. Display the deployment status and URLs

## Method 2: Manual Deployment

If the automated scripts don't work, you can deploy manually:

### Step 1: Clone the Space Repository

```bash
# Create a temporary directory
mkdir -p /tmp/hf_deploy
cd /tmp/hf_deploy

# Clone your Space (it may be empty if newly created)
# Replace YOUR_HF_TOKEN with your actual token
git clone https://YOUR_HF_TOKEN@huggingface.co/spaces/zairulanuar/malaylanguage-mcp
cd malaylanguage-mcp
```

If the Space doesn't exist yet, create it first at: https://huggingface.co/new-space

### Step 2: Copy Required Files

From the MalayLanguage repository root:

```bash
# Set the source directory (adjust path as needed)
SOURCE_DIR="/home/runner/work/MalayLanguage/MalayLanguage"

# Copy and rename files
cp $SOURCE_DIR/Dockerfile.hf Dockerfile
cp $SOURCE_DIR/README_HF_SPACES.md README.md
cp $SOURCE_DIR/requirements.txt .
cp $SOURCE_DIR/server.py .
cp $SOURCE_DIR/http_server.py .
cp $SOURCE_DIR/server.json .
cp $SOURCE_DIR/.gitignore .
```

### Step 3: Commit and Push

```bash
# Configure git (if needed)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Stage all files
git add .

# Commit
git commit -m "Deploy MalayLanguage MCP Server"

# Push to HuggingFace
git push origin main
```

## After Deployment

### Monitor Build Progress

The Space will take 5-10 minutes to build. Monitor progress using:

#### Option A: Web Interface
Visit: https://huggingface.co/spaces/zairulanuar/malaylanguage-mcp/logs

#### Option B: Command Line (Bash)

```bash
# View all logs
./HF_SPACE_LOGS.sh

# View only build logs
./HF_SPACE_LOGS.sh build

# View only runtime logs
./HF_SPACE_LOGS.sh run
```

#### Option C: Command Line (Python)

```bash
# View all logs
python3 HF_SPACE_LOGS.py

# View only build logs
python3 HF_SPACE_LOGS.py build

# View only runtime logs
python3 HF_SPACE_LOGS.py run
```

#### Option D: Direct API Access

```bash
# Set your HF token
export HF_TOKEN="your_hf_token_here"

# Get build logs (SSE stream)
curl -N -H "Authorization: Bearer $HF_TOKEN" \
     "https://huggingface.co/api/spaces/zairulanuar/malaylanguage-mcp/logs/build"

# Get runtime/container logs (SSE stream)
curl -N -H "Authorization: Bearer $HF_TOKEN" \
     "https://huggingface.co/api/spaces/zairulanuar/malaylanguage-mcp/logs/run"
```

### Test Your Deployment

Once the Space is running:

```bash
# Test health endpoint
curl https://zairulanuar-malaylanguage-mcp.hf.space/health

# Expected response:
# {"status":"healthy","service":"malaylanguage-mcp-server","version":"1.0.0"}

# Test service info
curl https://zairulanuar-malaylanguage-mcp.hf.space/

# Test with the connection script
python3 test_connection.py https://zairulanuar-malaylanguage-mcp.hf.space
```

## Configure Your MCP Client

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

Create or edit `.vscode/mcp.json`:

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

## Important URLs

- **Space Dashboard**: https://huggingface.co/spaces/zairulanuar/malaylanguage-mcp
- **Space Logs**: https://huggingface.co/spaces/zairulanuar/malaylanguage-mcp/logs
- **SSE Endpoint**: https://zairulanuar-malaylanguage-mcp.hf.space/sse
- **Health Check**: https://zairulanuar-malaylanguage-mcp.hf.space/health
- **Service Info**: https://zairulanuar-malaylanguage-mcp.hf.space/

## Troubleshooting

### Build Fails

1. Check build logs: `./HF_SPACE_LOGS.sh build`
2. Verify all required files are present
3. Check Dockerfile syntax
4. Ensure README.md has correct YAML frontmatter

### Space Doesn't Start

1. Check runtime logs: `./HF_SPACE_LOGS.sh run`
2. Verify port 7860 is used in Dockerfile
3. Check Python dependencies in requirements.txt
4. Ensure MALAYA_CACHE is set to /tmp/.malaya

### Models Fail to Load

1. First request may take 30-90 seconds (models downloading)
2. Check Space has enough memory (minimum 4GB recommended)
3. Monitor logs during model loading
4. Consider upgrading to a higher tier Space

### Connection Issues

1. Verify Space is running (green status)
2. Check the URL matches: `https://zairulanuar-malaylanguage-mcp.hf.space/sse`
3. Ensure `"transport": "sse"` is set in client config
4. Test health endpoint first

## Updating Your Deployment

To update your Space after making changes:

```bash
# Run deployment script again
./DEPLOY_TO_HF_SPACES.sh
# or
python3 DEPLOY_TO_HF_SPACES.py
```

The script will detect changes and push updates automatically.

## Files Included in Deployment

The following files are deployed to your Space:

- `Dockerfile` (from Dockerfile.hf) - HF Spaces optimized container
- `README.md` (from README_HF_SPACES.md) - Space description with YAML frontmatter
- `requirements.txt` - Python dependencies
- `server.py` - MCP server implementation
- `http_server.py` - HTTP/SSE server
- `server.json` - Server configuration
- `.gitignore` - Git ignore rules

## Key Configuration

The deployment uses these HF Spaces-specific settings:

- **Port**: 7860 (HF Spaces default)
- **User ID**: 1000 (HF Spaces requirement)
- **Model Cache**: /tmp/.malaya (writable location)
- **SDK**: docker
- **App Port**: 7860 (in README frontmatter)

## Need Help?

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **MalayLanguage Docs**: See DEPLOYMENT.md and HF_SPACES_DEPLOYMENT.md
- **MalayLanguage Issues**: https://github.com/zairulanuar/MalayLanguage/issues

---

**Ready to deploy? Run `./DEPLOY_TO_HF_SPACES.sh` or `python3 DEPLOY_TO_HF_SPACES.py` now!** 🚀
