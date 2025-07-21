from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserUpdate
from app.services.users.user_service import UserService

class UserController:
    def __init__(self, db: AsyncSession):
        self.service = UserService(db)

    async def get_user(self, user_id: str):
        """Get user by UUID string"""
        return await self.service.get_user_by_id(user_id)

    async def get_user_by_email(self, email: str):
        """Get user by email"""
        return await self.service.get_user_by_email(email)

    async def get_users(self, skip: int = 0, limit: int = 100):
        """List users - should be protected for admin use only"""
        return await self.service.list_users(skip, limit)

    async def update_user(self, user_id: str, user_in: UserUpdate):
        """Update user by UUID string"""
        return await self.service.update_user(user_id, user_in)

    async def delete_user(self, user_id: str):
        """Delete user by UUID string"""
        return await self.service.delete_user(user_id)
