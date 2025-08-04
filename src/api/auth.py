from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.api.jwt_utils import decode_access_token
import os
from typing import Optional, List
import bcrypt

# Example: user API keys (in production, fetch from DB or secure store)
USER_API_KEYS = {
    # 'user_email': 'user_api_key',
    'as4195@gmail.com': os.getenv('AS4195_API_KEY'),
    # Add more users as needed
}

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
bearer_scheme = HTTPBearer()

# Optionally restrict endpoints
RESTRICTED_ENDPOINTS: List[str] = [
    '/user/query-openai',
    '/user/query-gpt',
]

def get_current_user_api_key(
    api_key_header: str = Security(api_key_header),
    email: Optional[str] = None
):
    if not api_key_header:
        raise HTTPException(status_code=403, detail="API key missing")
    # If email is provided, check per-user key
    if email:
        expected_key = USER_API_KEYS.get(email)
        if expected_key and api_key_header == expected_key:
            return email
        raise HTTPException(status_code=403, detail="Invalid API key for user")
    # Otherwise, check if key is valid for any user
    if api_key_header in USER_API_KEYS.values():
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API key")

# Dependency for restricted endpoints

def restricted_api_key(
    api_key_header: str = Security(api_key_header),
    email: Optional[str] = None
):
    return get_current_user_api_key(api_key_header, email)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]  # email

# Password hashing utilities

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode()) 