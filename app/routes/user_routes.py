from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.controllers.user_controller import UserController
from app.schemas.user import User, UserUpdate
from app.middleware.auth_middleware import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get user by ID. 
    
    Requires authentication. Users can only access their own profile or admin access.
    """
    controller = UserController(db)
    return await controller.get_user(user_id)

@router.get("/", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    List users. 
    
    Requires authentication. This should typically be restricted to admin users.
    """
    controller = UserController(db)
    return await controller.get_users(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Update user.
    
    Requires authentication. Users can only update their own profile or admin access.
    """
    controller = UserController(db)
    return await controller.update_user(user_id, user_in)

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Delete user.
    
    Requires authentication. Users can only delete their own profile or admin access.
    """
    controller = UserController(db)
    return await controller.delete_user(user_id) 