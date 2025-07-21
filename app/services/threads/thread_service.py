from typing import Any

from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.chat import ChatThread


class ThreadService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_thread(self, thread_id: str) -> Row[Any] | RowMapping | ChatThread:
        result = await self.db.execute(
            select(ChatThread).where(ChatThread.id == thread_id)
        )

        thread = result.scalars().first()

        if thread:
            return thread

        thread = ChatThread(id=thread_id, user_id="anonymous")
        self.db.add(thread)
        await self.db.flush()
        return thread
