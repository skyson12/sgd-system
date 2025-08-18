import openai
import weaviate
import os
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from schemas import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        # OpenAI configuration
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Weaviate client
        self.weaviate_client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://localhost:8080")
        )
        
    async def initialize(self):
        """Initialize RAG service"""
        try:
            logger.info("RAG service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if RAG service is ready"""
        try:
            # Test connections
            self.weaviate_client.schema.get()
            return True
        except Exception as e:
            logger.error(f"RAG service not ready: {e}")
            return False
    
    async def index_document(
        self,
        document_id: int,
        title: str,
        content: str,
        summary: str = "",
        category: str = "",
        tags: List[str] = None
    ):
        """Index document in Weaviate for RAG"""
        try:
            document_object = {
                "title": title,
                "content": content,
                "summary": summary,
                "category": category,
                "tags": tags or [],
                "document_id": document_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Create object in Weaviate
            result = self.weaviate_client.data_object.create(
                data_object=document_object,
                class_name="Document"
            )
            
            logger.info(f"Indexed document {document_id} for RAG: {result}")
            
        except Exception as e:
            logger.error(f"Error indexing document {document_id} for RAG: {e}")
            raise
    
    async def chat(
        self,
        query: str,
        document_id: Optional[int] = None,
        context_limit: int = 5
    ) -> ChatResponse:
        """Chat with documents using RAG"""
        try:
            # Search for relevant documents
            relevant_docs = await self._search_relevant_documents(
                query=query,
                document_id=document_id,
                limit=context_limit
            )
            
            # Build context from relevant documents
            context = self._build_context(relevant_docs)
            
            # Generate response using OpenAI
            response_text = await self._generate_response(query, context)
            
            # Calculate confidence (simple heuristic)
            confidence = min(len(relevant_docs) / context_limit, 1.0)
            
            # Prepare sources
            sources = [
                {
                    "document_id": doc.get("document_id"),
                    "title": doc.get("title", "Unknown"),
                    "excerpt": doc.get("content", "")[:200] + "...",
                    "relevance": 0.8  # Placeholder
                }
                for doc in relevant_docs
            ]
            
            return ChatResponse(
                response=response_text,
                sources=sources,
                confidence=confidence,
                conversation_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"RAG chat failed: {e}")
            raise
    
    async def _search_relevant_documents(
        self,
        query: str,
        document_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        try:
            # Build search query
            search_query = self.weaviate_client.query.get("Document", [
                "title", "content", "summary", "category", "tags", "document_id"
            ]).with_near_text({
                "concepts": [query]
            }).with_limit(limit)
            
            # Add filter for specific document if provided
            if document_id:
                search_query = search_query.with_where({
                    "path": ["document_id"],
                    "operator": "Equal",
                    "valueInt": document_id
                })
            
            # Execute search
            result = search_query.do()
            
            # Extract documents
            documents = []
            if "data" in result and "Get" in result["data"] and "Document" in result["data"]["Get"]:
                documents = result["data"]["Get"]["Document"]
            
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from documents"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            title = doc.get("title", "Unknown Document")
            content = doc.get("content", "")
            summary = doc.get("summary", "")
            
            # Use summary if available, otherwise truncate content
            text = summary if summary else content[:500]
            
            context_parts.append(f"Document {i} - {title}:\n{text}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_response(self, query: str, context: str) -> str:
        """Generate response using OpenAI with context"""
        try:
            system_prompt = """You are an intelligent document assistant. You help users find information in their documents and answer questions based on the provided context. 

Instructions:
- Answer questions based only on the provided document context
- If the context doesn't contain enough information, say so clearly
- Provide specific references to documents when possible
- Be concise but comprehensive
- If asked about multiple documents, compare and synthesize the information
"""

            user_prompt = f"""Context from documents:
{context}

Question: {query}

Please provide a helpful answer based on the document context above."""

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating a response. Please try again."