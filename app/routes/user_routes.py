from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.controllers.user_controller import UserController
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.create_user(user_in)

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.get_user(user_id)

@router.get("/", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.get_users(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.update_user(user_id, user_in)

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.delete_user(user_id) 