import weaviate
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        self.client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            timeout_config=(5, 15)
        )
    
    async def initialize_schema(self):
        """Initialize Weaviate schema for documents"""
        try:
            # Check if schema already exists
            existing_classes = self.client.schema.get()["classes"]
            class_names = [cls["class"] for cls in existing_classes]
            
            if "Document" not in class_names:
                document_class = {
                    "class": "Document",
                    "description": "A document in the SGD system",
                    "vectorizer": "text2vec-openai",
                    "properties": [
                        {
                            "name": "title",
                            "dataType": ["string"],
                            "description": "The title of the document"
                        },
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "The extracted text content of the document"
                        },
                        {
                            "name": "summary",
                            "dataType": ["text"],
                            "description": "AI-generated summary of the document"
                        },
                        {
                            "name": "category",
                            "dataType": ["string"],
                            "description": "Document category"
                        },
                        {
                            "name": "tags",
                            "dataType": ["string[]"],
                            "description": "Document tags"
                        },
                        {
                            "name": "document_id",
                            "dataType": ["int"],
                            "description": "Reference to the document ID in PostgreSQL"
                        },
                        {
                            "name": "file_type",
                            "dataType": ["string"],
                            "description": "File type/content type"
                        },
                        {
                            "name": "created_at",
                            "dataType": ["date"],
                            "description": "Creation timestamp"
                        }
                    ]
                }
                
                self.client.schema.create_class(document_class)
                logger.info("Created Weaviate Document schema")
            else:
                logger.info("Weaviate Document schema already exists")
                
        except Exception as e:
            logger.error(f"Error initializing Weaviate schema: {e}")
            raise
    
    async def index_document(
        self,
        document_id: int,
        title: str,
        content: str,
        summary: str = None,
        category: str = None,
        tags: List[str] = None,
        file_type: str = None
    ) -> str:
        """Index a document in Weaviate"""
        try:
            document_object = {
                "title": title,
                "content": content,
                "summary": summary or "",
                "category": category or "",
                "tags": tags or [],
                "document_id": document_id,
                "file_type": file_type or "",
                "created_at": self._get_current_datetime()
            }
            
            # Create object in Weaviate
            result = self.client.data_object.create(
                data_object=document_object,
                class_name="Document"
            )
            
            vector_id = result
            logger.info(f"Indexed document {document_id} with vector ID {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {e}")
            raise
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        try:
            # Build search query
            search_query = self.client.query.get("Document", [
                "title", "content", "summary", "category", "tags", 
                "document_id", "file_type", "created_at"
            ]).with_near_text({
                "concepts": [query]
            }).with_limit(limit).with_offset(offset)
            
            # Add filters if provided
            if filters:
                where_conditions = []
                
                if filters.get("category_id"):
                    where_conditions.append({
                        "path": ["category"],
                        "operator": "Equal",
                        "valueString": str(filters["category_id"])
                    })
                
                if filters.get("tags"):
                    for tag in filters["tags"]:
                        where_conditions.append({
                            "path": ["tags"],
                            "operator": "Equal",
                            "valueString": tag
                        })
                
                if where_conditions:
                    if len(where_conditions) == 1:
                        search_query = search_query.with_where(where_conditions[0])
                    else:
                        search_query = search_query.with_where({
                            "operator": "And",
                            "operands": where_conditions
                        })
            
            # Execute search
            result = search_query.do()
            
            # Extract documents from result
            documents = []
            if "data" in result and "Get" in result["data"] and "Document" in result["data"]["Get"]:
                documents = result["data"]["Get"]["Document"]
            
            logger.info(f"Semantic search returned {len(documents)} results")
            return documents
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    async def delete_document(self, vector_id: str):
        """Delete document from Weaviate"""
        try:
            self.client.data_object.delete(vector_id, class_name="Document")
            logger.info(f"Deleted document with vector ID {vector_id}")
        except Exception as e:
            logger.error(f"Error deleting document {vector_id}: {e}")
            raise
    
    async def health_check(self) -> str:
        """Check Weaviate health"""
        try:
            # Check if we can access the schema
            self.client.schema.get()
            return "healthy"
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            return "unhealthy"
    
    def _get_current_datetime(self) -> str:
        """Get current datetime in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"