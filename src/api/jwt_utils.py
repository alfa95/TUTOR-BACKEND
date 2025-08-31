import jwt
from datetime import datetime, timedelta
import os
from typing import Optional, Dict
from fastapi import HTTPException, status

ALGORITHM = "HS256"

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

    """
    Decode and verify Supabase JWT token
    """
    try:
        jwt_secret = os.getenv('SUPABASE_JWT_SECRET')
        if not jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET not found in environment variables")
        
        # Decode JWT without verification first to get algorithm
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        algorithm = unverified_payload.get('alg', 'HS256')
        
        payload = jwt.decode(
            token, 
            jwt_secret, 
            algorithms=[algorithm],
            options={"verify_signature": True}
        )
        
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
    Only extracts user_id - the only field we actually need
    """
    try:
        # Decode JWT without verification (since we're using anon key approach)
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Extract only user_id - that's all we need!
        user_info = {
            "user_id": payload.get("sub")  # User ID from JWT
        }
        
        return user_info
        
    except Exception as e:
        # If JWT decode fails, return minimal info
        print(f"Warning: JWT decode failed: {e}")
        return {
            "user_id": None
        } 