from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import AuditLog, User
from schemas import AuditLogCreate, AuditSummary
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AuditService:
    async def create_log(self, db: Session, audit_data: AuditLogCreate) -> AuditLog:
        """Create an audit log entry"""
        try:
            audit_log = AuditLog(
                user_id=audit_data.user_id,
                action=audit_data.action,
                resource_type=audit_data.resource_type,
                resource_id=audit_data.resource_id,
                details=audit_data.details or {},
                ip_address=audit_data.ip_address,
                user_agent=audit_data.user_agent,
                timestamp=datetime.utcnow()
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            logger.info(f"Created audit log: {audit_log.id}")
            return audit_log
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            db.rollback()
            raise
    
    async def get_logs(
        self,
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with filters"""
        try:
            query = db.query(AuditLog)
            
            # Apply filters
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if action:
                query = query.filter(AuditLog.action == action)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            # Apply ordering and pagination
            logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise
    
    async def get_summary(self, db: Session, days: int = 7) -> AuditSummary:
        """Get audit summary for the specified number of days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total actions
            total_actions = db.query(func.count(AuditLog.id)).filter(
                AuditLog.timestamp >= start_date
            ).scalar()
            
            # Actions by type
            action_stats = db.query(
                AuditLog.action,
                func.count(AuditLog.id).label('count')
            ).filter(
                AuditLog.timestamp >= start_date
            ).group_by(AuditLog.action).all()
            
            actions_by_type = {stat.action: stat.count for stat in action_stats}
            
            # Actions by user
            user_stats = db.query(
                User.username,
                func.count(AuditLog.id).label('count')
            ).join(AuditLog).filter(
                AuditLog.timestamp >= start_date
            ).group_by(User.username).all()
            
            actions_by_user = {stat.username: stat.count for stat in user_stats}
            
            # Actions by resource type
            resource_stats = db.query(
                AuditLog.resource_type,
                func.count(AuditLog.id).label('count')
            ).filter(
                AuditLog.timestamp >= start_date
            ).group_by(AuditLog.resource_type).all()
            
            actions_by_resource = {stat.resource_type: stat.count for stat in resource_stats}
            
            # Timeline (actions per day)
            timeline = []
            for i in range(days):
                day_start = start_date + timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                day_count = db.query(func.count(AuditLog.id)).filter(
                    and_(
                        AuditLog.timestamp >= day_start,
                        AuditLog.timestamp < day_end
                    )
                ).scalar()
                
                timeline.append({
                    "date": day_start.date().isoformat(),
                    "count": day_count
                })
            
            # Top users
            top_users = [
                {
                    "username": stat.username,
                    "count": stat.count
                }
                for stat in sorted(user_stats, key=lambda x: x.count, reverse=True)[:10]
            ]
            
            return AuditSummary(
                total_actions=total_actions,
                actions_by_type=actions_by_type,
                actions_by_user=actions_by_user,
                actions_by_resource=actions_by_resource,
                timeline=timeline,
                top_users=top_users
            )
            
        except Exception as e:
            logger.error(f"Error getting audit summary: {e}")
            raise