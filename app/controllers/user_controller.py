from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate
from app.services.user.user_service import UserService

class UserController:
    def __init__(self, db: AsyncSession):
        self.service = UserService(db)

    async def create_user(self, user_in: UserCreate):
        return await self.service.create_user(user_in)

    async def get_user(self, user_id: int):
        return await self.service.get_user_by_id(user_id)

    async def get_users(self, skip: int = 0, limit: int = 100):
        return await self.service.list_users(skip, limit)

    async def update_user(self, user_id: int, user_in: UserUpdate):
        return await self.service.update_user(user_id, user_in)

    async def delete_user(self, user_id: int):
        return await self.service.delete_user(user_id)
