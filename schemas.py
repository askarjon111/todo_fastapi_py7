from pydantic import BaseModel, Field



class UserBase(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int


class TodoBase(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=200)
    user_id: int


class TodoCreate(TodoBase):
    pass


class TodoOut(TodoBase):
    id: int = Field(ge=1)
    is_completed: bool = Field(default=False)


class TodoUpdate(TodoBase):
    is_completed: bool = Field(default=False)
