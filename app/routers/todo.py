from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import *
from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoUpdate
from typing import Annotated
from fastapi import status, Form
from . import templates
import logging

logger = logging.getLogger(__name__)

todo_router = APIRouter()


@todo_router.get("/todos", response_class=HTMLResponse)
async def todos_page(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    repo = TodoRepository(db)
    todos, pagination = repo.get_user_todos(user.id, page, limit)

    return templates.TemplateResponse(
        request=request,
        name="todos.html",
        context={
            "user": user,
            "todos": todos,
            "pagination": pagination
        }
    )


@todo_router.post("/todos", response_class=RedirectResponse)
async def create_todo(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    title: str = Form(...),
    description: str = Form("")
):
    repo = TodoRepository(db)
    todo_data = TodoCreate(
        title=title,
        description=description if description else None,
        user_id=user.id
    )
    repo.create(todo_data)
    return RedirectResponse("/todos", status_code=303)


@todo_router.post("/todos/{todo_id}/toggle", response_class=RedirectResponse)
async def toggle_todo(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    todo_id: int
):
    repo = TodoRepository(db)
    todo = db.get(Todo, todo_id)
    if not todo or todo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Todo not found")

    update_data = TodoUpdate(completed=not todo.completed)
    repo.update_todo(todo_id, update_data)
    return RedirectResponse("/todos", status_code=303)


@todo_router.post("/todos/{todo_id}/delete", response_class=RedirectResponse)
async def delete_todo(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    todo_id: int
):
    repo = TodoRepository(db)
    todo = db.get(Todo, todo_id)
    if not todo or todo.user_id != user.id:
        raise HTTPException(status_code=404, detail="Todo not found")

    repo.delete_todo(todo_id)
    return RedirectResponse("/todos", status_code=303)