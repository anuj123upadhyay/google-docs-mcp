#!/bin/bash

# 🧪 Local Testing Guide for Google Docs MCP Actor
# Run this script to test your Actor locally

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 Google Docs MCP Actor - Local Testing"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check if we're in the right directory
echo -e "${BLUE}Step 1: Checking directory...${NC}"
if [ ! -f "src/main.py" ]; then
    echo -e "${RED}Error: Please run this script from the google-docs-mcp directory${NC}"
    exit 1
fi
echo -e "${GREEN}✓ In correct directory${NC}"
echo ""

# Step 2: Check Python version
echo -e "${BLUE}Step 2: Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo -e "${GREEN}✓ Python 3.9+ detected${NC}"
else
    echo -e "${RED}✗ Python 3.9+ required. Please upgrade.${NC}"
    exit 1
fi
echo ""

# Step 3: Check if virtual environment exists
echo -e "${BLUE}Step 3: Checking virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi
echo ""

# Step 4: Install dependencies
echo -e "${BLUE}Step 4: Installing dependencies...${NC}"
echo "This may take a few minutes on first run..."
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 5: Check for Google credentials
echo -e "${BLUE}Step 5: Checking Google credentials...${NC}"
if grep -q "YOUR_DOCUMENT_ID_HERE" storage/key_value_stores/default/INPUT.json; then
    echo -e "${YELLOW}⚠ Warning: You need to configure Google credentials!${NC}"
    echo ""
    echo "Please update storage/key_value_stores/default/INPUT.json with:"
    echo "  1. Your Google Service Account JSON"
    echo "  2. A valid document ID to test with"
    echo ""
    echo -e "${YELLOW}For now, we'll run a basic validation test without Google API calls.${NC}"
    SKIP_GOOGLE=true
else
    echo -e "${GREEN}✓ Credentials appear to be configured${NC}"
    SKIP_GOOGLE=false
fi
echo ""

# Step 6: Run syntax check
echo -e "${BLUE}Step 6: Running syntax checks...${NC}"
python3 -m py_compile src/main.py
python3 -m py_compile src/google_docs_client.py
python3 -m py_compile src/document_analyzer.py
python3 -m py_compile src/mcp_server.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All Python files have valid syntax${NC}"
else
    echo -e "${RED}✗ Syntax errors found${NC}"
    exit 1
fi
echo ""

# Step 7: Test imports
echo -e "${BLUE}Step 7: Testing imports...${NC}"
python3 << EOF
try:
    from src.google_docs_client import GoogleDocsClient
    from src.document_analyzer import DocumentAnalyzer
    from src.mcp_server import MCPServer
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All imports working${NC}"
else
    echo -e "${RED}✗ Import errors detected${NC}"
    exit 1
fi
echo ""

# Step 8: Show available test commands
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}  ✨ Setup Complete! Ready for Testing${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}Quick Test Commands:${NC}"
echo ""
echo -e "${YELLOW}1. Test Document Reading:${NC}"
echo "   apify run"
echo ""
echo -e "${YELLOW}2. Test Document Creation:${NC}"
echo "   apify run --input-file=.actor/INPUT_EXAMPLE_CREATE.json"
echo ""
echo -e "${YELLOW}3. Test MCP Server Mode:${NC}"
echo "   apify run --input-file=.actor/INPUT_EXAMPLE_MCP.json"
echo ""
echo -e "${YELLOW}4. Test Batch Operations:${NC}"
echo "   apify run --input-file=.actor/INPUT_EXAMPLE_BATCH.json"
echo ""
echo -e "${YELLOW}5. View Results:${NC}"
echo "   cat storage/datasets/default/*.json | jq ."
echo ""
echo -e "${YELLOW}6. View Logs:${NC}"
echo "   tail -f storage/logs/*.log"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Update credentials in storage/key_value_stores/default/INPUT.json"
echo "2. Share a test Google Doc with your service account"
echo "3. Run: ${GREEN}apify run${NC}"
echo ""
echo "Need help? Check DEPLOYMENT_GUIDE.md"
echo ""
