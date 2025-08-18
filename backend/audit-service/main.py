from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import os

from database import get_db
from models import AuditLog, User
from schemas import AuditLogCreate, AuditLogResponse, AuditSummary
from services.audit_service import AuditService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SGD Audit Service",
    description="Audit and logging service for SGD system",
    version="1.0.0"
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
audit_service = AuditService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/audit/log", response_model=AuditLogResponse)
async def create_audit_log(
    audit_log: AuditLogCreate,
    db: Session = Depends(get_db)
):
    """Create an audit log entry"""
    try:
        log_entry = await audit_service.create_log(db, audit_log)
        return AuditLogResponse.from_orm(log_entry)
    except Exception as e:
        logger.error(f"Error creating audit log: {e}")
        raise HTTPException(status_code=500, detail="Failed to create audit log")

@app.get("/audit/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get audit logs with filters"""
    try:
        logs = await audit_service.get_logs(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        return [AuditLogResponse.from_orm(log) for log in logs]
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audit logs")

@app.get("/audit/summary", response_model=AuditSummary)
async def get_audit_summary(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get audit summary for the specified number of days"""
    try:
        summary = await audit_service.get_summary(db, days)
        return summary
    except Exception as e:
        logger.error(f"Error getting audit summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audit summary")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)