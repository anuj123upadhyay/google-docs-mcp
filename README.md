# 📝 Google Docs MCP Actor

> **AI-Powered Google Docs Integration for the Apify

A comprehensive Model Context Protocol (MCP) server that enables seamless integration between AI assistants, automation tools, and Google Docs. This Actor provides intelligent document processing, content generation, and collaborative workflow capabilities.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-0078D7?logo=apify)](https://apify.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://www.python.org/)
[![Google Docs API](https://img.shields.io/badge/Google-Docs%20API-4285F4?logo=google)](https://developers.google.com/docs/api)
[![MCP](https://img.shields.io/badge/Protocol-MCP-brightgreen)](https://modelcontextprotocol.io)

---

## 🌟 Key Features

### Real-Time Document Interaction
- **Read** documents with full structure preservation
- **Write** and insert content at any position
- **Create** new documents programmatically
- **Update** existing documents with formatting

### Advanced Text Processing
- **Smart Analysis**: Extract keywords, generate summaries, detect language
- **Statistics**: Word count, character count, reading time estimation
- **Structure Detection**: Identify headings, lists, tables automatically
- **Link Extraction**: Find and catalog all URLs in documents

### Collaborative Editing Support
- **Permission Management**: Share documents with specific roles
- **Change Tracking**: Monitor document modifications
- **Multi-User Support**: Handle concurrent editing scenarios
- **Version Control**: Track document revisions

### Intelligent Document Analysis
- Keyword extraction with frequency analysis
- Automatic summarization (extractive)
- Content pattern recognition
- Language detection
- Table data extraction

### Model Context Protocol (MCP) Integration
- Full MCP server implementation
- 8+ pre-built tools for AI assistants
- Structured API for seamless AI integration
- Webhook support for notifications

---

## 🎯 Target Audience

- **AI Developers**: Building document-centric applications
- **Business Automation Specialists**: Streamlining Google Workspace workflows
- **Content Creators**: AI-assisted writing and editing tools
- **Enterprise Teams**: Intelligent document processing systems
- **Digital Marketers**: Automated content generation and management

---

## 🚀 Quick Start

### 1. Set Up Google API Credentials

You need either:

#### Option A: Service Account (Recommended for Automation)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Docs API and Google Drive API
4. Create a Service Account
5. Download the JSON key file
6. Share your documents with the service account email

#### Option B: OAuth 2.0 (For Personal Accounts)
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Get your access token and refresh token
3. Use these in the Actor configuration

### 2. Configure the Actor

```json
{
  "operation": "mcp_server",
  "googleCredentials": {
    "type": "service_account",
    "serviceAccountJson": "{...your service account JSON...}"
  },
  "mcpServerConfig": {
    "enableServer": true,
    "allowedTools": [
      "read_document",
      "write_document",
      "create_document",
      "analyze_content"
    ]
  }
}
```

### 3. Run the Actor

```bash
# Locally
apify run

# On Apify Platform
apify push
```

---

## 📋 Operations

### 1. Read Document
Extract content and metadata from Google Docs.

```json
{
  "operation": "read_document",
  "documentId": "YOUR_DOCUMENT_ID",
  "analysisOptions": {
    "wordCount": true,
    "extractKeywords": true,
    "summarize": true
  },
  "outputFormat": "json"
}
```

**Output:**
- Full text content
- Document metadata (title, dates, owners)
- Optional analysis results
- Character and word counts

### 2. Write Document
Insert or append content to documents.

```json
{
  "operation": "write_document",
  "documentId": "YOUR_DOCUMENT_ID",
  "content": "Your content here...",
  "insertPosition": {
    "location": "end"
  },
  "formatting": {
    "bold": true,
    "fontSize": 12,
    "foregroundColor": "#000000"
  }
}
```

**Features:**
- Insert at start, end, or specific index
- Apply text formatting (bold, italic, colors, fonts)
- Replace all content option

### 3. Create Document
Generate new Google Docs documents.

```json
{
  "operation": "create_document",
  "documentTitle": "My New Document",
  "content": "Initial content...",
  "shareSettings": {
    "shareWithEmails": ["user@example.com"],
    "role": "writer",
    "sendNotification": true
  }
}
```

**Returns:**
- Document ID
- Document URL
- Initial metadata

### 4. Analyze Document
Comprehensive content analysis.

```json
{
  "operation": "analyze_document",
  "documentId": "YOUR_DOCUMENT_ID",
  "analysisOptions": {
    "extractKeywords": true,
    "summarize": true,
    "wordCount": true,
    "extractLinks": true,
    "detectLanguage": true,
    "extractTables": true
  }
}
```

**Analysis Includes:**
- **Statistics**: Word/character counts, sentences, paragraphs, reading time
- **Keywords**: Top 20 keywords with frequency and relevance scores
- **Summary**: Extractive summary (5 key sentences)
- **Links**: All URLs with domain and occurrence count
- **Language**: Detected language code
- **Structure**: Headings, lists, tables
- **Tables**: Extracted table data in structured format

### 5. Search Content
Find specific text within documents.

```json
{
  "operation": "search_content",
  "documentId": "YOUR_DOCUMENT_ID",
  "searchQuery": "keyword to find"
}
```

**Returns:**
- All matches with positions
- Context snippets (50 chars before/after)
- Total match count

### 6. List Documents
Enumerate accessible documents.

```json
{
  "operation": "list_documents",
  "maxRetries": 100
}
```

**Returns list with:**
- Document ID
- Name/title
- Created/modified timestamps
- Owners
- Web view link

### 7. Batch Operations
Execute multiple operations efficiently.

```json
{
  "operation": "batch_operations",
  "batchOperations": [
    {
      "operation": "read",
      "documentId": "DOC_ID_1"
    },
    {
      "operation": "write",
      "documentId": "DOC_ID_2",
      "params": {
        "content": "Batch update"
      }
    }
  ],
  "rateLimitDelay": 100
}
```

**Features:**
- Sequential execution
- Rate limiting
- Individual error handling
- Success/failure tracking

### 8. MCP Server Mode
Run as Model Context Protocol server.

```json
{
  "operation": "mcp_server",
  "mcpServerConfig": {
    "enableServer": true,
    "allowedTools": [
      "read_document",
      "write_document",
      "create_document",
      "search_documents",
      "analyze_content",
      "list_documents"
    ],
    "webhookUrl": "https://your-webhook.com/endpoint"
  }
}
```

**MCP Tools Exposed:**
- `read_document`: Read full document content
- `write_document`: Insert/update content
- `create_document`: Create new documents
- `search_documents`: Search within documents
- `analyze_content`: Analyze and extract insights
- `list_documents`: List accessible documents
- `get_metadata`: Retrieve document metadata
- `share_document`: Manage permissions

---

## 🔧 Configuration Options

### Google Credentials
```json
{
  "googleCredentials": {
    "type": "service_account",  // or "oauth2"
    "serviceAccountJson": "{}",  // Full service account JSON
    "oauthToken": "token",       // OAuth access token
    "oauthRefreshToken": "token" // OAuth refresh token
  }
}
```

### Insert Position
```json
{
  "insertPosition": {
    "index": 1,              // Specific character position
    "location": "start"      // or "end" or "replace_all"
  }
}
```

### Text Formatting
```json
{
  "formatting": {
    "bold": true,
    "italic": false,
    "fontSize": 12,
    "fontFamily": "Arial",
    "foregroundColor": "#000000",
    "backgroundColor": "#FFFFFF"
  }
}
```

### Analysis Options
```json
{
  "analysisOptions": {
    "extractKeywords": true,
    "summarize": true,
    "wordCount": true,
    "extractLinks": true,
    "detectLanguage": true,
    "extractTables": false
  }
}
```

### Share Settings
```json
{
  "shareSettings": {
    "shareWithEmails": ["user@example.com"],
    "role": "reader",        // or "writer" or "commenter"
    "sendNotification": true
  }
}
```

---

## 💡 Use Cases

### 1. AI Content Generation
Generate blog posts, articles, or reports and automatically save to Google Docs with proper formatting.

### 2. Document Analysis Pipeline
Analyze multiple documents to extract insights, keywords, and summaries for content strategy.

### 3. Collaborative Workflow Automation
Automatically create and share documents with team members based on triggers.

### 4. Meeting Notes Assistant
AI assistant reads meeting agendas, creates notes documents, and shares with attendees.

### 5. Content Audit System
Scan documents for specific keywords, links, or compliance requirements.

### 6. Report Generation
Generate formatted reports from data sources and publish to Google Docs.

### 7. Translation Pipeline
Read documents, translate content (external service), write back translated version.

### 8. Knowledge Base Builder
Extract and consolidate information from multiple documents into structured format.

---

## 📊 Output Data

Results are saved to the Apify dataset in structured JSON format:

```json
{
  "operation": "read_document",
  "documentId": "abc123",
  "title": "My Document",
  "textContent": "Full text...",
  "metadata": {
    "documentUrl": "https://docs.google.com/document/d/...",
    "createdTime": "2025-01-01T00:00:00Z",
    "modifiedTime": "2025-01-15T10:30:00Z",
    "owners": [{"displayName": "John Doe", "emailAddress": "john@example.com"}]
  },
  "analysis": {
    "statistics": {
      "wordCount": 1500,
      "characterCount": 8500,
      "readingTime": 7.5
    },
    "keywords": [...],
    "summary": "...",
    "links": [...]
  }
}
```

---

## 🔐 Security & Privacy

- **Credentials**: All API credentials are encrypted and never logged
- **Permissions**: Service accounts require explicit document sharing
- **Rate Limiting**: Built-in delays to respect API quotas
- **Error Handling**: Comprehensive error catching and retry logic
- **Audit Trail**: All operations logged (except sensitive data)

---

## 📈 Performance & Limits

### Google API Quotas
- **Read requests**: 300 per minute per user
- **Write requests**: 300 per minute per user
- **Batch operations**: Use `rateLimitDelay` to manage quotas

### Actor Limits
- **Document size**: Up to 10 MB per document
- **Batch operations**: Recommended max 50 operations
- **Memory**: 2048 MB (configurable)
- **Timeout**: Adjustable based on operation

### Optimization Tips
1. Use batch operations for multiple documents
2. Set appropriate `rateLimitDelay` (100-500ms)
3. Enable `maxRetries` for resilience
4. Cache document IDs for repeated access

---

## 🐛 Troubleshooting

### Authentication Errors
```
Error: Authentication failed
```
**Solution**: 
- Verify service account JSON is valid
- Check API is enabled in Google Cloud
- Ensure document is shared with service account email

### Permission Errors
```
Error: The caller does not have permission
```
**Solution**:
- Share document with service account email
- Check service account has proper scopes
- Verify document ID is correct

### Rate Limit Errors
```
Error: Rate limit exceeded
```
**Solution**:
- Increase `rateLimitDelay` (e.g., 500ms)
- Reduce batch operation size
- Implement exponential backoff

### Document Not Found
```
Error: Requested entity was not found
```
**Solution**:
- Verify document ID is correct
- Check document hasn't been deleted
- Ensure proper permissions

---


## 🛠️ Development

### Local Setup
```bash
# Clone repository
cd google-docs-mcp

# Install dependencies
pip install -r requirements.txt

# Run locally
apify run
```

### Testing
```bash
# Test with sample input
apify run --input=INPUT.json

# Check output
cat ./storage/datasets/default/*.json
```

### Deployment
```bash
# Build and push to Apify
apify push

# Set to public (after approval)
apify actor publish
```

---

## 📚 Resources

- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Apify Documentation](https://docs.apify.com/)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Service Account Setup Guide](https://cloud.google.com/iam/docs/service-accounts)

---

## 🤝 Support

- **Issues**: Report bugs and feature requests via Apify Console
- **Documentation**: Full API documentation in code
- **Examples**: See `INPUT.json` for sample configurations
- **Community**: Share your use cases and workflows

---

## 📄 License

MIT License - Free to use and modify for the Apify 1 Million Challenge

---

## 🏆 Why This Actor Wins

1. **Comprehensive**: 8+ operations, full MCP support
2. **Production-Ready**: Error handling, rate limiting, retries
3. **AI-First**: Built for AI assistants and automation
4. **Well-Documented**: Clear examples and use cases
5. **Scalable**: Batch operations, efficient API usage
6. **Monetizable**: Clear value proposition and pricing strategy
7. **Innovative**: MCP protocol integration for modern AI workflows

---

**Built with ❤️ for the Apify 1 Million Challenge**

*Make your Google Docs intelligent, automated, and AI-ready!*
