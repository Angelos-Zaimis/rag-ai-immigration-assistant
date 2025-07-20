from pydantic import BaseModel
from uuid import UUID

class ChatSchema(BaseModel):
    id: UUID

    class Config:
        orm_mode = True
