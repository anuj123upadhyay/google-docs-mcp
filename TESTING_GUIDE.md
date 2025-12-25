# 🧪 Local Testing Guide

## How to Test Your Google Docs MCP Actor Locally

Before deploying to Apify, test everything locally to ensure it works correctly.

---

## 🚀 Quick Start (Easiest Method)

### Run the automated test script:

```bash
cd google-docs-mcp
./test-local.sh
```

This script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Validate syntax
- ✅ Test imports
- ✅ Show you next steps

---

## 📋 Manual Testing (Step-by-Step)

### Step 1: Install Dependencies

```bash
cd google-docs-mcp

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed apify-2.7.3 google-api-python-client-2.110.0 ...
```

### Step 2: Configure Google Credentials

You need Google API credentials. Choose one option:

#### Option A: Service Account (Recommended)

1. **Get Service Account JSON:**
   - Go to https://console.cloud.google.com/
   - Create/select project
   - Enable "Google Docs API" and "Google Drive API"
   - Create Service Account → Download JSON key

2. **Share a test document:**
   - Open any Google Doc
   - Click "Share"
   - Add the service account email (from JSON)
   - Grant "Editor" permission
   - Copy the document ID from URL

3. **Update INPUT.json:**

Edit `storage/key_value_stores/default/INPUT.json`:

```json
{
  "operation": "read_document",
  "googleCredentials": {
    "type": "service_account",
    "serviceAccountJson": "{\"type\":\"service_account\",\"project_id\":\"your-project\",\"private_key_id\":\"...\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\",\"client_email\":\"your-sa@project.iam.gserviceaccount.com\",\"client_id\":\"...\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://oauth2.googleapis.com/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_x509_cert_url\":\"...\"}"
  },
  "documentId": "1abc123-YOUR-ACTUAL-DOCUMENT-ID",
  "analysisOptions": {
    "wordCount": true,
    "extractKeywords": true,
    "summarize": true
  },
  "verbose": true
}
```

**Important:** Replace the entire `serviceAccountJson` value with your actual JSON (as a string).

### Step 3: Validate Python Syntax

```bash
# Check for syntax errors
python3 -m py_compile src/main.py
python3 -m py_compile src/google_docs_client.py
python3 -m py_compile src/document_analyzer.py
python3 -m py_compile src/mcp_server.py
```

**Expected output:** No output means success!

### Step 4: Test Imports

```bash
python3 << 'EOF'
try:
    from src.google_docs_client import GoogleDocsClient
    from src.document_analyzer import DocumentAnalyzer
    from src.mcp_server import MCPServer
    from src import main
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF
```

**Expected output:**
```
✅ All imports successful!
```

---

## 🎯 Running Tests

### Test 1: Read Document (Default Test)

```bash
apify run
```

**What it does:**
- Reads the INPUT.json file
- Authenticates with Google
- Reads the specified document
- Analyzes content
- Saves results to dataset

**Expected output:**
```
Info: Actor 'google-docs-mcp' is starting...
🚀 Starting Google Docs MCP Actor
Operation: read_document
🔐 Authenticating with Google APIs...
✅ Authentication successful!
📋 Executing operation: read_document
📖 Reading document: 1abc123...
✅ Document read successfully: 5234 characters
💾 Results saved to dataset
✨ Actor finished successfully!
```

**Check results:**
```bash
cat storage/datasets/default/*.json | python3 -m json.tool
```

**Expected result:**
```json
{
  "operation": "read_document",
  "documentId": "1abc123...",
  "title": "Test Document",
  "textContent": "Your document content here...",
  "characterCount": 5234,
  "wordCount": 892,
  "analysis": {
    "statistics": {
      "wordCount": 892,
      "characterCount": 5234,
      "readingTime": 4.5
    },
    "keywords": [
      {"keyword": "test", "frequency": 12, "relevance": 2.5}
    ],
    "summary": "This is a test document..."
  }
}
```

### Test 2: Create Document

```bash
apify run --input-file=.actor/INPUT_EXAMPLE_CREATE.json
```

**Before running:** Update the credentials in `INPUT_EXAMPLE_CREATE.json`

**What it does:**
- Creates a new Google Doc
- Adds content
- Shares with specified emails (optional)
- Returns document URL

**Expected output:**
```
📝 Creating new document: AI Generated Report
✅ Document created: https://docs.google.com/document/d/NEW_DOC_ID/edit
```

### Test 3: MCP Server Mode

```bash
apify run --input-file=.actor/INPUT_EXAMPLE_MCP.json
```

**What it does:**
- Initializes MCP server
- Lists available tools
- Shows webhook configuration

**Expected output:**
```
🖥️  Running in MCP Server mode
📡 MCP Server initialized with 8 tools
Available tools:
  - read_document: Read full document content
  - write_document: Insert/update content
  - create_document: Create new documents
  ...
```

### Test 4: Batch Operations

```bash
apify run --input-file=.actor/INPUT_EXAMPLE_BATCH.json
```

**Before running:** Update document IDs in the file

**What it does:**
- Executes multiple operations sequentially
- Tracks success/failure
- Returns aggregated results

**Expected output:**
```
⚡ Executing 3 batch operations...
  Operation 1/3: read
  Operation 2/3: analyze
  Operation 3/3: write
✅ Batch complete: 3/3 successful
```

---

## 🔍 Debugging Failed Tests

