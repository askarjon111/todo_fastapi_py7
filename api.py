import security
import jwt

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models import Todo, User
from database import Base, get_db, engine
from schemas import TodoCreate, TodoOut, TodoUpdate, Token, Token, UserCreate, UserOut


Base.metadata.create_all(bind=engine)
api_router = APIRouter(prefix='/api/todo')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

    user = db.scalar(select(User).where(User.id == int(user_id)))
    if user is None:
        raise credentials_exception

    return user


@api_router.post('/users', response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.first_name == user_in.first_name, User.last_name == user_in.last_name))
    if user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud")

    user_dict = user_in.model_dump()
    hashed_password = security.get_password_hash(user_dict.pop("password"))
    
    user = User(**user_dict, hashed_password=hashed_password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@api_router.post('/users/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.post('/', response_model=TodoOut)
def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db)):
    stmt = select(User).where(User.id == todo_in.user_id)
    user = db.scalar(stmt)

    if not user:
        raise HTTPException(status_code=400, detail=f"{todo_in['user_id']} idli user mavjud emas")

    todo = Todo(**todo_in.model_dump())

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@api_router.get('/', response_model=List[TodoOut])
def get_todos(db = Depends(get_db)):
    stmt = select(Todo)
    todos = db.scalars(stmt).all()

    return todos



@api_router.get('/{task_id}', response_model=TodoOut)
def get_todo(task_id: int, db = Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    return todo


@api_router.put('/{task_id}', response_model=TodoOut)
def update_todo(task_id: int, todo_in: TodoUpdate, db = Depends(get_db)):
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


@api_router.delete('/{task_id}')
def get_todo(task_id: int, db = Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    db.delete(todo)
    db.commit()

    return {"status": 204}