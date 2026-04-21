from datetime import datetime
from typing import Literal

from sqlalchemy import Column, String, Text
from sqlmodel import Field, SQLModel

TodoPriority = Literal["low", "medium", "high"]
TodoStatus = Literal["pending", "in_progress", "completed"]


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(200), nullable=False))
    description: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    priority: str = Field(
        sa_column=Column(String(10), nullable=False, server_default="medium")
    )
    status: str = Field(
        sa_column=Column(String(15), nullable=False, server_default="pending")
    )
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
