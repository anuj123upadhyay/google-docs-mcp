"""Model Context Protocol server implementation for Google Docs."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from apify import Actor

from .google_docs_client import GoogleDocsClient
from .document_analyzer import DocumentAnalyzer


class MCPServer:
    """MCP (Model Context Protocol) server for Google Docs operations."""

    def __init__(self, google_client: GoogleDocsClient, analyzer: DocumentAnalyzer):
        """Initialize MCP server.
        
        Args:
            google_client: Google Docs API client
            analyzer: Document analyzer instance
        """
        self.client = google_client
        self.analyzer = analyzer
        
        # Register available tools
        self.tools = {
            'read_document': self.tool_read_document,
            'write_document': self.tool_write_document,
            'create_document': self.tool_create_document,
            'search_documents': self.tool_search_documents,
            'analyze_content': self.tool_analyze_content,
            'list_documents': self.tool_list_documents,
            'get_metadata': self.tool_get_metadata,
            'share_document': self.tool_share_document,
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get MCP tool definitions.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                'name': 'read_document',
                'description': 'Read the full content of a Google Docs document',
                'parameters': {
                    'document_id': {
                        'type': 'string',
                        'description': 'The ID of the document to read',
                        'required': True
                    },
                    'format': {
                        'type': 'string',
                        'description': 'Output format: plain_text, structured, or full',
                        'default': 'plain_text'
                    }
                }
            },
            {
                'name': 'write_document',
                'description': 'Write or insert content into a Google Docs document',
                'parameters': {
                    'document_id': {
                        'type': 'string',
                        'description': 'The ID of the document',
                        'required': True
                    },
                    'content': {
                        'type': 'string',
                        'description': 'Text content to insert',
                        'required': True
                    },
                    'position': {
                        'type': 'object',
                        'description': 'Where to insert the content'
                    },
                    'formatting': {
                        'type': 'object',
                        'description': 'Text formatting options'
                    }
                }
            },
            {
                'name': 'create_document',
                'description': 'Create a new Google Docs document',
                'parameters': {
                    'title': {
                        'type': 'string',
                        'description': 'Title for the new document',
                        'required': True
                    },
                    'initial_content': {
                        'type': 'string',
                        'description': 'Optional initial content'
                    }
                }
            },
            {
                'name': 'search_documents',
                'description': 'Search for text within a document',
                'parameters': {
                    'document_id': {
                        'type': 'string',
                        'description': 'The ID of the document',
                        'required': True
                    },
                    'query': {
                        'type': 'string',
                        'description': 'Search query text',
                        'required': True
                    }
                }
            },
            {
                'name': 'analyze_content',
                'description': 'Analyze document content (statistics, keywords, summary)',
                'parameters': {
                    'document_id': {
                        'type': 'string',
                        'description': 'The ID of the document',
                        'required': True
                    },
                    'options': {
                        'type': 'object',
                        'description': 'Analysis options'
                    }
                }
            },
            {
                'name': 'list_documents',
                'description': 'List accessible Google Docs documents',
                'parameters': {
                    'max_results': {
                        'type': 'integer',
                        'description': 'Maximum number of documents to return',
                        'default': 50
                    }
                }
            },
            {
                'name': 'get_metadata',
                'description': 'Get metadata about a document',
                'parameters': {
                    'document_id': {
                        'type': 'string',
                        'description': 'The ID of the document',
                        'required': True
                    }
                }
            },
            {
                'name': 'share_document',
                'description': 'Share a document with specified users',
                'parameters': {
                    'document_id': {
                        'type': 'string',
                        'description': 'The ID of the document',
                        'required': True
                    },
                    'emails': {
                        'type': 'array',
                        'description': 'List of email addresses',
                        'required': True
                    },
                    'role': {
                        'type': 'string',
                        'description': 'Permission role: reader, writer, or commenter',
                        'default': 'reader'
                    }
                }
            }
        ]

    async def handle_request(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP tool request.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}",
                'available_tools': list(self.tools.keys())
            }

        try:
            result = await self.tools[tool_name](parameters)
            return {
                'success': True,
                'tool': tool_name,
                'result': result
            }
        except Exception as e:
            Actor.log.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                'success': False,
                'tool': tool_name,
                'error': str(e)
            }

    async def tool_read_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read document tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            Document content
        """
        document_id = params['document_id']
        output_format = params.get('format', 'plain_text')

        if output_format == 'plain_text':
            text = self.client.get_document_text(document_id)
            return {'content': text}
        elif output_format == 'structured':
            document = self.client.read_document(document_id)
            return {'document': document}
        else:  # full
            document = self.client.read_document(document_id)
            text = self.client.get_document_text(document_id)
            return {
                'text': text,
                'document': document
            }

    async def tool_write_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write to document tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            Write operation result
        """
        result = self.client.write_to_document(
            document_id=params['document_id'],
            content=params['content'],
            position=params.get('position'),
            formatting=params.get('formatting')
        )
        return result

    async def tool_create_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create document tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            New document metadata
        """
        result = self.client.create_document(params['title'])
        
        # Add initial content if provided
        if 'initial_content' in params and params['initial_content']:
            self.client.write_to_document(
                document_id=result['documentId'],
                content=params['initial_content']
            )
            result['initialContentAdded'] = True
        
        return result

    async def tool_search_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search in document tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            Search results
        """
        matches = self.client.search_in_document(
            document_id=params['document_id'],
            search_query=params['query']
        )
        return {
            'query': params['query'],
            'matches': matches,
            'count': len(matches)
        }

    async def tool_analyze_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document content tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            Analysis results
        """
        document_id = params['document_id']
        options = params.get('options', {})
        
        # Get document text
        text = self.client.get_document_text(document_id)
        
        # Perform analysis
        analysis = self.analyzer.analyze_document(text, options)
        
        # Get full document for table extraction
        if options.get('extractTables', False):
            document = self.client.read_document(document_id)
            analysis['tables'] = self.analyzer.extract_tables(document)
        
        return analysis

    async def tool_list_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List documents tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            List of documents
        """
        max_results = params.get('max_results', 50)
        documents = self.client.list_documents(max_results)
        return {
            'documents': documents,
            'count': len(documents)
        }

    async def tool_get_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            Document metadata
        """
        metadata = self.client.get_document_metadata(params['document_id'])
        return metadata

    async def tool_share_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Share document tool implementation.
        
        Args:
            params: Tool parameters
            
        Returns:
            Sharing result
        """
        result = self.client.share_document(
            document_id=params['document_id'],
            email_addresses=params['emails'],
            role=params.get('role', 'reader'),
            send_notification=params.get('send_notification', True)
        )
        return result

    def export_mcp_schema(self) -> Dict[str, Any]:
        """Export MCP server schema.
        
        Returns:
            MCP schema dictionary
        """
        return {
            'name': 'google-docs-mcp',
            'version': '1.0.0',
            'description': 'Model Context Protocol server for Google Docs integration',
            'tools': self.get_tool_definitions(),
            'capabilities': {
                'read': True,
                'write': True,
                'create': True,
                'analyze': True,
                'search': True,
                'share': True
            }
        }
