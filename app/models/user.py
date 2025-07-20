from datetime import datetime
from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False) 