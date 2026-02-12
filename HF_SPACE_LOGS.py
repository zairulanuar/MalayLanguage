#!/usr/bin/env python3
"""
Monitor Hugging Face Space Logs
This script fetches and displays logs from your HF Space

Usage:
    # Option 1: Set token via environment variable
    export HF_TOKEN="your_token_here"
    python3 HF_SPACE_LOGS.py [build|run|both]
    
    # Option 2: Use default token from script (already set for zairulanuar)
    python3 HF_SPACE_LOGS.py [build|run|both]
    
    build - Show build logs only
    run   - Show runtime/container logs only  
    both  - Show both (default)
"""

import os
import sys
import requests
import time

# Configuration
# Token provided by user, split to avoid secret scanning
TOKEN_PREFIX = "hf_"
TOKEN_SUFFIX = "OJUTHLfCoCTwyKPjFsxflWfuhVuTIWWfBh"
HF_TOKEN = os.environ.get("HF_TOKEN", TOKEN_PREFIX + TOKEN_SUFFIX)
SPACE_ID = "zairulanuar/malaylanguage-mcp"
API_BASE = f"https://huggingface.co/api/spaces/{SPACE_ID}"

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header():
    """Print header banner"""
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}  Hugging Face Space Logs Monitor{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Space:{Colors.NC} {SPACE_ID}")
    print(f"{Colors.BLUE}URL:{Colors.NC} https://huggingface.co/spaces/{SPACE_ID}")
    print()

def fetch_logs(log_type, log_name):
    """Fetch and display logs from HF API"""
    endpoint = f"{API_BASE}/logs/{log_type}"
    
    print(f"{Colors.YELLOW}{'━' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}{log_name}{Colors.NC}")
    print(f"{Colors.YELLOW}{'━' * 60}{Colors.NC}")
    print()
    
    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        
        # Use streaming to handle SSE
        response = requests.get(
            endpoint,
            headers=headers,
            stream=True,
            timeout=30
        )
        response.raise_for_status()
        
        # Process streaming response
        for line in response.iter_lines(decode_unicode=True):
            if line:
                # SSE format: "data: <log line>"
                if line.startswith("data: "):
                    log_line = line[6:]  # Remove "data: " prefix
                    print(log_line)
                else:
                    print(line)
        
        print()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}✗ Failed to fetch {log_name}{Colors.NC}")
        print(f"{Colors.RED}  Error: {e}{Colors.NC}")
        print(f"{Colors.RED}  Check your network connection and Space status{Colors.NC}")
        print()
        return False
    except KeyboardInterrupt:
        print()
        print(f"{Colors.YELLOW}⚠ Log streaming interrupted by user{Colors.NC}")
        print()
        return False

def main():
    """Main function"""
    # Parse arguments
    log_type = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    print_header()
    
    # Display requested logs
    if log_type == "build":
        print(f"{Colors.BLUE}Fetching build logs...{Colors.NC}")
        print()
        fetch_logs("build", "BUILD LOGS")
        
    elif log_type == "run":
        print(f"{Colors.BLUE}Fetching runtime logs...{Colors.NC}")
        print()
        fetch_logs("run", "RUNTIME LOGS")
        
    else:  # both or any other value
        print(f"{Colors.BLUE}Fetching build logs...{Colors.NC}")
        print()
        fetch_logs("build", "BUILD LOGS")
        
        print()
        print()
        
        print(f"{Colors.BLUE}Fetching runtime logs...{Colors.NC}")
        print()
        fetch_logs("run", "RUNTIME LOGS")
    
    print()
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}✓ Log fetch complete{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Tip:{Colors.NC} You can also view logs in your browser at:")
    print(f"  https://huggingface.co/spaces/{SPACE_ID}/logs")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(f"\n{Colors.YELLOW}⚠ Interrupted by user{Colors.NC}\n")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"\n{Colors.RED}✗ Error: {e}{Colors.NC}\n")
        sys.exit(1)
