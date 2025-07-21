from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from app.services.auth.jwt_service import JWTService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.jwt_service = JWTService()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user_uuid = uuid.UUID(user_id)
            result = await self.db.execute(select(User).where(User.id == user_uuid))
            return result.scalar_one_or_none()
        except ValueError:
            return None

    async def register_user(self, user_data: UserRegister) -> Token:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = self.jwt_service.get_password_hash(user_data.password)

        # Create user
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True
        )

        # Create refresh token
        token_data = self.jwt_service.create_token_pair(str(user.id))
        user.refresh_token = token_data["refresh_token"]

        # Save to database
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return Token(**token_data)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not self.jwt_service.verify_password(password, user.hashed_password):
            return None
        return user

    async def login_user(self, user_data: UserLogin) -> Token:
        """Login user and return tokens."""
        user = await self.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create token pair
        token_data = self.jwt_service.create_token_pair(str(user.id))
        
        # Update refresh token in database
        user.refresh_token = token_data["refresh_token"]
        await self.db.commit()
        await self.db.refresh(user)

        return Token(**token_data)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        # Verify refresh token
        payload = self.jwt_service.verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user and verify refresh token matches stored one
        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.refresh_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new token pair
        token_data = self.jwt_service.create_token_pair(user_id)
        
        # Update refresh token in database
        user.refresh_token = token_data["refresh_token"]
        await self.db.commit()

        return Token(**token_data)

    async def get_current_user(self, token: str) -> User:
        """Get current user from access token."""
        payload = self.jwt_service.verify_token(token, "access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    async def logout_user(self, user: User) -> None:
        """Logout user by invalidating refresh token."""
        user.refresh_token = None
        await self.db.commit() 