from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all(self, offset: int = 0, limit: int = 100) -> list[Todo]:
        statement = select(Todo).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def get_by_id(self, todo_id: int) -> Todo:
        todo = self.session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        return todo

    def create(self, data: TodoCreate) -> Todo:
        todo = Todo.model_validate(data)
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def update(self, todo_id: int, data: TodoUpdate) -> Todo:
        todo = self.get_by_id(todo_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        for key, value in update_data.items():
            setattr(todo, key, value)

        # If completed is explicitly set to True, mark status as completed
        if update_data.get("completed") is True:
            todo.status = "completed"
        # If status set to completed, mark completed flag
        if update_data.get("status") == "completed":
            todo.completed = True

        todo.updated_at = datetime.utcnow()
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> None:
        todo = self.get_by_id(todo_id)
        self.session.delete(todo)
        self.session.commit()