### Error: "Import could not be resolved"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "Authentication failed"

**Problem:** Invalid credentials

**Solution:**
1. Verify service account JSON is valid
2. Check APIs are enabled in Google Cloud
3. Ensure JSON is properly escaped (quotes, newlines)

### Error: "Document not found"

**Problem:** Document ID invalid or not shared

**Solution:**
1. Verify document ID from URL
2. Share document with service account email
3. Wait a few seconds for permissions to sync

### Error: "Rate limit exceeded"

**Problem:** Too many API calls

**Solution:**
1. Increase `rateLimitDelay` in INPUT.json (e.g., 200-500ms)
2. Wait a minute before retrying
3. Check Google Cloud Console quotas

### Error: "Permission denied"

**Problem:** Service account lacks permissions

**Solution:**
1. Share document with service account email
2. Grant "Editor" permission (not just "Viewer")
3. For creating docs, check Drive API is enabled

---

## 📊 Viewing Results

### View Dataset Output

```bash
# Pretty print JSON
cat storage/datasets/default/*.json | python3 -m json.tool

# Or with jq (if installed)
cat storage/datasets/default/*.json | jq .

# Count operations
ls -l storage/datasets/default/ | wc -l
```

### View Logs

```bash
# Real-time logs
tail -f storage/logs/*.log

# All logs
cat storage/logs/*.log

# Search for errors
grep -i error storage/logs/*.log
```

### Clear Previous Results

```bash
# Clear datasets
rm -rf storage/datasets/default/*

# Clear logs
rm -rf storage/logs/*

# Start fresh
apify run
```

---

## 🧪 Advanced Testing

### Test Individual Functions

Create a test script `test_functions.py`:

```python
#!/usr/bin/env python3
"""Test individual functions locally."""

import asyncio
import json
from src.google_docs_client import GoogleDocsClient
from src.document_analyzer import DocumentAnalyzer

async def test_document_analyzer():
    """Test the document analyzer without Google API."""
    print("Testing DocumentAnalyzer...")
    
    analyzer = DocumentAnalyzer()
    
    # Sample text
    text = """
    This is a test document about AI and automation.
    Machine learning is transforming how we work.
    Artificial intelligence enables smarter systems.
    Visit https://example.com for more info.
    """
    
    # Test analysis
    result = analyzer.analyze_document(text, {
        'wordCount': True,
        'extractKeywords': True,
        'summarize': True,
        'extractLinks': True
    })
    
    print(json.dumps(result, indent=2))
    print("✅ DocumentAnalyzer test passed!")

async def test_google_client():
    """Test Google client with real credentials."""
    print("\nTesting GoogleDocsClient...")
    
    # Load credentials from INPUT.json
    with open('storage/key_value_stores/default/INPUT.json') as f:
        config = json.load(f)
    
    try:
        client = GoogleDocsClient(config['googleCredentials'])
        print("✅ Authentication successful!")
        
        # Test reading
        doc_id = config.get('documentId')
        if doc_id and doc_id != 'YOUR_DOCUMENT_ID_HERE':
            text = client.get_document_text(doc_id)
            print(f"✅ Read document: {len(text)} characters")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    asyncio.run(test_document_analyzer())
    # asyncio.run(test_google_client())  # Uncomment when credentials are ready
```

Run it:
```bash
python3 test_functions.py
```

### Performance Testing

Test with multiple documents:

```bash
# Create test input
cat > test_batch.json << 'EOF'
{
  "operation": "batch_operations",
  "googleCredentials": {
    "type": "service_account",
    "serviceAccountJson": "..."
  },
  "batchOperations": [
    {"operation": "read", "documentId": "doc1"},
    {"operation": "read", "documentId": "doc2"},
    {"operation": "read", "documentId": "doc3"}
  ],
  "rateLimitDelay": 100
}
EOF

# Run and time it
time apify run --input-file=test_batch.json
```

### Memory Testing

Check memory usage:

```bash
# On macOS/Linux
/usr/bin/time -l apify run

# Look for "maximum resident set size"
```

---

## ✅ Testing Checklist

Before deploying, ensure:

- [ ] All dependencies install without errors
- [ ] No Python syntax errors
- [ ] All imports work
- [ ] Read operation successful
- [ ] Write operation successful
- [ ] Create operation successful
- [ ] Analysis features working
- [ ] Batch operations complete
- [ ] MCP server initializes
- [ ] Error handling catches issues
- [ ] Results save to dataset
- [ ] Logs are informative

---

## 🚀 Ready for Deployment?

If all tests pass:

```bash
# Push to Apify
apify push

# Test on platform
# Go to Apify Console and run
```

---

## 💡 Tips for Successful Testing

1. **Start Simple**: Test read operation first
2. **Use Test Documents**: Don't test on important docs
3. **Check Logs**: Always review logs for issues
4. **Test Errors**: Try invalid inputs to verify error handling
5. **Clear Results**: Delete old results between tests
6. **Monitor Quotas**: Check Google Cloud Console for API usage
7. **Be Patient**: First run takes longer due to authentication

---

## 📞 Need Help?

If you encounter issues:

1. Check DEPLOYMENT_GUIDE.md troubleshooting section
2. Review Google Docs API documentation
3. Verify service account setup
4. Check Apify SDK documentation
5. Review error messages carefully

---

**Happy Testing! 🎉**

Once everything works locally, you're ready to deploy to Apify and win the 1 Million Challenge!
