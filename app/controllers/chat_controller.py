
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat import ChatCreate
from app.services.chat.chat_service import ChatService

class ChatController:
    def __init__(self, db: AsyncSession):
        self.service = ChatService(db)

    async def handle_create_chat(self, thread_id: str, query: str):
        return await self.service.handle_message(thread_id, query)