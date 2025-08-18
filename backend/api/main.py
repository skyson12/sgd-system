from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import httpx
from datetime import datetime
import uuid
import os

from database import get_db, engine
from models import Document, User, Category, AuditLog
from schemas import (
    DocumentCreate, DocumentResponse, DocumentUpdate,
    UserResponse, CategoryResponse, SearchQuery,
    DocumentMetrics, SystemHealth
)
from auth import verify_token, get_current_user
from storage import MinIOClient
from services.document_service import DocumentService
from services.search_service import SearchService
from services.audit_service import AuditService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SGD Document Management API",
    description="Intelligent Document Management System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Services
minio_client = MinIOClient()
document_service = DocumentService()
search_service = SearchService()
audit_service = AuditService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting SGD Document Management API...")
    
    # Initialize MinIO buckets
    await minio_client.create_bucket_if_not_exists("documents")
    
    # Initialize search service
    await search_service.initialize_schema()
    
    logger.info("API startup complete")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/health/detailed", response_model=SystemHealth)
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with service status"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check MinIO
    try:
        await minio_client.health_check()
        storage_status = "healthy"
    except Exception as e:
        logger.error(f"MinIO health check failed: {e}")
        storage_status = "unhealthy"
    
    # Check Weaviate
    try:
        weaviate_status = await search_service.health_check()
    except Exception as e:
        logger.error(f"Weaviate health check failed: {e}")
        weaviate_status = "unhealthy"
    
    # Check AI service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{os.getenv('AI_SERVICE_URL')}/health")
            ai_status = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.error(f"AI service health check failed: {e}")
        ai_status = "unhealthy"
    
    return SystemHealth(
        status="healthy" if all([
            db_status == "healthy",
            storage_status == "healthy", 
            weaviate_status == "healthy",
            ai_status == "healthy"
        ]) else "degraded",
        database=db_status,
        storage=storage_status,
        search=weaviate_status,
        ai_service=ai_status,
        timestamp=datetime.utcnow()
    )

@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new document"""
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'text/plain']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to MinIO
        file_url = await minio_client.upload_file(
            bucket="documents",
            object_name=unique_filename,
            file_data=file.file,
            content_type=file.content_type
        )
        
        # Create document record
        document_data = DocumentCreate(
            title=title,
            description=description,
            filename=file.filename,
            file_path=unique_filename,
            file_url=file_url,
            file_size=file.size,
            content_type=file.content_type,
            category_id=category_id,
            tags=tags.split(',') if tags else [],
            uploaded_by=current_user.id
        )
        
        document = await document_service.create_document(db, document_data, current_user.id)
        
        # Log audit event
        await audit_service.log_action(
            user_id=current_user.id,
            action="DOCUMENT_UPLOAD",
            resource_type="document",
            resource_id=document.id,
            details={"filename": file.filename, "size": file.size}
        )
        
        # Queue for AI processing
        await document_service.queue_ai_processing(document.id)
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Document upload failed")

@app.get("/documents/search")
async def search_documents(
    q: str,
    semantic: bool = False,
    category_id: Optional[int] = None,
    tags: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search documents"""
    try:
        if semantic:
            results = await search_service.semantic_search(
                query=q,
                limit=limit,
                offset=offset,
                filters={
                    "category_id": category_id,
                    "tags": tags.split(',') if tags else None
                }
            )
        else:
            results = await document_service.text_search(
                db=db,
                query=q,
                category_id=category_id,
                tags=tags.split(',') if tags else None,
                limit=limit,
                offset=offset
            )
        
        # Log search action
        await audit_service.log_action(
            user_id=current_user.id,
            action="DOCUMENT_SEARCH",
            resource_type="search",
            details={
                "query": q,
                "semantic": semantic,
                "results_count": len(results)
            }
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID"""
    document = await document_service.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Log access
    await audit_service.log_action(
        user_id=current_user.id,
        action="DOCUMENT_ACCESS",
        resource_type="document",
        resource_id=document_id
    )
    
    return DocumentResponse.from_orm(document)

@app.post("/documents/{document_id}/chat")
async def chat_with_document(
    document_id: int,
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat with a specific document using RAG"""
    try:
        # Verify document exists
        document = await document_service.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Use AI service for RAG
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.getenv('AI_SERVICE_URL')}/rag/chat",
                json={
                    "document_id": document_id,
                    "query": query,
                    "context_limit": 5
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="AI service error")
            
            result = response.json()
        
        # Log chat action
        await audit_service.log_action(
            user_id=current_user.id,
            action="DOCUMENT_CHAT",
            resource_type="document",
            resource_id=document_id,
            details={"query": query}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Document chat failed: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")

@app.get("/analytics/metrics", response_model=DocumentMetrics)
async def get_analytics_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics metrics"""
    try:
        metrics = await document_service.get_analytics_metrics(db)
        return metrics
    except Exception as e:
        logger.error(f"Analytics metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Analytics failed")

@app.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return [CategoryResponse.from_orm(cat) for cat in categories]

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)