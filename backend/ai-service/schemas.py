from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ProcessDocumentRequest(BaseModel):
    document_id: int
    priority: str = "normal"

class ClassificationResult(BaseModel):
    category: str
    confidence: float
    subcategory: Optional[str] = None
    tags: List[str] = []

class NLPAnalysis(BaseModel):
    entities: Dict[str, List[str]]
    language: str
    sentiment: Optional[Dict[str, float]] = None
    keywords: List[str] = []

class ProcessDocumentResponse(BaseModel):
    document_id: int
    status: str
    extracted_text: str
    summary: str
    entities: Dict[str, List[str]]
    classification: ClassificationResult
    processing_time: float
    timestamp: datetime

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    document_id: Optional[int] = None
    context_limit: int = Field(default=5, le=10)
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    conversation_id: str
    timestamp: datetime

class DocumentAnalysis(BaseModel):
    extracted_text: str
    summary: str
    entities: Dict[str, List[str]]
    classification: ClassificationResult
    language: str
    sentiment: Optional[Dict[str, float]]
    timestamp: datetime

class HealthStatus(BaseModel):
    status: str
    nlp_service: str
    ocr_service: str
    classification_service: str
    rag_service: str
    timestamp: datetime