from pydantic import BaseModel, Field


class UserBase(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: str | None = Field(default='user', max_length=50)


class UserCreate(UserBase):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(UserBase):
    id: int
    username: str
    user_avatar: str | None = None
