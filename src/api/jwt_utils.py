import jwt
from datetime import datetime, timedelta
import os
from typing import Optional, Dict
from fastapi import HTTPException, status

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def decode_supabase_jwt(token: str) -> Optional[Dict]:
    """
    Decode and verify Supabase JWT token
    """
    try:
        # Get JWT secret from environment
        jwt_secret = os.getenv('SUPABASE_JWT_SECRET')
        if not jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET not found in environment variables")
        
        # Decode JWT without verification first to get algorithm
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        algorithm = unverified_payload.get('alg', 'HS256')
        
        # Now verify with the correct algorithm
        payload = jwt.decode(
            token, 
            jwt_secret, 
            algorithms=[algorithm],
            options={"verify_signature": True}
        )
        
        # Check if token is expired
        exp = payload.get('exp')
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise jwt.ExpiredSignatureError("Token has expired")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

def get_user_from_jwt(token: str) -> Dict:
    """
    Extract user information from JWT token (without verification)
    """
    try:
        # Decode JWT without verification (since we're using anon key approach)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Extract user information
        user_info = {
            "user_id": payload.get("sub"),  # User ID from JWT
            "email": payload.get("email"),
            "role": payload.get("role"),
            "provider": payload.get("app_metadata", {}).get("provider"),
            "session_id": payload.get("session_id")
        }
        
        return user_info
        
    except Exception as e:
        # If JWT decode fails, return minimal info
        print(f"Warning: JWT decode failed: {e}")
        return {
            "user_id": None,
            "email": None,
            "role": None,
            "provider": None,
            "session_id": None
        }

def verify_user_access(user_id: str, token: str) -> bool:
    """
    Verify that the authenticated user can access the requested user_id
    """
    user_info = get_user_from_jwt(token)
    
    # Check if user is trying to access their own data
    if user_info["user_id"] == user_id:
        return True
    
    # You can add additional logic here for admin access, etc.
    # For now, users can only access their own data
    return False 