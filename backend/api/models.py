from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    keycloak_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    color = Column(String, default="#3B82F6")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="category")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    filename = Column(String)
    file_path = Column(String, unique=True)  # MinIO object name
    file_url = Column(String)
    file_size = Column(Integer)
    content_type = Column(String)
    
    # Content analysis
    extracted_text = Column(Text)
    summary = Column(Text)
    entities = Column(JSON)  # Named entities
    classification = Column(String)
    classification_confidence = Column(Float)
    
    # Metadata
    tags = Column(JSON)  # List of tags
    metadata = Column(JSON)  # Additional metadata
    
    # Relationships
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="documents")
    
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploader = relationship("User", back_populates="documents")
    
    # Status and processing
    status = Column(String, default="uploaded")  # uploaded, processing, processed, error
    processing_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Workflow
    approval_status = Column(String, default="pending")  # pending, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Search and indexing
    vector_id = Column(String, unique=True)  # Weaviate object ID
    indexed_at = Column(DateTime)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, index=True)  # UPLOAD, ACCESS, DELETE, SEARCH, etc.
    resource_type = Column(String, index=True)  # document, user, category, etc.
    resource_id = Column(Integer)
    details = Column(JSON)  # Additional action details
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_type = Column(String, index=True)  # approval, notification, expiration
    document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String, default="active")  # active, completed, failed, cancelled
    
    # n8n integration
    n8n_execution_id = Column(String)
    
    # Workflow data
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    document = relationship("Document")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String, index=True)  # email, slack, teams, in_app
    status = Column(String, default="pending")  # pending, sent, failed
    
    # External IDs
    external_id = Column(String)  # Email message ID, Slack timestamp, etc.
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")