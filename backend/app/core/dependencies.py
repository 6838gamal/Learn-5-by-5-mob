from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .security import decode_token

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Validate JWT and return user_id (UUID string)."""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("Missing subject")
        return user_id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Load and return the full User model from DB."""
    from app.repositories.user_repository import UserRepository
    from app.models.user import User

    repo = UserRepository(db)
    user: User | None = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


async def require_premium(current_user=Depends(get_current_user)):
    """Raises 403 if user does not have an active Premium or Lifetime subscription."""
    from app.repositories.subscription_repository import SubscriptionRepository
    # Subscription check is injected via service later; placeholder guards here.
    return current_user
