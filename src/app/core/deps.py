from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from src.app.apps.auth.models import User
from src.app.core.security import Security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class CurrentUser(BaseModel):
    user_id: int
    role: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    try:
        payload = Security.decode_token(token)
    except Exception as e:
        raise HTTPException(
            detail="Invalid Token", status_code=status.HTTP_401_UNAUTHORIZED
        )
    user_id = payload.get("sub")
    role = payload.get("role", "user")
    if user_id is None:
        raise HTTPException(
            detail="Invalid token payload", status_code=status.HTTP_401_UNAUTHORIZED
        )
    return CurrentUser(user_id=int(user_id), role=role)


async def admin_required(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            detail="Admin access required", status_code=status.HTTP_403_FORBIDDEN
        )
    return user
