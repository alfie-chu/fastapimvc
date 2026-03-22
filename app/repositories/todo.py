from sqlalchemy.orm import Session
from sqlmodel import select, func
from app.models.todo import Todo, TodoBase
from typing import Optional, List
from app.utilities.pagination import Pagination
from app.schemas.todo import TodoUpdate
import logging

logger = logging.getLogger(__name__)


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_todos(self, user_id: int, page: int = 1, limit: int = 10) -> (List[Todo], Pagination):
        offset = (page - 1) * limit

        db_qry = select(Todo).where(Todo.user_id == user_id)
        count_qry = select(func.count()).select_from(db_qry.subquery())
        count_todos = self.db.exec(count_qry).one()

        todos = self.db.exec(db_qry.offset(offset).limit(limit)).all()
        pagination = Pagination(total_count=count_todos, current_page=page, limit=limit)

        return todos, pagination

    def create(self, todo_data: TodoBase) -> Optional[Todo]:
        try:
            todo_db = Todo.model_validate(todo_data)
            self.db.add(todo_db)
            self.db.commit()
            self.db.refresh(todo_db)
            return todo_db
        except Exception as e:
            logger.error(f"An error occurred while saving todo: {e}")
            raise

    def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Todo:
        todo = self.db.get(Todo, todo_id)
        if not todo:
            raise Exception("Invalid todo id given")
        if todo_data.title is not None:
            todo.title = todo_data.title
        if todo_data.description is not None:
            todo.description = todo_data.description
        if todo_data.completed is not None:
            todo.completed = todo_data.completed

        try:
            self.db.add(todo)
            self.db.commit()
            self.db.refresh(todo)
            return todo
        except Exception as e:
            logger.error(f"An error occurred while updating todo: {e}")
            raise

    def delete_todo(self, todo_id: int):
        todo = self.db.get(Todo, todo_id)
        if not todo:
            raise Exception("Todo doesn't exist")
        try:
            self.db.delete(todo)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"An error occurred while deleting todo: {e}")
            raise