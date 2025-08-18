from sqlalchemy.orm import Session
from models import AuditLog
from database import SessionLocal
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditService:
    async def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit action"""
        try:
            db = SessionLocal()
            
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            
            db.add(audit_log)
            db.commit()
            
            logger.info(f"Logged audit action: {action} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error logging audit action: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
    
    async def get_audit_logs(
        self,
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """Get audit logs with filters"""
        try:
            query = db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise