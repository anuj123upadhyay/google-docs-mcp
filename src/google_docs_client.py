"""Google Docs API client wrapper for authentication and operations."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleDocsClient:
    """Wrapper class for Google Docs API interactions."""

    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]

    def __init__(self, credentials_config: Dict[str, Any]):
        """Initialize Google Docs client with credentials.
        
        Args:
            credentials_config: Dictionary containing authentication details
        """
        self.credentials_config = credentials_config
        self.credentials = None
        self.docs_service = None
        self.drive_service = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Google APIs using provided credentials."""
        cred_type = self.credentials_config.get('type', 'service_account')

        try:
            if cred_type == 'service_account':
                self._authenticate_service_account()
            elif cred_type == 'oauth2':
                self._authenticate_oauth2()
            else:
                raise ValueError(f"Unsupported credential type: {cred_type}")

            # Build services
            self.docs_service = build('docs', 'v1', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)

        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def _authenticate_service_account(self) -> None:
        """Authenticate using service account credentials."""
        service_account_json = self.credentials_config.get('serviceAccountJson')
        
        if not service_account_json:
            raise ValueError("Service account JSON is required")

        # Parse JSON if it's a string
        if isinstance(service_account_json, str):
            service_account_info = json.loads(service_account_json)
        else:
            service_account_info = service_account_json

        self.credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=self.SCOPES
        )

    def _authenticate_oauth2(self) -> None:
        """Authenticate using OAuth2 credentials."""
        access_token = self.credentials_config.get('oauthToken')
        refresh_token = self.credentials_config.get('oauthRefreshToken')

        if not access_token:
            raise ValueError("OAuth access token is required")

        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            scopes=self.SCOPES
        )

        # Refresh token if needed
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())

    def read_document(self, document_id: str) -> Dict[str, Any]:
        """Read a Google Docs document.
        
        Args:
            document_id: The ID of the document to read
            
        Returns:
            Dictionary containing document data
        """
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            return document
        except HttpError as error:
            raise Exception(f"Error reading document: {error}")

    def get_document_text(self, document_id: str) -> str:
        """Extract plain text from a document.
        
        Args:
            document_id: The ID of the document
            
        Returns:
            Plain text content of the document
        """
        try:
            document = self.read_document(document_id)
            text_content = []
            
            if 'body' in document and 'content' in document['body']:
                for element in document['body']['content']:
                    if 'paragraph' in element:
                        for text_run in element['paragraph'].get('elements', []):
                            if 'textRun' in text_run:
                                text_content.append(text_run['textRun']['content'])
                    elif 'table' in element:
                        # Extract text from tables
                        for row in element['table'].get('tableRows', []):
                            for cell in row.get('tableCells', []):
                                for content_element in cell.get('content', []):
                                    if 'paragraph' in content_element:
                                        for text_run in content_element['paragraph'].get('elements', []):
                                            if 'textRun' in text_run:
                                                text_content.append(text_run['textRun']['content'])
            
            return ''.join(text_content)
        except Exception as error:
            raise Exception(f"Error extracting text: {error}")

    def create_document(self, title: str) -> Dict[str, Any]:
        """Create a new Google Docs document.
        
        Args:
            title: Title for the new document
            
        Returns:
            Dictionary containing document metadata
        """
        try:
            document = self.docs_service.documents().create(body={'title': title}).execute()
            return {
                'documentId': document.get('documentId'),
                'title': document.get('title'),
                'revisionId': document.get('revisionId'),
                'documentUrl': f"https://docs.google.com/document/d/{document.get('documentId')}/edit"
            }
        except HttpError as error:
            raise Exception(f"Error creating document: {error}")

    def write_to_document(
        self,
        document_id: str,
        content: str,
        position: Optional[Dict[str, Any]] = None,
        formatting: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Write content to a document.
        
        Args:
            document_id: The ID of the document
            content: Text content to insert
            position: Where to insert (index or location type)
            formatting: Text formatting options
            
        Returns:
            Result of the write operation
        """
        try:
            # Determine insert position
            insert_index = 1  # Default: start of document
            
            if position:
                if 'index' in position:
                    insert_index = position['index']
                elif position.get('location') == 'end':
                    # Get document to find end position
                    doc = self.read_document(document_id)
                    insert_index = doc['body']['content'][-1]['endIndex'] - 1
                elif position.get('location') == 'replace_all':
                    # Delete all content first, then insert
                    doc = self.read_document(document_id)
                    end_index = doc['body']['content'][-1]['endIndex']
                    requests = [
                        {
                            'deleteContentRange': {
                                'range': {
                                    'startIndex': 1,
                                    'endIndex': end_index - 1
                                }
                            }
                        }
                    ]
                    self.docs_service.documents().batchUpdate(
                        documentId=document_id,
                        body={'requests': requests}
                    ).execute()
                    insert_index = 1

            # Build insert request
            requests = [
                {
                    'insertText': {
                        'location': {'index': insert_index},
                        'text': content
                    }
                }
            ]

            # Add formatting if specified
            if formatting:
                text_style = {}
                
                if formatting.get('bold'):
                    text_style['bold'] = True
                if formatting.get('italic'):
                    text_style['italic'] = True
                if formatting.get('fontSize'):
                    text_style['fontSize'] = {'magnitude': formatting['fontSize'], 'unit': 'PT'}
                if formatting.get('fontFamily'):
                    text_style['weightedFontFamily'] = {'fontFamily': formatting['fontFamily']}
                if formatting.get('foregroundColor'):
                    text_style['foregroundColor'] = self._parse_color(formatting['foregroundColor'])
                if formatting.get('backgroundColor'):
                    text_style['backgroundColor'] = self._parse_color(formatting['backgroundColor'])

                if text_style:
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': insert_index,
                                'endIndex': insert_index + len(content)
                            },
                            'textStyle': text_style,
                            'fields': ','.join(text_style.keys())
                        }
                    })

            # Execute batch update
            result = self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

            return {
                'success': True,
                'documentId': document_id,
                'insertedText': content,
                'position': insert_index,
                'replies': result.get('replies', [])
            }

        except HttpError as error:
            raise Exception(f"Error writing to document: {error}")

    def _parse_color(self, color_hex: str) -> Dict[str, Any]:
        """Parse hex color to Google Docs RGB format.
        
        Args:
            color_hex: Hex color code (e.g., #FF0000)
            
        Returns:
            RGB color dictionary
        """
        color_hex = color_hex.lstrip('#')
        r = int(color_hex[0:2], 16) / 255.0
        g = int(color_hex[2:4], 16) / 255.0
        b = int(color_hex[4:6], 16) / 255.0
        
        return {
            'color': {
                'rgbColor': {
                    'red': r,
                    'green': g,
                    'blue': b
                }
            }
        }

    def list_documents(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """List Google Docs documents accessible to the authenticated user.
        
        Args:
            max_results: Maximum number of documents to return
            
        Returns:
            List of document metadata
        """
        try:
            query = "mimeType='application/vnd.google-apps.document'"
            results = self.drive_service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, createdTime, modifiedTime, owners, webViewLink)"
            ).execute()
            
            return results.get('files', [])
        except HttpError as error:
            raise Exception(f"Error listing documents: {error}")

    def search_in_document(self, document_id: str, search_query: str) -> List[Dict[str, Any]]:
        """Search for text within a document.
        
        Args:
            document_id: The ID of the document
            search_query: Text to search for
            
        Returns:
            List of matches with positions
        """
        try:
            text_content = self.get_document_text(document_id)
            matches = []
            
            # Simple text search (case-insensitive)
            start = 0
            search_lower = search_query.lower()
            text_lower = text_content.lower()
            
            while True:
                index = text_lower.find(search_lower, start)
                if index == -1:
                    break
                    
                matches.append({
                    'position': index,
                    'text': text_content[index:index + len(search_query)],
                    'context': text_content[max(0, index - 50):index + len(search_query) + 50]
                })
                start = index + 1
            
            return matches
        except Exception as error:
            raise Exception(f"Error searching document: {error}")

    def share_document(
        self,
        document_id: str,
        email_addresses: List[str],
        role: str = 'reader',
        send_notification: bool = True
    ) -> Dict[str, Any]:
        """Share a document with specified users.
        
        Args:
            document_id: The ID of the document
            email_addresses: List of email addresses to share with
            role: Permission level ('reader', 'writer', 'commenter')
            send_notification: Whether to send email notification
            
        Returns:
            Results of sharing operation
        """
        try:
            results = []
            for email in email_addresses:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email
                }
                
                result = self.drive_service.permissions().create(
                    fileId=document_id,
                    body=permission,
                    sendNotificationEmail=send_notification
                ).execute()
                
                results.append({
                    'email': email,
                    'role': role,
                    'permissionId': result.get('id')
                })
            
            return {
                'success': True,
                'documentId': document_id,
                'permissions': results
            }
        except HttpError as error:
            raise Exception(f"Error sharing document: {error}")

    def get_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """Get detailed metadata about a document.
        
        Args:
            document_id: The ID of the document
            
        Returns:
            Document metadata
        """
        try:
            # Get doc info
            doc = self.read_document(document_id)
            
            # Get drive metadata
            drive_metadata = self.drive_service.files().get(
                fileId=document_id,
                fields="id,name,createdTime,modifiedTime,owners,lastModifyingUser,size,webViewLink"
            ).execute()
            
            return {
                'documentId': document_id,
                'title': doc.get('title'),
                'revisionId': doc.get('revisionId'),
                'createdTime': drive_metadata.get('createdTime'),
                'modifiedTime': drive_metadata.get('modifiedTime'),
                'owners': drive_metadata.get('owners', []),
                'lastModifyingUser': drive_metadata.get('lastModifyingUser', {}),
                'webViewLink': drive_metadata.get('webViewLink'),
                'documentUrl': f"https://docs.google.com/document/d/{document_id}/edit"
            }
        except Exception as error:
            raise Exception(f"Error getting metadata: {error}")
