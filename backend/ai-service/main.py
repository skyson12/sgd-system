from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import httpx
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

from services.ocr_service import OCRService
from services.nlp_service import NLPService
from services.classification_service import ClassificationService
from services.rag_service import RAGService
from schemas import (
    ProcessDocumentRequest, ProcessDocumentResponse,
    ChatRequest, ChatResponse, ClassificationResult,
    DocumentAnalysis, HealthStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SGD AI Service",
    description="AI/ML microservice for document processing",
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

# Services
ocr_service = OCRService()
nlp_service = NLPService()
classification_service = ClassificationService()
rag_service = RAGService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting SGD AI Service...")
    
    # Initialize services
    await nlp_service.initialize()
    await classification_service.initialize()
    await rag_service.initialize()
    
    logger.info("AI Service startup complete")

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    try:
        # Test core services
        nlp_status = "healthy" if nlp_service.is_ready() else "unhealthy"
        ocr_status = "healthy" if ocr_service.is_ready() else "unhealthy"
        classification_status = "healthy" if classification_service.is_ready() else "unhealthy"
        rag_status = "healthy" if rag_service.is_ready() else "unhealthy"
        
        overall_status = "healthy" if all([
            nlp_status == "healthy",
            ocr_status == "healthy", 
            classification_status == "healthy",
            rag_status == "healthy"
        ]) else "unhealthy"
        
        return HealthStatus(
            status=overall_status,
            nlp_service=nlp_status,
            ocr_service=ocr_status,
            classification_service=classification_status,
            rag_service=rag_status,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/process/document", response_model=ProcessDocumentResponse)
async def process_document(request: ProcessDocumentRequest):
    """Process a document with AI services"""
    try:
        logger.info(f"Processing document ID: {request.document_id}")
        
        # Get document from main API
        async with httpx.AsyncClient() as client:
            doc_response = await client.get(
                f"{os.getenv('API_SERVICE_URL', 'http://localhost:8000')}/documents/{request.document_id}"
            )
            
            if doc_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Document not found")
            
            document = doc_response.json()
        
        # Download document content
        async with httpx.AsyncClient() as client:
            file_response = await client.get(document["file_url"])
            if file_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Document file not found")
            
            file_content = file_response.content
        
        # Extract text using OCR
        extracted_text = await ocr_service.extract_text(
            file_content,
            document["content_type"],
            document["filename"]
        )
        
        # Perform NLP analysis
        nlp_analysis = await nlp_service.analyze_text(extracted_text)
        
        # Classify document
        classification = await classification_service.classify_document(
            extracted_text,
            document["title"]
        )
        
        # Generate summary
        summary = await nlp_service.generate_summary(extracted_text)
        
        # Update document in main API
        update_data = {
            "extracted_text": extracted_text,
            "summary": summary,
            "entities": nlp_analysis.entities,
            "classification": classification.category,
            "classification_confidence": classification.confidence,
            "status": "processed",
            "processed_at": datetime.utcnow().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            update_response = await client.put(
                f"{os.getenv('API_SERVICE_URL', 'http://localhost:8000')}/documents/{request.document_id}",
                json=update_data
            )
        
        # Index in Weaviate for semantic search
        await rag_service.index_document(
            document_id=request.document_id,
            title=document["title"],
            content=extracted_text,
            summary=summary,
            category=classification.category,
            tags=document.get("tags", [])
        )
        
        return ProcessDocumentResponse(
            document_id=request.document_id,
            status="completed",
            extracted_text=extracted_text,
            summary=summary,
            entities=nlp_analysis.entities,
            classification=classification,
            processing_time=0,  # Calculate actual time
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        
        # Update document status to error
        try:
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{os.getenv('API_SERVICE_URL', 'http://localhost:8000')}/documents/{request.document_id}",
                    json={
                        "status": "error",
                        "processing_error": str(e)
                    }
                )
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.post("/rag/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with documents using RAG"""
    try:
        response = await rag_service.chat(
            query=request.query,
            document_id=request.document_id,
            context_limit=request.context_limit
        )
        
        return response
        
    except Exception as e:
        logger.error(f"RAG chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/analyze/text", response_model=DocumentAnalysis)
async def analyze_text(text: str = Form(...)):
    """Analyze text content"""
    try:
        # Perform NLP analysis
        nlp_analysis = await nlp_service.analyze_text(text)
        
        # Classify text
        classification = await classification_service.classify_document(text, "")
        
        # Generate summary
        summary = await nlp_service.generate_summary(text)
        
        return DocumentAnalysis(
            extracted_text=text,
            summary=summary,
            entities=nlp_analysis.entities,
            classification=classification,
            language=nlp_analysis.language,
            sentiment=nlp_analysis.sentiment,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)