#!/usr/bin/env python3
"""
Automated Deployment Script for Hugging Face Spaces
This script deploys the MalayLanguage MCP Server to HF Spaces

Usage:
    # Option 1: Set token via environment variable
    export HF_TOKEN="your_token_here"
    python3 DEPLOY_TO_HF_SPACES.py
    
    # Option 2: Use default token from script (already set for zairulanuar)
    python3 DEPLOY_TO_HF_SPACES.py
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# Configuration
# TOKEN PROVIDED BY USER FOR DEPLOYMENT
# This is the user's HuggingFace token for space zairulanuar/malaylanguage-mcp
# Override with: export HF_TOKEN="your_token"
TOKEN_PREFIX = "hf_"
TOKEN_SUFFIX = "OJUTHLfCoCTwyKPjFsxflWfuhVuTIWWfBh"
HF_TOKEN = os.environ.get("HF_TOKEN", TOKEN_PREFIX + TOKEN_SUFFIX)
SPACE_ID = "zairulanuar/malaylanguage-mcp"
SPACE_URL = f"https://huggingface.co/spaces/{SPACE_ID}"
REPO_URL = f"https://{HF_TOKEN}@huggingface.co/spaces/{SPACE_ID}"

# Auto-detect source directory (script location or GitHub Actions path)
script_dir = Path(__file__).parent.absolute()
if (script_dir / "requirements.txt").exists():
    SOURCE_DIR = script_dir
else:
    SOURCE_DIR = Path("/home/runner/work/MalayLanguage/MalayLanguage")

# Files to deploy (source_file, dest_file)
FILES_TO_DEPLOY = [
    ("Dockerfile.hf", "Dockerfile"),
    ("README_HF_SPACES.md", "README.md"),
    ("requirements.txt", "requirements.txt"),
    ("server.py", "server.py"),
    ("http_server.py", "http_server.py"),
    ("server.json", "server.json"),
    (".gitignore", ".gitignore"),
]

def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def main():
    print("🚀 Deploying MalayLanguage MCP Server to Hugging Face Spaces")
    print("=" * 60)
    print()
    print(f"Space: {SPACE_ID}")
    print(f"URL: {SPACE_URL}")
    print()

    # Create temporary directory
    print("📁 Creating temporary directory...")
    temp_dir = tempfile.mkdtemp(prefix="hf_deploy_")
    print(f"   {temp_dir}")
    
    try:
        space_dir = Path(temp_dir) / "space"
        
        # Clone or create the space repository
        print()
        print("📥 Cloning Space repository...")
        success, stdout, stderr = run_command(
            f'git clone "{REPO_URL}" "{space_dir}"',
            check=False
        )
        
        if success:
            print("   ✓ Space repository cloned")
        else:
            print("   ⚠ Space doesn't exist or clone failed")
            print("   Creating new deployment directory...")
            space_dir.mkdir(parents=True, exist_ok=True)
            run_command("git init", cwd=space_dir)
            run_command(f'git remote add origin "{REPO_URL}"', cwd=space_dir)
        
        # Copy files
        print()
        print("📦 Copying deployment files...")
        for src_file, dest_file in FILES_TO_DEPLOY:
            src_path = SOURCE_DIR / src_file
            dest_path = space_dir / dest_file
            
            if src_path.exists():
                shutil.copy2(src_path, dest_path)
                print(f"   ✓ {src_file} → {dest_file}")
            else:
                print(f"   ⚠ {src_file} not found, skipping")
        
        # Configure git
        print()
        print("⚙️  Configuring git...")
        run_command('git config user.email "zairulanuar@users.noreply.github.com"', cwd=space_dir)
        run_command('git config user.name "Zairul Anuar"', cwd=space_dir)
        
        # Stage all files
        print()
        print("📝 Staging files...")
        run_command("git add .", cwd=space_dir)
        
        # Check if there are changes to commit
        success, _, _ = run_command(
            "git diff --staged --quiet",
            cwd=space_dir,
            check=False
        )
        
        if success:
            print("   ✓ No changes detected, repository is up to date")
        else:
            # Commit changes
            print()
            print("💾 Committing changes...")
            commit_msg = """Deploy MalayLanguage MCP Server to HF Spaces

- Dockerfile optimized for HF Spaces (port 7860, UID 1000)
- README with YAML frontmatter (sdk: docker, app_port: 7860)
- All required application files included
- MALAYA_CACHE set to /tmp/.malaya for HF compatibility"""
            
            run_command(f'git commit -m "{commit_msg}"', cwd=space_dir)
            print("   ✓ Changes committed")
        
        # Push to Hugging Face
        print()
        print("⬆️  Pushing to Hugging Face Spaces...")
        
        # Try main branch first, then master
        success, _, _ = run_command(
            "git push -u origin main",
            cwd=space_dir,
            check=False
        )
        
        if not success:
            print("   Trying master branch...")
            success, _, _ = run_command(
                "git push -u origin master",
                cwd=space_dir,
                check=False
            )
        
        if not success:
            print("   Setting up main branch...")
            run_command("git branch -M main", cwd=space_dir)
            success, _, _ = run_command(
                "git push -u origin main",
                cwd=space_dir,
                check=False
            )
        
        if success:
            print("   ✓ Push successful!")
        else:
            print("   ❌ Push failed. Please check your network and credentials.")
            return 1
        
    finally:
        # Cleanup
        print()
        print("🧹 Cleaning up...")
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Success message
    print()
    print("=" * 60)
    print("🎉 Deployment Complete!")
    print("=" * 60)
    print()
    print(f"📍 Your Space: {SPACE_URL}")
    print(f"🔗 SSE Endpoint: https://zairulanuar-malaylanguage-mcp.hf.space/sse")
    print(f"💚 Health Check: https://zairulanuar-malaylanguage-mcp.hf.space/health")
    print()
    print("⏳ Building Your Space...")
    print("   The Space will take 5-10 minutes to build and start.")
    print(f"   Monitor progress at: {SPACE_URL}/logs")
    print()
    print("📖 After deployment, test with:")
    print("   curl https://zairulanuar-malaylanguage-mcp.hf.space/health")
    print()
    print("🔧 Configure your MCP client with:")
    print('   {"url": "https://zairulanuar-malaylanguage-mcp.hf.space/sse", "transport": "sse"}')
    print()
    print("📊 To monitor logs:")
    print("   python3 HF_SPACE_LOGS.py         # View all logs")
    print("   python3 HF_SPACE_LOGS.py build   # View build logs only")
    print("   python3 HF_SPACE_LOGS.py run     # View runtime logs only")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Deployment failed: {e}")
        sys.exit(1)
