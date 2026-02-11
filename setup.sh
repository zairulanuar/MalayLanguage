#!/bin/bash
# Quick setup script for MalayLanguage MCP Server

set -e

echo "==================================="
echo "MalayLanguage MCP Server Setup"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "ERROR: Python 3.10 or higher is required"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "To run the server:"
echo "  stdio mode:  python server.py"
echo "  HTTP mode:   python http_server.py"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
