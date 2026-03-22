from app.models.todo import TodoBase
from sqlmodel import SQLModel
from typing import Optional


class TodoCreate(TodoBase):
    pass


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(SQLModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    user_id: int