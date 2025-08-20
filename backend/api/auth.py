from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
import httpx
import os
from models import User
from database import get_db
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://localhost:3001")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-token-with-at-least-32-characters-long")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Supabase Auth"""
    try:
        # Decode and verify token
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def get_current_user(
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get current user from token"""
    try:
        user_id = token_payload.get("sub")
        email = token_payload.get("email")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Get or create user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create new user from token
            user = User(
                keycloak_id=user_id,  # Using keycloak_id field for Supabase user ID
                username=email.split('@')[0],  # Use email prefix as username
                email=email,
                first_name=token_payload.get("user_metadata", {}).get("first_name"),
                last_name=token_payload.get("user_metadata", {}).get("last_name"),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is disabled")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"User retrieval failed: {str(e)}")

# Optional: Create a simple auth bypass for development
async def get_current_user_dev(db: Session = Depends(get_db)):
    """Development-only: Get or create a default admin user"""
    try:
        # Look for existing admin user
        user = db.query(User).filter(User.email == "admin@sgd.com").first()
        if not user:
            # Create default admin user
            user = User(
                keycloak_id="dev-admin-001",
                username="admin",
                email="admin@sgd.com",
                first_name="Admin",
                last_name="User",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    except Exception as e:
        logger.error(f"Dev user creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")