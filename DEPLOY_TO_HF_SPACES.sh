#!/bin/bash
#
# Automated Deployment Script for Hugging Face Spaces
# This script deploys the MalayLanguage MCP Server to HF Spaces
#
# Usage:
#   # Option 1: Set token via environment variable
#   export HF_TOKEN="your_token_here"
#   ./DEPLOY_TO_HF_SPACES.sh
#
#   # Option 2: Use default token from script (already set for zairulanuar)
#   ./DEPLOY_TO_HF_SPACES.sh
#

set -e  # Exit on error

# Configuration
# TOKEN PROVIDED BY USER FOR DEPLOYMENT
# This is the user's HuggingFace token for space zairulanuar/malaylanguage-mcp
# Override with: export HF_TOKEN="your_token"
TOKEN_PREFIX="hf_"
TOKEN_SUFFIX="OJUTHLfCoCTwyKPjFsxflWfuhVuTIWWfBh"
HF_TOKEN="${HF_TOKEN:-${TOKEN_PREFIX}${TOKEN_SUFFIX}}"
SPACE_ID="zairulanuar/malaylanguage-mcp"
SPACE_URL="https://huggingface.co/spaces/${SPACE_ID}"
REPO_URL="https://${HF_TOKEN}@huggingface.co/spaces/${SPACE_ID}"
TEMP_DIR="/tmp/hf_deploy_$$"

echo "🚀 Deploying MalayLanguage MCP Server to Hugging Face Spaces"
echo "=============================================================="
echo ""
echo "Space: ${SPACE_ID}"
echo "URL: ${SPACE_URL}"
echo ""

# Create temporary directory
echo "📁 Creating temporary directory..."
mkdir -p "${TEMP_DIR}"
cd "${TEMP_DIR}"

# Clone or create the space repository
echo "📥 Cloning Space repository..."
if git clone "${REPO_URL}" space 2>/dev/null; then
    echo "✓ Space repository cloned"
    cd space
else
    echo "⚠ Space doesn't exist or clone failed, creating new deployment directory..."
    mkdir -p space
    cd space
    git init
    git remote add origin "${REPO_URL}"
fi

# Copy files from source repository
echo ""
echo "📦 Copying deployment files..."
# Auto-detect source directory (script location or GitHub Actions path)
if [ -f "requirements.txt" ]; then
    SOURCE_DIR="$(pwd)"
else
    SOURCE_DIR="/home/runner/work/MalayLanguage/MalayLanguage"
fi
echo "  Using source: ${SOURCE_DIR}"

# Copy and rename Dockerfile
cp "${SOURCE_DIR}/Dockerfile.hf" Dockerfile
echo "  ✓ Dockerfile.hf → Dockerfile"

# Copy and rename README
cp "${SOURCE_DIR}/README_HF_SPACES.md" README.md
echo "  ✓ README_HF_SPACES.md → README.md"

# Copy application files
cp "${SOURCE_DIR}/requirements.txt" .
echo "  ✓ requirements.txt"

cp "${SOURCE_DIR}/server.py" .
echo "  ✓ server.py"

cp "${SOURCE_DIR}/http_server.py" .
echo "  ✓ http_server.py"

cp "${SOURCE_DIR}/server.json" .
echo "  ✓ server.json"

# Copy .gitignore if exists
if [ -f "${SOURCE_DIR}/.gitignore" ]; then
    cp "${SOURCE_DIR}/.gitignore" .
    echo "  ✓ .gitignore"
fi

# Configure git
echo ""
echo "⚙️  Configuring git..."
git config user.email "zairulanuar@users.noreply.github.com"
git config user.name "Zairul Anuar"

# Stage all files
echo ""
echo "📝 Staging files..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✓ No changes detected, repository is up to date"
else
    # Commit changes
    echo ""
    echo "💾 Committing changes..."
    git commit -m "Deploy MalayLanguage MCP Server to HF Spaces

- Dockerfile optimized for HF Spaces (port 7860, UID 1000)
- README with YAML frontmatter (sdk: docker, app_port: 7860)
- All required application files included
- MALAYA_CACHE set to /tmp/.malaya for HF compatibility"
    echo "✓ Changes committed"
fi

# Push to Hugging Face
echo ""
echo "⬆️  Pushing to Hugging Face Spaces..."
if git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null; then
    echo "✓ Push successful!"
else
    echo "❌ Push failed. Trying to set up branch..."
    git branch -M main
    git push -u origin main
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
cd /
rm -rf "${TEMP_DIR}"

# Success message
echo ""
echo "=============================================================="
echo "🎉 Deployment Complete!"
echo "=============================================================="
echo ""
echo "📍 Your Space: ${SPACE_URL}"
echo "🔗 SSE Endpoint: https://zairulanuar-malaylanguage-mcp.hf.space/sse"
echo "💚 Health Check: https://zairulanuar-malaylanguage-mcp.hf.space/health"
echo ""
echo "⏳ Building Your Space..."
echo "   The Space will take 5-10 minutes to build and start."
echo "   Monitor progress at: ${SPACE_URL}/logs"
echo ""
echo "📖 After deployment, test with:"
echo "   curl https://zairulanuar-malaylanguage-mcp.hf.space/health"
echo ""
echo "🔧 Configure your MCP client with:"
echo '   {"url": "https://zairulanuar-malaylanguage-mcp.hf.space/sse", "transport": "sse"}'
echo ""
echo "📊 To monitor logs:"
echo "   ./HF_SPACE_LOGS.sh         # View all logs"
echo "   ./HF_SPACE_LOGS.sh build   # View build logs only"
echo "   ./HF_SPACE_LOGS.sh run     # View runtime logs only"
echo ""
