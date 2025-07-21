from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: UserCreate):
        """Create a new user - Note: For registration use AuthService.register_user instead"""
        user = User(
            id=uuid.uuid4(),
            email=user_in.email,
            hashed_password=user_in.password,  # Should be hashed before calling this
            is_active=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: str):
        """Get user by UUID string"""
        try:
            user_uuid = uuid.UUID(user_id)
            result = await self.db.execute(select(User).where(User.id == user_uuid))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

    async def get_user_by_email(self, email: str):
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def list_users(self, skip: int, limit: int):
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_user(self, user_id: str, user_in: UserUpdate):
        """Update user by UUID string"""
        try:
            user_uuid = uuid.UUID(user_id)
            result = await self.db.execute(select(User).where(User.id == user_uuid))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            for field, value in user_in.dict(exclude_unset=True).items():
                setattr(user, field, value)

            await self.db.commit()
            await self.db.refresh(user)
            return user
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

    async def delete_user(self, user_id: str):
        """Delete user by UUID string"""
        try:
            user_uuid = uuid.UUID(user_id)
            result = await self.db.execute(select(User).where(User.id == user_uuid))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            await self.db.delete(user)
            await self.db.commit()
            return user
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")
