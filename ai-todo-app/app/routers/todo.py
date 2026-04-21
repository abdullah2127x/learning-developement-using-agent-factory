from fastapi import APIRouter, Query, status

from app.database.session import SessionDep
from app.schemas.todo import TodoCreate, TodoListResponse, TodoResponse, TodoUpdate
from app.services.todo import TodoService

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=TodoListResponse)
def list_todos(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    service = TodoService(session)
    todos = service.get_all(offset=offset, limit=limit)
    return TodoListResponse(todos=todos, count=len(todos))


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, session: SessionDep):
    service = TodoService(session)
    return service.get_by_id(todo_id)


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, session: SessionDep):
    service = TodoService(session)
    return service.create(data)


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, data: TodoUpdate, session: SessionDep):
    service = TodoService(session)
    return service.update(todo_id, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, session: SessionDep):
    service = TodoService(session)
    service.delete(todo_id)
