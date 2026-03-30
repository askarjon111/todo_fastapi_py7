from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean


from database import Base


class Todo(Base):
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100))
    description: Mapped[str] = mapped_column(String(length=200))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
