from database import get_db
from models import User
import security
import jwt

from fastapi.params import Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from enums import Roles


oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="/users/login", tokenUrl="/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati tugagan"
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await db.scalar(select(User).where(User.id == int(user_id)))
    if user is None:
        raise credentials_exception

    return user


async def role_checker(*allowed_roles: Roles):
    async def checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat etilmagan")
        return user

    return checker
