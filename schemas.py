from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=200)


class TodoCreate(TodoBase):
    pass


class TodoOut(TodoBase):
    id: int = Field(ge=1)
    is_completed: bool = Field(default=False)


class TodoUpdate(TodoBase):
    is_completed: bool = Field(default=False)
