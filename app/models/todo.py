from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from app.models.user import User


class TodoBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: int = Field(foreign_key="user.id")


class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: User = Relationship()