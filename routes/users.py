import security
import shutil

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from models import User
from database import get_db
from schemas.users import Token, UserCreate, UserOut
from email_service import send_welcome_email
from dependencies import get_current_user

users_router = APIRouter(prefix='/api/users')


@users_router.post('/', response_model=UserOut)
async def create_user(bg_tasks: BackgroundTasks, user_in: UserCreate, db: Session = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == user_in.username))
    if user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud")

    user_dict = user_in.model_dump()
    hashed_password = security.get_password_hash(user_dict.pop("password"))

    user = User(**user_dict, hashed_password=hashed_password)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    bg_tasks.add_task(send_welcome_email, f"{user.username}@gmail.com")

    return user


@users_router.post('/upload_avatar/')
async def upload_avatar(file: UploadFile = File(...),
                        current_user: UserOut = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    from config import UPLOAD_FOLDER

    file_extension = file.filename.split(".")[-1]
    file_location = f"{UPLOAD_FOLDER}/{current_user.id}_avatar.{file_extension}"
    static_location = f"/static/{current_user.id}_avatar.{file_extension}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.user_avatar = static_location
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@users_router.post('/login/', response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get('/me/', response_model=UserOut)
async def get_current_user_profile(current_user: UserOut = Depends(get_current_user)):
    return current_user
