# routers/chat_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.controllers.chat_controller import ChatController
from app.schemas.chat import ChatCreate

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def create_new_chat(
    thread_id: str, query: str,
    db: AsyncSession = Depends(get_db)
):
    controller = ChatController(db)
    return await controller.handle_create_chat(thread_id, query)
