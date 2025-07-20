from uuid import UUID
from pydantic import BaseModel

class ChatBase(BaseModel):
    content: str
    pass

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: UUID

    class Config:
        from_attributes = True 