from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from keycloak import KeycloakOpenID
import os
import jwt
from models import User
from database import get_db

security = HTTPBearer()

# Keycloak configuration
keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_URL", "http://localhost:8090"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID", "sgd-client"),
    realm_name=os.getenv("KEYCLOAK_REALM", "sgd-realm"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET")
)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Keycloak"""
    try:
        # Get public key from Keycloak
        public_key = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        
        # Decode and verify token
        payload = jwt.decode(
            credentials.credentials,
            public_key,
            algorithms=["RS256"],
            audience="account",
            options={"verify_exp": True}
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

async def get_current_user(
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get current user from token"""
    try:
        keycloak_id = token_payload.get("sub")
        if not keycloak_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Get or create user
        user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
        if not user:
            # Create new user from token
            user = User(
                keycloak_id=keycloak_id,
                username=token_payload.get("preferred_username"),
                email=token_payload.get("email"),
                first_name=token_payload.get("given_name"),
                last_name=token_payload.get("family_name"),
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
        raise HTTPException(status_code=500, detail=f"User retrieval failed: {str(e)}")