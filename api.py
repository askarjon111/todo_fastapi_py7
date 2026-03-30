from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from schemas import TodoCreate, TodoOut, TodoUpdate
from database import Base, get_db, engine
from models import Todo



Base.metadata.create_all(bind=engine)
api_router = APIRouter(prefix='/api/todo')


@api_router.post('/', response_model=TodoOut)
def create_todo(todo_in: TodoCreate, db = Depends(get_db)):
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
