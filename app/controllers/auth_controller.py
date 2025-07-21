from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserRegister, UserLogin, Token, RefreshTokenRequest, UserResponse
from app.services.auth.auth_service import AuthService
from app.models.user import User


class AuthController:
    def __init__(self, db: AsyncSession):
        self.service = AuthService(db)

    async def register(self, user_data: UserRegister) -> Token:
        """Register a new user and return tokens."""
        return await self.service.register_user(user_data)

    async def login(self, user_data: UserLogin) -> Token:
        """Login user and return tokens."""
        return await self.service.login_user(user_data)

    async def refresh_token(self, refresh_data: RefreshTokenRequest) -> Token:
        """Refresh access token using refresh token."""
        return await self.service.refresh_access_token(refresh_data.refresh_token)

    async def get_current_user_profile(self, current_user: User) -> UserResponse:
        """Get current user profile."""
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            is_active=current_user.is_active,
            created_at=current_user.created_at
        )

    async def logout(self, current_user: User) -> dict:
        """Logout user by invalidating refresh token."""
        await self.service.logout_user(current_user)
        return {"message": "Successfully logged out"} 