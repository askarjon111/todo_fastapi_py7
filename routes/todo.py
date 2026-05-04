from dependencies import get_current_user
from email_service import send_telegram_message


from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks

from models import Todo
from database import get_db
from schemas.todo import TodoCreate, TodoOut, TodoUpdate
from schemas.users import UserOut

todo_router = APIRouter(prefix='/api/todo')


@todo_router.post('/send_telegram_message')
async def send_telegram_message_endpoint(chat_id: str, message: str, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(send_telegram_message, chat_id, message)
    return {"status": "Message sent"}


@todo_router.post('/', response_model=TodoOut)
async def create_todo(todo_in: TodoCreate, db: Session = Depends(get_db), user: UserOut = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=400, detail=f"{todo_in['user_id']} idli user mavjud emas")

    todo = Todo(**todo_in.model_dump(), user_id=user.id)

    db.add(todo)
    await db.commit()
    await db.refresh(todo)

    return todo


@todo_router.get('/')
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


@todo_router.get('/{task_id}', response_model=TodoOut)
async def get_todo(task_id: int, db=Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    return todo


@todo_router.put('/{task_id}', response_model=TodoOut)
async def update_todo(task_id: int, todo_in: TodoUpdate, db=Depends(get_db)):
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


@todo_router.delete('/{task_id}')
async def delete_todo(task_id: int, db=Depends(get_db)):
    stmt = select(Todo).where(Todo.id == task_id)
    todo = db.scalar(stmt)

    if not todo:
        raise HTTPException(status_code=404, detail=f"{task_id}-raqamli todo mavjud emas")

    db.delete(todo)
    db.commit()

    return {"status": 204}
