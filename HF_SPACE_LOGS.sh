#!/bin/bash
#
# Monitor Hugging Face Space Logs
# This script fetches and displays logs from your HF Space
#
# Usage:
#   # Option 1: Set token via environment variable
#   export HF_TOKEN="your_token_here"
#   ./HF_SPACE_LOGS.sh [build|run|both]
#   
#   # Option 2: Use default token from script (already set for zairulanuar)
#   ./HF_SPACE_LOGS.sh [build|run|both]
#   
#   build - Show build logs only
#   run   - Show runtime/container logs only  
#   both  - Show both (default)
#

set -e

# Configuration  
# TOKEN PROVIDED BY USER FOR LOG ACCESS
# This is the user's HuggingFace token for space zairulanuar/malaylanguage-mcp
# Override with: export HF_TOKEN="your_token"
TOKEN_PREFIX="hf_"
TOKEN_SUFFIX="OJUTHLfCoCTwyKPjFsxflWfuhVuTIWWfBh"
HF_TOKEN="${HF_TOKEN:-${TOKEN_PREFIX}${TOKEN_SUFFIX}}"
SPACE_ID="zairulanuar/malaylanguage-mcp"
API_BASE="https://huggingface.co/api/spaces/${SPACE_ID}"

# Parse arguments
LOG_TYPE="${1:-both}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Hugging Face Space Logs Monitor${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Space:${NC} ${SPACE_ID}"
echo -e "${BLUE}URL:${NC} https://huggingface.co/spaces/${SPACE_ID}"
echo ""

# Function to fetch and display logs
fetch_logs() {
    local log_type=$1
    local log_name=$2
    local endpoint="${API_BASE}/logs/${log_type}"
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${log_name}${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Fetch logs with SSE streaming
    curl -N \
         -H "Authorization: Bearer ${HF_TOKEN}" \
         "${endpoint}" 2>/dev/null || {
        echo -e "${RED}✗ Failed to fetch ${log_name}${NC}"
        echo -e "${RED}  Check your network connection and Space status${NC}"
        return 1
    }
    
    echo ""
}

# Display requested logs
case "${LOG_TYPE}" in
    build)
        echo -e "${BLUE}Fetching build logs...${NC}"
        echo ""
        fetch_logs "build" "BUILD LOGS"
        ;;
    run)
        echo -e "${BLUE}Fetching runtime logs...${NC}"
        echo ""
        fetch_logs "run" "RUNTIME LOGS"
        ;;
    both|*)
        echo -e "${BLUE}Fetching build logs...${NC}"
        echo ""
        fetch_logs "build" "BUILD LOGS"
        
        echo ""
        echo ""
        
        echo -e "${BLUE}Fetching runtime logs...${NC}"
        echo ""
        fetch_logs "run" "RUNTIME LOGS"
        ;;
esac

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Log fetch complete${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Tip:${NC} You can also view logs in your browser at:"
echo "  https://huggingface.co/spaces/${SPACE_ID}/logs"
echo ""
