from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
import enum
from uuid import uuid4

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class RoleEnum(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    thread_id = Column(String, ForeignKey("chat_threads.id", ondelete="CASCADE"))
    role = Column(Enum(RoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    thread = relationship("ChatThread", back_populates="messages")
