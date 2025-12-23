from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.apps.auth.models import RefreshToken
from src.app.apps.auth.repository import RefreshTokenRepository, UserRepository
from src.app.apps.auth.schemas import TokenResponse, UserCreate, UserLogin, UserRead
from src.app.core.deps import CurrentUser, get_current_user
from src.app.core.security import Security
from src.app.db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            detail="Email already registered", status_code=status.HTTP_409_CONFLICT
        )
    user = await repo.create(email=payload.email, password=payload.password)
    return UserRead(id=user.id, email=user.email, role=user.role, is_active=True)


@router.post("/token", response_model=TokenResponse)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_session)):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(payload.email)
    if not user or not Security.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            detail="Invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED
        )
    access_token = Security.create_access_token(str(user.id), extra={"role": user.role})
    refresh_token = Security.create_refresh_token(str(user.id))
    rt_repo = RefreshTokenRepository(session)
    rt = await rt_repo.create(user.id, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = Security.decode_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    user_id = payload.get("sub")
    role = payload.get("role", "user")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    rt_repo = RefreshTokenRepository(session)
    existing = await rt_repo.get_by_token(refresh_token)
    if not existing or existing.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or unknown",
        )
    await rt_repo.revoke(existing.id)
    new_access = Security.create_access_token(str(user_id), extra={"role": role})
    new_refresh = Security.create_refresh_token(str(user_id))
    await rt_repo.create(int(user_id), new_refresh)
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    rt_repo = RefreshTokenRepository(session)
    record = await rt_repo.get_by_token(refresh_token)
    if record:
        await rt_repo.revoke(record.id)
    return None


@router.get("/me", response_model=UserRead)
async def me(
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = UserRepository(session)
    user = await repo.get_by_id(current_user.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserRead(
        id=user.id, email=user.email, role=user.role, is_active=user.is_active
    )
