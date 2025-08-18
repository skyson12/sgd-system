from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    filename: str
    file_path: str
    file_url: str
    file_size: int
    content_type: str
    category_id: Optional[int] = None
    tags: List[str] = []
    uploaded_by: int

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None

class DocumentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    filename: str
    file_url: str
    file_size: int
    content_type: str
    status: DocumentStatus
    approval_status: ApprovalStatus
    extracted_text: Optional[str]
    summary: Optional[str]
    entities: Optional[Dict[str, Any]]
    classification: Optional[str]
    classification_confidence: Optional[float]
    tags: List[str]
    metadata: Optional[Dict[str, Any]]
    category_id: Optional[int]
    uploaded_by: int
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    created_at: datetime

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    semantic: bool = False
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)

class DocumentMetrics(BaseModel):
    total_documents: int
    documents_by_category: Dict[str, int]
    documents_by_status: Dict[str, int]
    processing_stats: Dict[str, Any]
    storage_usage: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]

class SystemHealth(BaseModel):
    status: str
    database: str
    storage: str
    search: str
    ai_service: str
    timestamp: datetime

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: Optional[int] = None
    context_limit: int = Field(default=5, le=10)

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    timestamp: datetime