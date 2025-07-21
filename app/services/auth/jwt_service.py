from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from app.config.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    PWD_CONTEXT_SCHEMES,
    PWD_CONTEXT_DEPRECATED
)

class JWTService:
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=PWD_CONTEXT_SCHEMES,
            deprecated=PWD_CONTEXT_DEPRECATED
        )
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password for storing in the database."""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
        # Add unique JTI (JWT ID) for refresh token invalidation
        to_encode.update({
            "exp": expire, 
            "type": "refresh",
            "jti": str(uuid.uuid4())
        })
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check if token type matches expected
            if payload.get("type") != token_type:
                return None
                
            # Check expiration
            exp = payload.get("exp")
            if exp is None:
                return None
                
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
                
            return payload
            
        except JWTError:
            return None
    
    def get_user_id_from_token(self, token: str, token_type: str = "access") -> Optional[str]:
        """Extract user ID from a valid token."""
        payload = self.verify_token(token, token_type)
        if payload:
            return payload.get("sub")
        return None
    
    def create_token_pair(self, user_id: str) -> Dict[str, Any]:
        """Create both access and refresh tokens for a user."""
        access_token = self.create_access_token(data={"sub": user_id})
        refresh_token = self.create_refresh_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
        } 