from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas import TodoCreate, TodoOut, TodoUpdate, UserCreate, UserOut
from database import Base, get_db, engine
from models import Todo, User



Base.metadata.create_all(bind=engine)
api_router = APIRouter(prefix='/api/todo')


@api_router.post('/users', response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(**user_in.model_dump())

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


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