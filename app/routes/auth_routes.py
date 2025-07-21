from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.controllers.auth_controller import AuthController
from app.schemas.user import UserRegister, UserLogin, Token, RefreshTokenRequest, UserResponse
from app.middleware.auth_middleware import get_current_active_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: User email address (must be unique)
    - **password**: User password (will be hashed)
    
    Returns access and refresh tokens.
    """
    controller = AuthController(db)
    return await controller.register(user_data)

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    - **email**: User email address
    - **password**: User password
    
    Returns access and refresh tokens.
    """
    controller = AuthController(db)
    return await controller.login(user_data)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens.
    """
    controller = AuthController(db)
    return await controller.refresh_token(refresh_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile.
    
    Requires valid access token in Authorization header:
    Authorization: Bearer <access_token>
    """
    controller = AuthController(db=None)  # No DB needed for this endpoint
    return await controller.get_current_user_profile(current_user)

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user by invalidating refresh token.
    
    Requires valid access token in Authorization header:
    Authorization: Bearer <access_token>
    """
    controller = AuthController(db)
    return await controller.logout(current_user) 