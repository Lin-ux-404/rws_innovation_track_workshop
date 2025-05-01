import os
import json
import uuid
import base64
from datetime import datetime
from typing import Annotated, List, Optional
import requests
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure.core.credentials import AzureKeyCredential
from semantic_kernel.functions import kernel_function

class RAGPlugin:
    """A plugin for Retrieval Augmented Generation using Azure Blob Storage and Azure AI Search."""
    
    def __init__(self):
        # Azure Blob Storage settings
        self.connection_string = os.getenv("RAG_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("RAG_DOCUMENTS_CONTAINER_NAME")
        
        # Azure AI Search settings
        self.search_endpoint = os.getenv("SEARCH_SERVICE_ENDPOINT")
        self.search_key = os.getenv("SEARCH_SERVICE_ADMIN_KEY")
        self.search_index_name = os.getenv("SEARCH_INDEX_NAME", "documents-index")
        
        # Validate settings
        if not self.connection_string or not self.container_name:
            raise ValueError("RAG_STORAGE_CONNECTION_STRING and RAG_DOCUMENTS_CONTAINER_NAME environment variables must be set")
        
        if not self.search_endpoint or not self.search_key:
            raise ValueError("SEARCH_SERVICE_ENDPOINT and SEARCH_SERVICE_ADMIN_KEY environment variables must be set")
        
        # Initialize clients
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.search_index_name,
            credential=AzureKeyCredential(self.search_key)
        )
    
    @kernel_function(description="Upload a document to the knowledge base.")
    def upload_document(
        self,
        content: Annotated[str, "The text content of the document"],
        title: Annotated[str, "The title of the document"],
        source: Annotated[str, "The source of the document (e.g., 'internal', 'web', 'manual')"] = "internal",
        document_type: Annotated[str, "The type of the document (e.g., 'report', 'article', 'guide')"] = "document"
    ) -> str:
        """Upload a text document to the knowledge base for later retrieval."""
        try:
            # Generate a unique ID for the document
            doc_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            # Create metadata for the document
            metadata = {
                "id": doc_id,
                "title": title,
                "source": source,
                "documentType": document_type,
                "uploadTimestamp": timestamp
            }
            
            # Upload the document content to blob storage
            blob_name = f"{doc_id}.txt"
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(content, overwrite=True)
            
            # Create a search document with the content and metadata
            search_document = {
                "id": doc_id,
                "title": title,
                "content": content,
                "source": source,
                "documentType": document_type,
                "uploadTimestamp": timestamp,
                "blobName": blob_name
            }
            
            # Upload to search index
            self.search_client.upload_documents([search_document])
            
            return f"Document '{title}' (ID: {doc_id}) successfully uploaded to the knowledge base."
            
        except Exception as e:
            return f"Error uploading document: {str(e)}"
    
    @kernel_function(description="Search for information in the knowledge base.")
    def search_knowledge_base(
        self,
        query: Annotated[str, "The search query"],
        top: Annotated[int, "The number of results to return"] = 3,
        use_semantic_search: Annotated[bool, "Whether to use semantic search capabilities"] = True
    ) -> str:
        """Search for information in the knowledge base using the provided query."""
        try:
            # Set up search options
            search_options = {
                "top": top,
                "include_total_count": True,
                "select": "id,title,content,source,documentType,uploadTimestamp"
            }
            
            if use_semantic_search:
                search_options["query_type"] = QueryType.SEMANTIC
                search_options["semantic_configuration_name"] = "default"
            
            # Execute the search
            results = self.search_client.search(query, **search_options)
            
            # Process and format the results
            search_results = []
            total_count = results.get_count()
            
            for result in results:
                doc = {
                    "id": result["id"],
                    "title": result["title"],
                    "content": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"],
                    "source": result["source"],
                    "documentType": result["documentType"],
                    "uploadTimestamp": result["uploadTimestamp"]
                }
                search_results.append(doc)
            
            # Format output
            formatted_results = json.dumps(search_results, indent=2)
            response = f"Found {total_count} results for query '{query}'.\n\nTop {len(search_results)} results:\n{formatted_results}"
            
            return response
            
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    @kernel_function(description="Retrieve the full content of a specific document by ID.")
    def get_document_by_id(
        self,
        document_id: Annotated[str, "The ID of the document to retrieve"]
    ) -> str:
        """Retrieve the complete content of a specific document by its ID."""
        try:
            # Search for the document by ID
            result = self.search_client.get_document(document_id)
            
            if not result:
                return f"Document with ID '{document_id}' not found."
            
            # Format the document
            formatted_doc = {
                "id": result["id"],
                "title": result["title"],
                "content": result["content"],
                "source": result["source"],
                "documentType": result["documentType"],
                "uploadTimestamp": result["uploadTimestamp"]
            }
            
            # Format output
            formatted_result = json.dumps(formatted_doc, indent=2)
            return f"Document retrieved:\n{formatted_result}"
            
        except Exception as e:
            return f"Error retrieving document: {str(e)}"
