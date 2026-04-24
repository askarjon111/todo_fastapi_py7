import asyncio

from email_service import send_welcome_email
import security
import jwt

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import Depends, HTTPException, status, APIRouter, BackgroundTasks
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm

from models import Todo, User
from database import get_db
from schemas import TodoCreate, TodoOut, TodoUpdate, Token, Token, UserCreate, UserOut


api_router = APIRouter(prefix='/api')


oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="/users/login", tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati tugagan"
    )
    try:
        payload = await jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await db.scalar(select(User).where(User.id == int(user_id)))
    if user is None:
        raise credentials_exception

    return user


@api_router.post('/users', response_model=UserOut)
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

    # Add background task to send welcome email
    bg_tasks.add_task(send_welcome_email, f"{user.username}@gmail.com")

    return user


@api_router.post('/users/login', response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not await security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.get('/users/me', response_model=UserOut)
async def get_current_user_profile(current_user: UserOut = Depends(get_current_user)):
    return current_user


@api_router.post('/todo/', response_model=TodoOut)
async def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db), user: UserOut = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=400, detail=f"{todo_in['user_id']} idli user mavjud emas")

    todo = Todo(**todo_in.model_dump(), user_id=user.id)

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@api_router.get('/todo/')
async def get_todos(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)):
    stmt = select(Todo).limit(limit).offset(offset)
    todos = db.scalars(stmt).all()
    todo_count = db.scalar(select(func.count()).select_from(Todo))

    data = {
        "total": todo_count,
        "items": todos,
        "limit": limit,
        "offset": offset
    }

    return data



@api_router.get('/todo/{task_id}', response_model=TodoOut)
async def get_todo(task_id: int, db = Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    return todo


@api_router.put('/todo/{task_id}', response_model=TodoOut)
async def update_todo(task_id: int, todo_in: TodoUpdate, db = Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo: TodoOut = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    todo.name = todo_in.name
    todo.description = todo_in.description
    todo.is_completed = todo_in.is_completed

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@api_router.delete('/todo/{task_id}')
async def delete_todo(task_id: int, db = Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    db.delete(todo)
    db.commit()

    return {"status": 204}