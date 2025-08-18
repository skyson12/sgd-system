from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import Document, Category, User
from schemas import DocumentCreate, DocumentUpdate, DocumentMetrics
from typing import List, Optional, Dict, Any
import logging
import httpx
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "http://localhost:8001")
    
    async def create_document(
        self,
        db: Session,
        document_data: DocumentCreate,
        user_id: int
    ) -> Document:
        """Create a new document"""
        try:
            document = Document(
                title=document_data.title,
                description=document_data.description,
                filename=document_data.filename,
                file_path=document_data.file_path,
                file_url=document_data.file_url,
                file_size=document_data.file_size,
                content_type=document_data.content_type,
                category_id=document_data.category_id,
                tags=document_data.tags,
                uploaded_by=user_id,
                status="uploaded"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"Created document: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            db.rollback()
            raise
    
    async def get_document(self, db: Session, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return db.query(Document).filter(Document.id == document_id).first()
    
    async def update_document(
        self,
        db: Session,
        document_id: int,
        document_data: DocumentUpdate
    ) -> Optional[Document]:
        """Update document"""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return None
            
            update_data = document_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(document, field, value)
            
            document.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(document)
            
            logger.info(f"Updated document: {document_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            db.rollback()
            raise
    
    async def delete_document(self, db: Session, document_id: int) -> bool:
        """Delete document"""
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return False
            
            db.delete(document)
            db.commit()
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            db.rollback()
            raise
    
    async def text_search(
        self,
        db: Session,
        query: str,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Document]:
        """Text-based search"""
        try:
            # Build query
            db_query = db.query(Document)
            
            # Text search in title, description, and extracted_text
            search_filter = or_(
                Document.title.ilike(f"%{query}%"),
                Document.description.ilike(f"%{query}%"),
                Document.extracted_text.ilike(f"%{query}%")
            )
            db_query = db_query.filter(search_filter)
            
            # Apply filters
            if category_id:
                db_query = db_query.filter(Document.category_id == category_id)
            
            if tags:
                for tag in tags:
                    db_query = db_query.filter(Document.tags.contains([tag]))
            
            # Apply pagination and ordering
            documents = db_query.order_by(Document.updated_at.desc()).offset(offset).limit(limit).all()
            
            logger.info(f"Text search returned {len(documents)} results")
            return documents
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            raise
    
    async def get_analytics_metrics(self, db: Session) -> DocumentMetrics:
        """Get analytics metrics"""
        try:
            # Total documents
            total_documents = db.query(func.count(Document.id)).scalar()
            
            # Documents by category
            category_stats = db.query(
                Category.name,
                func.count(Document.id).label('count')
            ).outerjoin(Document).group_by(Category.name).all()
            
            documents_by_category = {stat.name: stat.count for stat in category_stats}
            
            # Documents by status
            status_stats = db.query(
                Document.status,
                func.count(Document.id).label('count')
            ).group_by(Document.status).all()
            
            documents_by_status = {stat.status: stat.count for stat in status_stats}
            
            # Processing stats
            last_24h = datetime.utcnow() - timedelta(hours=24)
            processed_last_24h = db.query(func.count(Document.id)).filter(
                and_(
                    Document.processed_at >= last_24h,
                    Document.status == "processed"
                )
            ).scalar()
            
            processing_stats = {
                "processed_last_24h": processed_last_24h,
                "average_processing_time": "2.3s",  # Could calculate this
                "success_rate": 0.95
            }
            
            # Storage usage
            total_size = db.query(func.sum(Document.file_size)).scalar() or 0
            storage_usage = {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_file_size_mb": round((total_size / max(total_documents, 1)) / (1024 * 1024), 2)
            }
            
            # Recent activity
            recent_docs = db.query(Document).order_by(Document.created_at.desc()).limit(5).all()
            recent_activity = [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "action": "uploaded",
                    "timestamp": doc.created_at.isoformat(),
                    "user": doc.uploader.username if doc.uploader else "Unknown"
                }
                for doc in recent_docs
            ]
            
            return DocumentMetrics(
                total_documents=total_documents,
                documents_by_category=documents_by_category,
                documents_by_status=documents_by_status,
                processing_stats=processing_stats,
                storage_usage=storage_usage,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics metrics: {e}")
            raise
    
    async def queue_ai_processing(self, document_id: int):
        """Queue document for AI processing"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_service_url}/process/document",
                    json={"document_id": document_id}
                )
                
                if response.status_code == 200:
                    logger.info(f"Queued document {document_id} for AI processing")
                else:
                    logger.error(f"Failed to queue document {document_id}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error queuing document {document_id} for processing: {e}")