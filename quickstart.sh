#!/bin/bash

# Google Docs MCP Actor - Quick Start Script
# This script helps you test the Actor locally

echo "🚀 Google Docs MCP Actor - Quick Start"
echo "========================================"
echo ""

# Check if apify CLI is installed
if ! command -v apify &> /dev/null; then
    echo "❌ Apify CLI is not installed!"
    echo "Install it with: npm install -g apify-cli"
    exit 1
fi

echo "✅ Apify CLI found"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python version: $python_version"
echo ""

# Menu
echo "Select an option:"
echo "1. Install dependencies"
echo "2. Test read operation"
echo "3. Test create operation"
echo "4. Test MCP server mode"
echo "5. Test batch operations"
echo "6. Run with custom input"
echo "7. Deploy to Apify"
echo "8. Exit"
echo ""
read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo "📦 Installing dependencies..."
        pip3 install -r requirements.txt
        echo "✅ Dependencies installed!"
        ;;
    2)
        echo "📖 Testing read operation..."
        echo "Note: Make sure to update documentId in INPUT.json"
        apify run
        ;;
    3)
        echo "📝 Testing create operation..."
        apify run --input-file=.actor/INPUT_EXAMPLE_CREATE.json
        ;;
    4)
        echo "🖥️  Testing MCP server mode..."
        apify run --input-file=.actor/INPUT_EXAMPLE_MCP.json
        ;;
    5)
        echo "⚡ Testing batch operations..."
        apify run --input-file=.actor/INPUT_EXAMPLE_BATCH.json
        ;;
    6)
        read -p "Enter path to input file: " input_file
        apify run --input-file=$input_file
        ;;
    7)
        echo "🚀 Deploying to Apify..."
        read -p "Are you sure? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            apify push
        else
            echo "Deployment cancelled"
        fi
        ;;
    8)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✨ Done!"
echo ""
echo "To view results:"
echo "  cat storage/datasets/default/*.json"
echo ""
echo "To view logs:"
echo "  cat storage/logs/*.log"
