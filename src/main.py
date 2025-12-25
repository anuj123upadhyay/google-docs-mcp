"""Module defines the main entry point for the Google Docs MCP Actor.

This Actor provides comprehensive Google Docs integration through a Model Context Protocol server,
enabling AI assistants and automation tools to interact with Google Docs programmatically.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from apify import Actor

from .google_docs_client import GoogleDocsClient
from .document_analyzer import DocumentAnalyzer
from .mcp_server import MCPServer


async def main() -> None:
    """Main entry point for the Google Docs MCP Actor.

    This coroutine handles all Google Docs operations including reading, writing,
    creating documents, and running as an MCP server.
    """
    async with Actor:
        # Get input configuration
        actor_input = await Actor.get_input() or {}
        
        Actor.log.info('🚀 Starting Google Docs MCP Actor')
        Actor.log.info(f"Operation: {actor_input.get('operation', 'mcp_server')}")
        
        # Validate required inputs
        if not actor_input.get('googleCredentials'):
            Actor.log.error('❌ Google credentials are required!')
            await Actor.fail('Missing required parameter: googleCredentials')
            return
        
        try:
            # Initialize clients
            Actor.log.info('🔐 Authenticating with Google APIs...')
            google_client = GoogleDocsClient(actor_input['googleCredentials'])
            analyzer = DocumentAnalyzer()
            mcp_server = MCPServer(google_client, analyzer)
            
            Actor.log.info('✅ Authentication successful!')
            
            # Get operation type
            operation = actor_input.get('operation', 'mcp_server')
            
            # Execute operation
            result = await execute_operation(
                operation,
                actor_input,
                google_client,
                analyzer,
                mcp_server
            )
            
            # Save results to dataset
            if result:
                await Actor.push_data(result)
                Actor.log.info(f'💾 Results saved to dataset')
            
            Actor.log.info('✨ Actor finished successfully!')
            
        except Exception as e:
            Actor.log.error(f'❌ Error: {str(e)}')
            await Actor.fail(str(e))


async def execute_operation(
    operation: str,
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient,
    analyzer: DocumentAnalyzer,
    mcp_server: MCPServer
) -> Dict[str, Any]:
    """Execute the specified operation.
    
    Args:
        operation: Operation type to execute
        actor_input: Actor input configuration
        google_client: Google Docs API client
        analyzer: Document analyzer
        mcp_server: MCP server instance
        
    Returns:
        Operation result
    """
    Actor.log.info(f'📋 Executing operation: {operation}')
    
    if operation == 'read_document':
        return await read_document_operation(actor_input, google_client, analyzer)
    
    elif operation == 'write_document':
        return await write_document_operation(actor_input, google_client)
    
    elif operation == 'create_document':
        return await create_document_operation(actor_input, google_client)
    
    elif operation == 'update_document':
        return await update_document_operation(actor_input, google_client)
    
    elif operation == 'list_documents':
        return await list_documents_operation(actor_input, google_client)
    
    elif operation == 'analyze_document':
        return await analyze_document_operation(actor_input, google_client, analyzer)
    
    elif operation == 'search_content':
        return await search_content_operation(actor_input, google_client)
    
    elif operation == 'batch_operations':
        return await batch_operations_operation(actor_input, google_client, analyzer)
    
    elif operation == 'mcp_server':
        return await mcp_server_operation(actor_input, mcp_server)
    
    else:
        raise ValueError(f"Unknown operation: {operation}")


async def read_document_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient,
    analyzer: DocumentAnalyzer
) -> Dict[str, Any]:
    """Read a Google Docs document.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        analyzer: Document analyzer
        
    Returns:
        Document content and metadata
    """
    document_id = actor_input.get('documentId')
    if not document_id:
        raise ValueError('documentId is required for read_document operation')
    
    Actor.log.info(f'📖 Reading document: {document_id}')
    
    # Get document data
    document = google_client.read_document(document_id)
    text_content = google_client.get_document_text(document_id)
    metadata = google_client.get_document_metadata(document_id)
    
    # Analyze if requested
    analysis = None
    if actor_input.get('analysisOptions'):
        Actor.log.info('🔍 Analyzing document...')
        analysis = analyzer.analyze_document(text_content, actor_input['analysisOptions'])
    
    output_format = actor_input.get('outputFormat', 'json')
    
    result = {
        'operation': 'read_document',
        'documentId': document_id,
        'title': metadata['title'],
        'metadata': metadata,
        'textContent': text_content if output_format in ['plain_text', 'json'] else None,
        'analysis': analysis,
        'characterCount': len(text_content),
        'wordCount': len(text_content.split())
    }
    
    if output_format == 'markdown':
        result['markdown'] = text_content  # Could be enhanced with proper markdown conversion
    
    Actor.log.info(f'✅ Document read successfully: {len(text_content)} characters')
    return result


async def write_document_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient
) -> Dict[str, Any]:
    """Write content to a Google Docs document.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        
    Returns:
        Write operation result
    """
    document_id = actor_input.get('documentId')
    content = actor_input.get('content')
    
    if not document_id or not content:
        raise ValueError('documentId and content are required for write_document operation')
    
    Actor.log.info(f'✏️ Writing to document: {document_id}')
    
    result = google_client.write_to_document(
        document_id=document_id,
        content=content,
        position=actor_input.get('insertPosition'),
        formatting=actor_input.get('formatting')
    )
    
    Actor.log.info(f'✅ Content written successfully: {len(content)} characters')
    
    return {
        'operation': 'write_document',
        **result
    }


async def create_document_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient
) -> Dict[str, Any]:
    """Create a new Google Docs document.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        
    Returns:
        New document metadata
    """
    title = actor_input.get('documentTitle', 'Untitled Document')
    
    Actor.log.info(f'📝 Creating new document: {title}')
    
    result = google_client.create_document(title)
    
    # Add initial content if provided
    if actor_input.get('content'):
        Actor.log.info('Adding initial content...')
        google_client.write_to_document(
            document_id=result['documentId'],
            content=actor_input['content'],
            formatting=actor_input.get('formatting')
        )
    
    # Share document if requested
    if actor_input.get('shareSettings'):
        share_settings = actor_input['shareSettings']
        if share_settings.get('shareWithEmails'):
            Actor.log.info('Sharing document...')
            google_client.share_document(
                document_id=result['documentId'],
                email_addresses=share_settings['shareWithEmails'],
                role=share_settings.get('role', 'reader'),
                send_notification=share_settings.get('sendNotification', True)
            )
    
    Actor.log.info(f'✅ Document created: {result["documentUrl"]}')
    
    return {
        'operation': 'create_document',
        **result
    }


async def update_document_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient
) -> Dict[str, Any]:
    """Update an existing document (combines read and write).
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        
    Returns:
        Update operation result
    """
    document_id = actor_input.get('documentId')
    if not document_id:
        raise ValueError('documentId is required for update_document operation')
    
    Actor.log.info(f'🔄 Updating document: {document_id}')
    
    # Read current content
    current_text = google_client.get_document_text(document_id)
    
    # Write new content
    write_result = google_client.write_to_document(
        document_id=document_id,
        content=actor_input.get('content', ''),
        position=actor_input.get('insertPosition'),
        formatting=actor_input.get('formatting')
    )
    
    Actor.log.info('✅ Document updated successfully')
    
    return {
        'operation': 'update_document',
        'documentId': document_id,
        'previousLength': len(current_text),
        **write_result
    }


async def list_documents_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient
) -> Dict[str, Any]:
    """List accessible Google Docs documents.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        
    Returns:
        List of documents
    """
    max_results = actor_input.get('maxRetries', 100)
    
    Actor.log.info(f'📚 Listing documents (max: {max_results})...')
    
    documents = google_client.list_documents(max_results)
    
    Actor.log.info(f'✅ Found {len(documents)} documents')
    
    return {
        'operation': 'list_documents',
        'count': len(documents),
        'documents': documents
    }


async def analyze_document_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient,
    analyzer: DocumentAnalyzer
) -> Dict[str, Any]:
    """Analyze a document's content.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        analyzer: Document analyzer
        
    Returns:
        Analysis results
    """
    document_id = actor_input.get('documentId')
    if not document_id:
        raise ValueError('documentId is required for analyze_document operation')
    
    Actor.log.info(f'🔍 Analyzing document: {document_id}')
    
    # Get document content
    text_content = google_client.get_document_text(document_id)
    document_data = google_client.read_document(document_id)
    metadata = google_client.get_document_metadata(document_id)
    
    # Perform analysis
    analysis_options = actor_input.get('analysisOptions', {
        'wordCount': True,
        'extractKeywords': True,
        'summarize': True,
        'extractLinks': True,
        'detectLanguage': True
    })
    
    analysis = analyzer.analyze_document(text_content, analysis_options)
    
    # Extract tables if requested
    if analysis_options.get('extractTables', False):
        analysis['tables'] = analyzer.extract_tables(document_data)
    
    Actor.log.info('✅ Analysis complete')
    
    return {
        'operation': 'analyze_document',
        'documentId': document_id,
        'title': metadata['title'],
        'metadata': metadata,
        'analysis': analysis
    }


async def search_content_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient
) -> Dict[str, Any]:
    """Search for content in a document.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        
    Returns:
        Search results
    """
    document_id = actor_input.get('documentId')
    search_query = actor_input.get('searchQuery')
    
    if not document_id or not search_query:
        raise ValueError('documentId and searchQuery are required for search_content operation')
    
    Actor.log.info(f'🔎 Searching for "{search_query}" in document: {document_id}')
    
    matches = google_client.search_in_document(document_id, search_query)
    
    Actor.log.info(f'✅ Found {len(matches)} matches')
    
    return {
        'operation': 'search_content',
        'documentId': document_id,
        'query': search_query,
        'matchCount': len(matches),
        'matches': matches
    }


async def batch_operations_operation(
    actor_input: Dict[str, Any],
    google_client: GoogleDocsClient,
    analyzer: DocumentAnalyzer
) -> Dict[str, Any]:
    """Execute multiple operations in batch.
    
    Args:
        actor_input: Actor input configuration
        google_client: Google Docs API client
        analyzer: Document analyzer
        
    Returns:
        Batch operation results
    """
    batch_ops = actor_input.get('batchOperations', [])
    
    if not batch_ops:
        raise ValueError('batchOperations array is required')
    
    Actor.log.info(f'⚡ Executing {len(batch_ops)} batch operations...')
    
    results = []
    for i, op in enumerate(batch_ops):
        try:
            Actor.log.info(f'  Operation {i+1}/{len(batch_ops)}: {op.get("operation")}')
            
            # Execute each operation
            op_type = op.get('operation')
            op_params = op.get('params', {})
            op_params['documentId'] = op.get('documentId')
            
            # Add rate limiting delay
            if i > 0:
                delay = actor_input.get('rateLimitDelay', 100) / 1000.0
                await asyncio.sleep(delay)
            
            # Execute based on type
            if op_type == 'read':
                result = google_client.get_document_text(op['documentId'])
            elif op_type == 'write':
                result = google_client.write_to_document(**op_params)
            elif op_type == 'analyze':
                text = google_client.get_document_text(op['documentId'])
                result = analyzer.analyze_document(text, op_params.get('options', {}))
            else:
                result = {'error': f'Unknown operation type: {op_type}'}
            
            results.append({
                'index': i,
                'operation': op_type,
                'documentId': op.get('documentId'),
                'success': True,
                'result': result
            })
            
        except Exception as e:
            Actor.log.error(f'  ❌ Operation {i+1} failed: {str(e)}')
            results.append({
                'index': i,
                'operation': op.get('operation'),
                'documentId': op.get('documentId'),
                'success': False,
                'error': str(e)
            })
    
    success_count = sum(1 for r in results if r.get('success'))
    Actor.log.info(f'✅ Batch complete: {success_count}/{len(batch_ops)} successful')
    
    return {
        'operation': 'batch_operations',
        'totalOperations': len(batch_ops),
        'successfulOperations': success_count,
        'failedOperations': len(batch_ops) - success_count,
        'results': results
    }


async def mcp_server_operation(
    actor_input: Dict[str, Any],
    mcp_server: MCPServer
) -> Dict[str, Any]:
    """Run as MCP server and expose tools.
    
    Args:
        actor_input: Actor input configuration
        mcp_server: MCP server instance
        
    Returns:
        MCP server information
    """
    Actor.log.info('🖥️  Running in MCP Server mode')
    
    # Get MCP configuration
    mcp_config = actor_input.get('mcpServerConfig', {})
    
    # Export schema
    schema = mcp_server.export_mcp_schema()
    
    Actor.log.info(f'📡 MCP Server initialized with {len(schema["tools"])} tools')
    Actor.log.info('Available tools:')
    for tool in schema['tools']:
        Actor.log.info(f'  - {tool["name"]}: {tool["description"]}')
    
    # Process any webhook notifications
    webhook_url = mcp_config.get('webhookUrl')
    if webhook_url:
        Actor.log.info(f'📨 Webhook configured: {webhook_url}')
    
    return {
        'operation': 'mcp_server',
        'status': 'initialized',
        'schema': schema,
        'webhookUrl': webhook_url,
        'message': 'MCP Server is ready to accept tool requests'
    }

