from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.todo import TodoPriority, TodoStatus


class TodoCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TodoPriority = "medium"
    status: TodoStatus = "pending"


class TodoUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TodoPriority | None = None
    status: TodoStatus | None = None
    completed: bool | None = None


class TodoResponse(SQLModel):
    id: int
    title: str
    description: str | None
    priority: str
    status: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class TodoListResponse(SQLModel):
    todos: list[TodoResponse]
    count: int
